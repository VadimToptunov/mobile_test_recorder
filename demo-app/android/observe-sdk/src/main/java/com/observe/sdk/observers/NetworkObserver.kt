package com.observe.sdk.observers

import android.util.Log
import com.observe.sdk.core.ObserveConfig
import com.observe.sdk.events.Event
import com.observe.sdk.events.EventBus
import com.observe.sdk.security.SSLKeyCapture
import com.observe.sdk.security.bypassCertificatePinning
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import java.util.UUID

/**
 * Network observer using OkHttp Interceptor
 * 
 * Features:
 * - Intercepts all HTTP requests/responses
 * - Captures request/response metadata
 * - Generates correlation IDs
 * - Tracks timing information
 * - Emits network events to EventBus
 */
class NetworkObserver(
    private val eventBus: EventBus
) : Interceptor {
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var isEnabled = true
    
    fun start() {
        Log.d(TAG, "NetworkObserver started")
        isEnabled = true
    }
    
    fun stop() {
        Log.d(TAG, "NetworkObserver stopped")
        isEnabled = false
    }
    
    override fun intercept(chain: Interceptor.Chain): Response {
        if (!isEnabled) {
            return chain.proceed(chain.request())
        }
        
        val request = chain.request()
        val correlationId = UUID.randomUUID().toString()
        val startTime = System.currentTimeMillis()
        
        // Log request
        scope.launch {
            val requestEvent = Event.NetworkEvent(
                timestamp = startTime,
                sessionId = "",
                correlationId = correlationId,
                method = request.method,
                url = request.url.toString(),
                endpoint = extractEndpoint(request.url.toString()),
                statusCode = null,
                requestBody = extractRequestBody(request),
                responseBody = null,
                duration = 0,
                error = null
            )
            eventBus.publish(requestEvent)
            
            Log.d(TAG, "Request: ${request.method} ${request.url}")
        }
        
        // Execute request
        val response: Response
        var error: String? = null
        
        try {
            response = chain.proceed(request)
        } catch (e: IOException) {
            error = e.message ?: "Network error"
            Log.e(TAG, "Network error: $error", e)
            
            // Emit error event
            scope.launch {
                val errorEvent = Event.NetworkEvent(
                    timestamp = System.currentTimeMillis(),
                    sessionId = "",
                    correlationId = correlationId,
                    method = request.method,
                    url = request.url.toString(),
                    endpoint = extractEndpoint(request.url.toString()),
                    statusCode = null,
                    requestBody = null,
                    responseBody = null,
                    duration = System.currentTimeMillis() - startTime,
                    error = error
                )
                eventBus.publish(errorEvent)
            }
            
            throw e
        }
        
        // Log response
        val endTime = System.currentTimeMillis()
        val duration = endTime - startTime
        
        scope.launch {
            val responseEvent = Event.NetworkEvent(
                timestamp = endTime,
                sessionId = "",
                correlationId = correlationId,
                method = request.method,
                url = request.url.toString(),
                endpoint = extractEndpoint(request.url.toString()),
                statusCode = response.code,
                requestBody = extractRequestBody(request),
                responseBody = extractResponseBody(response),
                duration = duration,
                error = if (response.isSuccessful) null else "HTTP ${response.code}"
            )
            eventBus.publish(responseEvent)
            
            Log.d(TAG, "Response: ${response.code} ${request.url} (${duration}ms)")
        }
        
        return response
    }
    
    /**
     * Extract endpoint from full URL
     * Example: "http://10.0.2.2:8000/api/auth/login" -> "/api/auth/login"
     */
    private fun extractEndpoint(url: String): String {
        return try {
            val uri = java.net.URI(url)
            uri.path
        } catch (e: Exception) {
            url
        }
    }
    
    /**
     * Extract request body (limited size for performance)
     */
    private fun extractRequestBody(request: okhttp3.Request): String? {
        return try {
            val body = request.body ?: return null
            val buffer = okio.Buffer()
            body.writeTo(buffer)
            
            // Limit to 1KB for performance
            val maxSize = 1024L
            val size = minOf(buffer.size, maxSize)
            buffer.readUtf8(size)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to extract request body: ${e.message}")
            null
        }
    }
    
    /**
     * Extract response body (limited size for performance)
     */
    private fun extractResponseBody(response: Response): String? {
        return try {
            val body = response.body ?: return null
            val source = body.source()
            source.request(Long.MAX_VALUE)
            val buffer = source.buffer
            
            // Limit to 1KB for performance
            val maxSize = 1024L
            val size = minOf(buffer.size, maxSize)
            buffer.clone().readUtf8(size)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to extract response body: ${e.message}")
            null
        }
    }
    
    companion object {
        private const val TAG = "NetworkObserver"
        
        /**
         * Create OkHttp client with NetworkObserver
         * 
         * @param eventBus Event bus for publishing network events
         * @param config Observe configuration (optional, for SSL key capture)
         */
        fun createClient(
            eventBus: EventBus,
            config: ObserveConfig? = null
        ): okhttp3.OkHttpClient {
            val observer = NetworkObserver(eventBus)
            observer.start()
            
            val builder = okhttp3.OkHttpClient.Builder()
                .addInterceptor(observer)
            
            // Add SSL key capture if enabled
            if (config?.exportCryptoKeys == true) {
                Log.w(TAG, "🔓 SSL key capture ENABLED - traffic can be decrypted!")
                builder.addInterceptor(SSLKeyCapture())
            }
            
            // Bypass certificate pinning if enabled
            if (config?.bypassCertPinning == true) {
                Log.w(TAG, "🔓 Certificate pinning BYPASSED - MITM proxy allowed!")
                builder.bypassCertificatePinning()
            }
            
            return builder.build()
        }
    }
}
