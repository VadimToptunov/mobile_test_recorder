package com.observe.sdk

import android.app.Application
import android.util.Log
import android.webkit.WebView
import com.observe.sdk.core.ObserveConfig
import com.observe.sdk.core.ObserveSession
import com.observe.sdk.events.Event
import com.observe.sdk.events.EventBus
import com.observe.sdk.export.EventExporter
import com.observe.sdk.observers.NavigationObserver
import com.observe.sdk.observers.NetworkObserver
import com.observe.sdk.observers.UIObserver
import com.observe.sdk.observers.WebViewObserver
import com.observe.sdk.security.CryptoKeyExporter
import java.io.File
import java.util.UUID

/**
 * Main entry point for Observe SDK
 * 
 * Usage:
 * ```kotlin
 * // In Application class
 * class MyApp : Application() {
 *     override fun onCreate() {
 *         super.onCreate()
 *         ObserveSDK.initialize(
 *             this,
 *             ObserveConfig(enabled = true)
 *         )
 *     }
 * }
 * ```
 */
object ObserveSDK {
    
    private var isInitialized = false
    private var isStarted = false
    
    private lateinit var application: Application
    private lateinit var config: ObserveConfig
    private lateinit var session: ObserveSession
    
    // Core components
    private lateinit var eventBus: EventBus
    private lateinit var eventExporter: EventExporter
    
    // Observers
    private lateinit var uiObserver: UIObserver
    private lateinit var navigationObserver: NavigationObserver
    private lateinit var networkObserver: NetworkObserver
    private lateinit var webViewObserver: WebViewObserver
    
    /**
     * Initialize SDK with configuration
     */
    fun initialize(app: Application, cfg: ObserveConfig) {
        if (isInitialized) {
            Log.w(TAG, "SDK already initialized")
            return
        }
        
        application = app
        config = cfg
        
        if (!config.enabled) {
            Log.i(TAG, "SDK disabled by config")
            return
        }
        
        Log.i(TAG, "Initializing ObserveSDK...")
        
        // Create session
        session = ObserveSession.create(app)
        
        // Initialize components
        eventBus = EventBus()
        eventExporter = EventExporter(
            context = app,
            config = EventExporter.ExportConfig(
                bufferSize = cfg.eventBufferSize,
                maxStoredFiles = cfg.maxStoredFiles
            )
        )
        
        // Initialize crypto key exporter if enabled
        if (cfg.exportCryptoKeys) {
            Log.w(TAG, "🔐 Crypto key export ENABLED - this build can decrypt traffic!")
            CryptoKeyExporter.initialize(cfg)
        }
        
        // Initialize observers
        uiObserver = UIObserver(app, eventBus)
        navigationObserver = NavigationObserver(app, eventBus)
        networkObserver = NetworkObserver(eventBus)
        webViewObserver = WebViewObserver(app, eventBus)
        
        // Subscribe to events
        subscribeToEvents()
        
        isInitialized = true
        
        // Auto-start if configured
        if (config.autoStart) {
            start()
        }
        
        Log.i(TAG, "SDK initialized successfully. Session: ${session.sessionId}")
    }
    
    /**
     * Start observation
     */
    fun start() {
        if (!isInitialized) {
            Log.e(TAG, "SDK not initialized. Call initialize() first.")
            return
        }
        
        if (isStarted) {
            Log.w(TAG, "SDK already started")
            return
        }
        
        Log.i(TAG, "Starting observation...")
        
        // Start exporter
        eventExporter.start()
        
        // Start observers
        uiObserver.start()
        navigationObserver.start()
        networkObserver.start()
        webViewObserver.start()
        
        // Emit session start event
        eventBus.publish(Event.SessionEvent(
            timestamp = System.currentTimeMillis(),
            sessionId = session.sessionId,
            eventType = "session_start",
            data = mapOf(
                "device_model" to session.deviceModel,
                "os_version" to session.osVersion,
                "app_version" to session.appVersion
            )
        ))
        
        isStarted = true
        Log.i(TAG, "Observation started")
    }
    
    /**
     * Stop observation
     */
    fun stop() {
        if (!isStarted) {
            Log.w(TAG, "SDK not started")
            return
        }
        
        Log.i(TAG, "Stopping observation...")
        
        // Emit session end event
        eventBus.publish(Event.SessionEvent(
            timestamp = System.currentTimeMillis(),
            sessionId = session.sessionId,
            eventType = "session_end",
            data = mapOf(
                "duration" to (System.currentTimeMillis() - session.startTime),
                "event_count" to eventExporter.getEventCount()
            )
        ))
        
        // Stop observers
        uiObserver.stop()
        navigationObserver.stop()
        networkObserver.stop()
        webViewObserver.stop()
        
        // Stop exporter (will flush events)
        eventExporter.stop()
        
        isStarted = false
        Log.i(TAG, "Observation stopped")
    }
    
