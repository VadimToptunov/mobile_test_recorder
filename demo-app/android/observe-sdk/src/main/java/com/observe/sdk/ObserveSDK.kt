package com.observe.sdk

import android.app.Application
import android.util.Log
import com.observe.sdk.core.ObserveConfig
import com.observe.sdk.core.ObserveSession
import com.observe.sdk.events.EventBus
import com.observe.sdk.export.EventExporter
import com.observe.sdk.observers.UIObserver
import com.observe.sdk.observers.NavigationObserver
import com.observe.sdk.observers.NetworkObserver

/**
 * Main entry point for Observe SDK
 * 
 * Usage:
 * ```kotlin
 * // In Application.onCreate()
 * ObserveSDK.initialize(
 *     app = this,
 *     config = ObserveConfig(
 *         appVersion = BuildConfig.VERSION_NAME,
 *         serverUrl = "http://localhost:8080"
 *     )
 * )
 * ```
 */
object ObserveSDK {
    
    private const val TAG = "ObserveSDK"
    
    private var isInitialized = false
    private lateinit var config: ObserveConfig
    private lateinit var session: ObserveSession
    private lateinit var eventBus: EventBus
    
    // Observers
    private lateinit var uiObserver: UIObserver
    private lateinit var navigationObserver: NavigationObserver
    private lateinit var networkObserver: NetworkObserver
    
    // Exporter
    private lateinit var eventExporter: EventExporter
    
    /**
     * Initialize the Observe SDK
     * 
     * Should be called once in Application.onCreate()
     */
    fun initialize(app: Application, config: ObserveConfig) {
        if (isInitialized) {
            Log.w(TAG, "SDK already initialized")
            return
        }
        
        this.config = config
        
        Log.i(TAG, "🎯 Initializing Observe SDK...")
        Log.i(TAG, "   App version: ${config.appVersion}")
        Log.i(TAG, "   Server: ${config.serverUrl}")
        
        // Create session
        session = ObserveSession.create(
            appVersion = config.appVersion,
            platform = "android"
        )
        
        Log.i(TAG, "   Session ID: ${session.id}")
        
        // Initialize event bus
        eventBus = EventBus()
        
        // Initialize observers
        uiObserver = UIObserver(app, eventBus)
        navigationObserver = NavigationObserver(app, eventBus)
        networkObserver = NetworkObserver(eventBus)
        
        // Start observers
        uiObserver.start()
        navigationObserver.start()
        networkObserver.start()
        
        // Initialize exporter
        eventExporter = EventExporter(eventBus, config)
        eventExporter.start()
        
        isInitialized = true
        Log.i(TAG, "✅ Observe SDK initialized successfully")
    }
    
    /**
     * Get current session
     */
    fun getSession(): ObserveSession {
        checkInitialized()
        return session
    }
    
    /**
     * Shutdown SDK (for testing or cleanup)
     */
    fun shutdown() {
        if (!isInitialized) return
        
        Log.i(TAG, "Shutting down Observe SDK...")
        
        uiObserver.stop()
        navigationObserver.stop()
        networkObserver.stop()
        eventExporter.stop()
        
        isInitialized = false
        Log.i(TAG, "SDK shut down")
    }
    
    private fun checkInitialized() {
        if (!isInitialized) {
            throw IllegalStateException(
                "ObserveSDK not initialized. Call ObserveSDK.initialize() first."
            )
        }
    }
}

