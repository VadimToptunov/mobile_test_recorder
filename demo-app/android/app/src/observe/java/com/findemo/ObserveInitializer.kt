package com.findemo

import android.app.Application
import android.util.Log
import com.observe.sdk.ObserveSDK
import com.observe.sdk.core.ObserveConfig

/**
 * Initializer for Observe build variant
 * 
 * This file ONLY exists in observe source set
 * It will NOT be compiled into test or prod builds
 */
object ObserveInitializer {
    
    private const val TAG = "ObserveInit"
    
    fun initialize(app: Application) {
        Log.i(TAG, " Initializing Observe SDK for observe build")
        
        try {
            ObserveSDK.initialize(
                app = app,
                config = ObserveConfig(
                    appVersion = BuildConfig.VERSION_NAME,
                    serverUrl = "http://10.0.2.2:8080",  // Android emulator localhost
                    batchSize = 50,
                    flushIntervalMs = 5000
                )
            )
            
            Log.i(TAG, " Observe SDK initialized successfully")
        } catch (e: Exception) {
            Log.e(TAG, " Failed to initialize Observe SDK", e)
        }
    }
}

/**
 * Extension function for Application class
 * Available ONLY in observe build
 */
fun Application.initializeObserveSDK() {
    ObserveInitializer.initialize(this)
}

