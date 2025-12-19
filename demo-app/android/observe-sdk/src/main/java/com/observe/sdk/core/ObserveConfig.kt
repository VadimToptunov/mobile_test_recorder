package com.observe.sdk.core

/**
 * Configuration for Observe SDK
 * 
 * @param enabled Enable/disable SDK
 * @param autoStart Automatically start observation on init
 * @param eventBufferSize Number of events to buffer before export
 * @param maxStoredFiles Maximum number of event files to keep
 * @param exportEndpoint Optional network endpoint for event upload
 * @param debugMode Enable verbose logging
 */
data class ObserveConfig(
    val enabled: Boolean = true,
    val autoStart: Boolean = true,
    val eventBufferSize: Int = 50,
    val maxStoredFiles: Int = 10,
    val exportEndpoint: String? = null,
    val debugMode: Boolean = true
) {
    companion object {
        /**
         * Default configuration
         */
        fun default() = ObserveConfig()
        
        /**
         * Disabled configuration (for production)
         */
        fun disabled() = ObserveConfig(enabled = false)
    }
}