    /**
     * Subscribe to EventBus and forward to exporter
     */
    private fun subscribeToEvents() {
        eventBus.subscribe<Event.UIEvent> { event ->
            // Set session ID
            val eventWithSession = event.copy(sessionId = session.sessionId)
            eventExporter.queueEvent(eventWithSession)
            Log.d(TAG, "UI Event: ${event.actionType} on ${event.screen}")
        }
        
        eventBus.subscribe<Event.NavigationEvent> { event ->
            val eventWithSession = event.copy(sessionId = session.sessionId)
            eventExporter.queueEvent(eventWithSession)
            Log.d(TAG, "Navigation: ${event.fromScreen} -> ${event.toScreen}")
        }
        
        eventBus.subscribe<Event.NetworkEvent> { event ->
            val eventWithSession = event.copy(sessionId = session.sessionId)
            eventExporter.queueEvent(eventWithSession)
            Log.d(TAG, "Network: ${event.method} ${event.endpoint} [${event.statusCode}]")
        }
        
        eventBus.subscribe<Event.SessionEvent> { event ->
            eventExporter.queueEvent(event)
            Log.d(TAG, "Session: ${event.eventType}")
        }
    }
    
    /**
     * Get current session info
     */
    fun getSession(): ObserveSession? {
        return if (isInitialized) session else null
    }
    
    /**
     * Get network observer for OkHttp integration
     */
    fun getNetworkObserver(): NetworkObserver? {
        return if (isInitialized) networkObserver else null
    }
    
    /**
     * Get exported event files
     */
    fun getExportedFiles(): List<java.io.File> {
        return if (isInitialized) {
            eventExporter.getExportedFiles()
        } else {
            emptyList()
        }
    }
    
    /**
     * Clear all exported events
     */
    fun clearExports() {
        if (isInitialized) {
            eventExporter.clearExports()
        }
    }
    
    /**
     * Check if SDK is initialized
     */
    fun isInitialized(): Boolean = isInitialized
    
    /**
     * Check if observation is active
     */
    fun isRunning(): Boolean = isStarted
    
    /**
     * Get event count
     */
    fun getEventCount(): Int {
        return if (isInitialized) {
            eventExporter.getEventCount()
        } else {
            0
        }
    }
    
    /**
     * Export crypto keys for traffic decryption
     * 
     * SECURITY WARNING:
     * This exports TLS/SSL session keys and device encryption keys!
     * Only call this in test/observe builds!
     * 
     * Returns: File with exported keys (JSON format)
     */
    fun exportCryptoKeys(): File? {
        if (!isInitialized) {
            Log.w(TAG, "Cannot export crypto keys - SDK not initialized")
            return null
        }
        
        if (!config.exportCryptoKeys) {
            Log.w(TAG, "Crypto key export is disabled in config")
            return null
        }
        
        Log.i(TAG, "Exporting crypto keys...")
        return CryptoKeyExporter.exportKeys(application, session.sessionId)
    }
    
    /**
     * Export TLS keys in NSS Key Log format (for Wireshark)
     * 
     * Returns: File with TLS keys in Wireshark-compatible format
     */
    fun exportTLSKeys(): File? {
        if (!isInitialized) {
            Log.w(TAG, "Cannot export TLS keys - SDK not initialized")
            return null
        }
        
        if (!config.exportCryptoKeys) {
            Log.w(TAG, "Crypto key export is disabled in config")
            return null
        }
        
        Log.i(TAG, "Exporting TLS keys (NSS format)...")
        return CryptoKeyExporter.exportNSSKeyLog(application, session.sessionId)
    }
    
    /**
     * Register a WebView for observation
     * 
     * Call this when creating a WebView to observe:
     * - Page loads
     * - DOM element clicks
     * - Form inputs
     * - Form submissions
     * - Element hierarchy
     * 
     * Example:
     * ```kotlin
     * val webView = WebView(context)
     * ObserveSDK.observeWebView(webView, "PaymentScreen")
     * ```
     */
    fun observeWebView(webView: WebView, screenName: String) {
        if (!isInitialized) {
            Log.w(TAG, "Cannot observe WebView - SDK not initialized")
            return
        }
        
        if (!isStarted) {
            Log.w(TAG, "Cannot observe WebView - SDK not started")
            return
        }
        
        webViewObserver.observeWebView(webView, screenName)
    }
    
    /**
     * Stop observing a WebView
     */
    fun stopObservingWebView(webView: WebView) {
        if (!isInitialized || !isStarted) return
        webViewObserver.stopObservingWebView(webView)
    }
    
    /**
     * Get crypto key export stats
     */
    fun getCryptoKeyStats(): Map<String, Any>? {
        if (!isInitialized || !config.exportCryptoKeys) {
            return null
        }
        
        return CryptoKeyExporter.getStats()
    }
    
    private const val TAG = "ObserveSDK"
}