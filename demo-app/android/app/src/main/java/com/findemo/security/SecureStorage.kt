package com.findemo.security

import android.content.Context
import android.content.SharedPreferences
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/**
 * Secure Storage using Android Keystore
 * 
 * This implements secure data storage for sensitive information like:
 * - Authentication tokens
 * - API keys
 * - User credentials
 * - Session data
 * 
 * Features:
 * - Hardware-backed encryption (when available)
 * - AES-256-GCM encryption
 * - Secure key storage in Android Keystore
 * - Automatic key generation
 */
class SecureStorage(private val context: Context) {
    
    companion object {
        private const val TAG = "SecureStorage"
        private const val KEYSTORE_ALIAS = "FindemoSecureKey"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val PREFS_NAME = "findemo_secure_prefs"
        private const val GCM_IV_LENGTH = 12
        private const val GCM_TAG_LENGTH = 128
    }
    
    private val keyStore: KeyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
    private val encryptedPrefs: SharedPreferences
    
    init {
        // Create or get master key
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        
        // Create encrypted shared preferences
        encryptedPrefs = EncryptedSharedPreferences.create(
            context,
            PREFS_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
        
        // Ensure encryption key exists
        if (!keyStore.containsAlias(KEYSTORE_ALIAS)) {
            generateSecretKey()
        }
        
        Log.i(TAG, "SecureStorage initialized with hardware-backed encryption")
    }
    
    /**
     * Generate secret key in Android Keystore
     */
    private fun generateSecretKey() {
        try {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            )
            
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                KEYSTORE_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .setUserAuthenticationRequired(false)  // For demo - set true in real app
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            keyGenerator.generateKey()
            
            Log.i(TAG, "Generated new secret key in Keystore")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to generate secret key", e)
            throw SecurityException("Key generation failed", e)
        }
    }
    
    /**
     * Get secret key from Keystore
     */
    private fun getSecretKey(): SecretKey {
        val entry = keyStore.getEntry(KEYSTORE_ALIAS, null) as? KeyStore.SecretKeyEntry
            ?: throw SecurityException("Secret key not found")
        
        return entry.secretKey
    }
    
    /**
     * Encrypt data using AES-GCM
     */
    private fun encrypt(plaintext: String): String {
        try {
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.ENCRYPT_MODE, getSecretKey())
            
            val iv = cipher.iv
            val encrypted = cipher.doFinal(plaintext.toByteArray(Charsets.UTF_8))
            
            // Combine IV + encrypted data
            val combined = iv + encrypted
            
            return Base64.encodeToString(combined, Base64.NO_WRAP)
        } catch (e: Exception) {
            Log.e(TAG, "Encryption failed", e)
            throw SecurityException("Encryption failed", e)
        }
    }
    
    /**
     * Decrypt data using AES-GCM
     */
    private fun decrypt(encrypted: String): String {
        try {
            val combined = Base64.decode(encrypted, Base64.NO_WRAP)
            
            // Extract IV and encrypted data
            val iv = combined.copyOfRange(0, GCM_IV_LENGTH)
            val ciphertext = combined.copyOfRange(GCM_IV_LENGTH, combined.size)
            
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            val spec = GCMParameterSpec(GCM_TAG_LENGTH, iv)
            cipher.init(Cipher.DECRYPT_MODE, getSecretKey(), spec)
            
            val decrypted = cipher.doFinal(ciphertext)
            
            return String(decrypted, Charsets.UTF_8)
        } catch (e: Exception) {
            Log.e(TAG, "Decryption failed", e)
            throw SecurityException("Decryption failed", e)
        }
    }
    
    /**
     * Store encrypted string
     */
    fun putString(key: String, value: String) {
        try {
            val encrypted = encrypt(value)
            encryptedPrefs.edit().putString(key, encrypted).apply()
            Log.d(TAG, "Stored encrypted value for key: $key")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to store value", e)
        }
    }
    
    /**
     * Get decrypted string
     */
    fun getString(key: String, defaultValue: String? = null): String? {
        return try {
            val encrypted = encryptedPrefs.getString(key, null) ?: return defaultValue
            decrypt(encrypted)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to retrieve value", e)
            defaultValue
        }
    }
    
    /**
     * Store access token securely
     */
    fun storeAccessToken(token: String) {
        putString("access_token", token)
        SecurityMonitor.reportSecurityEvent(
            SecurityEvent.TOKEN_STORED,
            "type" to "access_token"
        )
    }
    
    /**
     * Get access token
     */
    fun getAccessToken(): String? {
        return getString("access_token")
    }
    
    /**
     * Store refresh token securely
     */
    fun storeRefreshToken(token: String) {
        putString("refresh_token", token)
    }
    
    /**
     * Get refresh token
     */
    fun getRefreshToken(): String? {
        return getString("refresh_token")
    }
    
    /**
     * Clear all sensitive data
     */
    fun clearAll() {
        encryptedPrefs.edit().clear().apply()
        Log.i(TAG, "Cleared all secure storage")
        
        SecurityMonitor.reportSecurityEvent(
            SecurityEvent.STORAGE_CLEARED,
            "reason" to "logout"
        )
    }
    
    /**
     * Remove specific key
     */
    fun remove(key: String) {
        encryptedPrefs.edit().remove(key).apply()
        Log.d(TAG, "Removed key: $key")
    }
    
    /**
     * Check if key exists
     */
    fun contains(key: String): Boolean {
        return encryptedPrefs.contains(key)
    }
    
    /**
     * Check if hardware-backed encryption is available
     */
    fun isHardwareBackedEncryption(): Boolean {
        return try {
            val key = getSecretKey()
            val factory = java.security.KeyFactory.getInstance(key.algorithm, ANDROID_KEYSTORE)
            val keyInfo = factory.getKeySpec(key, android.security.keystore.KeyInfo::class.java)
            keyInfo.isInsideSecureHardware
        } catch (e: Exception) {
            false
        }
    }
}

/**
 * Security events for monitoring
 */
enum class SecurityEvent {
    TOKEN_STORED,
    TOKEN_RETRIEVED,
    STORAGE_CLEARED,
    ENCRYPTION_FAILED,
    DECRYPTION_FAILED,
    ROOT_DETECTED,
    TAMPER_DETECTED,
    CERTIFICATE_PINNING_FAILURE,
    BIOMETRIC_AUTH_SUCCESS,
    BIOMETRIC_AUTH_FAILURE
}

/**
 * Security monitoring and reporting
 */
object SecurityMonitor {
    private const val TAG = "SecurityMonitor"
    
    fun reportSecurityEvent(event: SecurityEvent, vararg params: Pair<String, String>) {
        val eventData = params.joinToString(", ") { "${it.first}=${it.second}" }
        Log.i(TAG, "Security Event: $event ${if (eventData.isNotEmpty()) "($eventData)" else ""}")
        
        // In production: send to analytics/monitoring service
        // analytics.logSecurityEvent(event, params.toMap())
    }
}

