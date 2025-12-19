package com.findemo

import android.app.Application
import android.util.Log

class FinDemoApplication : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        Log.d(TAG, "App starting - Build config:")
        Log.d(TAG, "  OBSERVE_ENABLED: ${BuildConfig.OBSERVE_ENABLED}")
        Log.d(TAG, "  TEST_MODE: ${BuildConfig.TEST_MODE}")
        
        // Initialize based on build variant
        when {
            BuildConfig.OBSERVE_ENABLED -> {
                initializeObserveMode()
            }
            BuildConfig.TEST_MODE -> {
                initializeTestMode()
            }
            else -> {
                initializeProductionMode()
            }
        }
    }
    
    private fun initializeObserveMode() {
        Log.i(TAG, "🎯 Observe mode enabled - SDK will record events")
        // ObserveSDK will be initialized here
        // This is done in observe source set
    }
    
    private fun initializeTestMode() {
        Log.i(TAG, "🧪 Test mode enabled")
        // Test-specific initialization
        // Could disable analytics, speed up animations, etc.
    }
    
    private fun initializeProductionMode() {
        Log.i(TAG, "🚀 Production mode")
        // Normal app initialization
        // Analytics, crashlytics, etc.
    }
    
    companion object {
        private const val TAG = "FinDemoApp"
    }
}

