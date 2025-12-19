package com.observe.sdk.observers

import android.app.Activity
import android.app.Application
import android.os.Bundle
import android.util.Log
import com.observe.sdk.events.Event
import com.observe.sdk.events.EventBus
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

/**
 * Observes navigation events and screen transitions
 * 
 * Features:
 * - Tracks Activity lifecycle (onCreate, onResume, onPause, onStop)
 * - Records screen transitions with timing
 * - Captures screen stack information
 * - Emits navigation events to EventBus
 */
class NavigationObserver(
    private val app: Application,
    private val eventBus: EventBus
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val screenStack = mutableListOf<ScreenInfo>()
    private var currentScreen: ScreenInfo? = null
    
    private val activityLifecycleCallbacks = object : Application.ActivityLifecycleCallbacks {
        override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
            val screenName = activity.javaClass.simpleName
            Log.d(TAG, "Screen created: $screenName")
            
            val screenInfo = ScreenInfo(
                name = screenName,
                className = activity.javaClass.name,
                createTime = System.currentTimeMillis(),
                resumeTime = null
            )
            
            // Emit screen create event
            scope.launch {
                val navEvent = Event.NavigationEvent(
                    timestamp = System.currentTimeMillis(),
                    sessionId = "",
                    fromScreen = currentScreen?.name,
                    toScreen = screenName,
                    navType = "created",
                    params = null
                )
                eventBus.publish(navEvent)
            }
            
            // Track in stack
            screenStack.add(screenInfo)
        }

        override fun onActivityStarted(activity: Activity) {
            Log.d(TAG, "Screen started: ${activity.javaClass.simpleName}")
        }

        override fun onActivityResumed(activity: Activity) {
            val screenName = activity.javaClass.simpleName
            Log.d(TAG, "Screen resumed: $screenName")
            
            val fromScreen = currentScreen?.name
            val resumeTime = System.currentTimeMillis()
            
            // Update current screen
            currentScreen = screenStack.find { it.name == screenName }?.apply {
                this.resumeTime = resumeTime
            }
            
            // Emit navigation event
            scope.launch {
                val navEvent = Event.NavigationEvent(
                    timestamp = resumeTime,
                    sessionId = "",
                    fromScreen = fromScreen,
                    toScreen = screenName,
                    navType = "navigate",
                    params = extractScreenParams(activity)
                )
                eventBus.publish(navEvent)
                
                Log.d(TAG, "Navigation: $fromScreen -> $screenName")
            }
        }

        override fun onActivityPaused(activity: Activity) {
            val screenName = activity.javaClass.simpleName
            Log.d(TAG, "Screen paused: $screenName")
            
            scope.launch {
                val navEvent = Event.NavigationEvent(
                    timestamp = System.currentTimeMillis(),
                    sessionId = "",
                    fromScreen = screenName,
                    toScreen = null,
                    navType = "paused",
                    params = null
                )
                eventBus.publish(navEvent)
            }
        }

        override fun onActivityStopped(activity: Activity) {
            val screenName = activity.javaClass.simpleName
            Log.d(TAG, "Screen stopped: $screenName")
        }

        override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}

        override fun onActivityDestroyed(activity: Activity) {
            val screenName = activity.javaClass.simpleName
            Log.d(TAG, "Screen destroyed: $screenName")
            
            // Remove from stack
            screenStack.removeAll { it.name == screenName }
            
            // Emit destroy event
            scope.launch {
                val navEvent = Event.NavigationEvent(
                    timestamp = System.currentTimeMillis(),
                    sessionId = "",
                    fromScreen = screenName,
                    toScreen = null,
                    navType = "destroyed",
                    params = null
                )
                eventBus.publish(navEvent)
            }
            
            if (currentScreen?.name == screenName) {
                currentScreen = screenStack.lastOrNull()
            }
        }
    }
    
    fun start() {
        Log.d(TAG, "NavigationObserver started")
        app.registerActivityLifecycleCallbacks(activityLifecycleCallbacks)
    }
    
    fun stop() {
        Log.d(TAG, "NavigationObserver stopped")
        app.unregisterActivityLifecycleCallbacks(activityLifecycleCallbacks)
        screenStack.clear()
        currentScreen = null
    }
    
    /**
     * Extract parameters from Activity intent
     */
    private fun extractScreenParams(activity: Activity): String? {
        return try {
            val intent = activity.intent
            val extras = intent.extras
            
            if (extras != null && !extras.isEmpty) {
                val params = mutableMapOf<String, String>()
                for (key in extras.keySet()) {
                    val value = extras.get(key)
                    params[key] = value?.toString() ?: "null"
                }
                params.toString()
            } else {
                null
            }
        } catch (e: Exception) {
            Log.w(TAG, "Failed to extract screen params: ${e.message}")
            null
        }
    }
    
    /**
     * Get current navigation stack
     */
    fun getNavigationStack(): List<String> {
        return screenStack.map { it.name }
    }
    
    /**
     * Get current screen name
     */
    fun getCurrentScreen(): String? {
        return currentScreen?.name
    }
    
    /**
     * Screen information
     */
    private data class ScreenInfo(
        val name: String,
        val className: String,
        val createTime: Long,
        var resumeTime: Long?
    )
    
    companion object {
        private const val TAG = "NavigationObserver"
    }
}
