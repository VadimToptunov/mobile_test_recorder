package com.observe.sdk.core

/**
 * Configuration for Observe SDK
 */
data class ObserveConfig(
    val appVersion: String,
    val serverUrl: String = "http://localhost:8080",
    val batchSize: Int = 50,
    val flushIntervalMs: Long = 5000,
    val enableNetworkCapture: Boolean = true,
    val enableHierarchyCapture: Boolean = true,
    val performanceMode: PerformanceMode = PerformanceMode.BALANCED
)

enum class PerformanceMode {
    AGGRESSIVE,  // Capture everything, may impact performance
    BALANCED,    // Reasonable balance between capture and performance
    MINIMAL      // Minimal overhead, capture only essential events
}

