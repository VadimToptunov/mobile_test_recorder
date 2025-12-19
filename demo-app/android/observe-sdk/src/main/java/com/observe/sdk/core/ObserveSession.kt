package com.observe.sdk.core

import android.os.Build
import java.util.UUID

/**
 * Represents a single observe recording session
 */
data class ObserveSession(
    val id: String,
    val startTime: Long,
    val appVersion: String,
    val platform: String,
    val deviceInfo: DeviceInfo
) {
    companion object {
        fun create(appVersion: String, platform: String): ObserveSession {
            return ObserveSession(
                id = UUID.randomUUID().toString(),
                startTime = System.currentTimeMillis(),
                appVersion = appVersion,
                platform = platform,
                deviceInfo = DeviceInfo.current()
            )
        }
    }
}

data class DeviceInfo(
    val model: String,
    val manufacturer: String,
    val osVersion: String,
    val sdkInt: Int
) {
    companion object {
        fun current(): DeviceInfo {
            return DeviceInfo(
                model = Build.MODEL,
                manufacturer = Build.MANUFACTURER,
                osVersion = Build.VERSION.RELEASE,
                sdkInt = Build.VERSION.SDK_INT
            )
        }
    }
}

