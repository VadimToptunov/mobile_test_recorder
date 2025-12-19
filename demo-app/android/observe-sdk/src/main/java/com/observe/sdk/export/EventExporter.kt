package com.observe.sdk.export

import android.util.Log
import com.observe.sdk.core.ObserveConfig
import com.observe.sdk.events.EventBus
import kotlinx.coroutines.*

/**
 * Exports recorded events to server or local storage
 * 
 * TODO: Implement full functionality:
 * - Subscribe to event bus
 * - Batch events
 * - Send to server via HTTP
 * - Local SQLite fallback
 * - Retry logic
 */
class EventExporter(
    private val eventBus: EventBus,
    private val config: ObserveConfig
) {
    
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    fun start() {
        Log.d(TAG, "EventExporter started")
        // TODO: Start collecting events
        // TODO: Setup periodic flush
    }
    
    fun stop() {
        Log.d(TAG, "EventExporter stopping...")
        scope.cancel()
        // TODO: Flush remaining events
    }
    
    companion object {
        private const val TAG = "EventExporter"
    }
}

