package com.findemo.ui.kyc

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.regula.documentreader.api.DocumentReader
import com.regula.documentreader.api.completions.IDocumentReaderCompletion
import com.regula.documentreader.api.completions.IDocumentReaderInitCompletion
import com.regula.documentreader.api.enums.DocReaderAction
import com.regula.documentreader.api.enums.Scenario
import com.regula.documentreader.api.errors.DocumentReaderException
import com.regula.documentreader.api.params.DocReaderConfig
import com.regula.documentreader.api.results.DocumentReaderResults

@Composable
fun KYCScreen(
    onKYCComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    var isSDKInitialized by remember { mutableStateOf(false) }
    var isScanning by remember { mutableStateOf(false) }
    var scanResult by remember { mutableStateOf<String?>(null) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    // Camera permission launcher
    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            startDocumentScanning(context) { result, error ->
                scanResult = result
                errorMessage = error
                isScanning = false
            }
        } else {
            errorMessage = "Camera permission is required for document scanning"
            isScanning = false
        }
    }
    
    // Initialize Regula SDK
    LaunchedEffect(Unit) {
        initializeRegulaSDK(context) { success, error ->
            isSDKInitialized = success
            if (!success) {
                errorMessage = error
            }
        }
    }
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("kyc_screen"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Title
        Text(
            text = "Identity Verification",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Please scan your ID document to verify your identity",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
        
        Spacer(modifier = Modifier.height(48.dp))
        
        // Status icon
        if (scanResult != null) {
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = "Success",
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.primary
            )
        } else {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = "Identity",
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Scan result
        if (scanResult != null) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Document Scanned Successfully!",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = scanResult!!,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                }
            }
        }
        
        // Error message
        if (errorMessage != null) {
            Text(
                text = errorMessage!!,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Scan button
        Button(
            onClick = {
                if (!isSDKInitialized) {
                    errorMessage = "SDK is still initializing, please wait..."
                    return@Button
                }
                
                isScanning = true
                errorMessage = null
                
                // Check camera permission
                when {
                    ContextCompat.checkSelfPermission(
                        context,
                        Manifest.permission.CAMERA
                    ) == PackageManager.PERMISSION_GRANTED -> {
                        // Permission granted, start scanning
                        startDocumentScanning(context) { result, error ->
                            scanResult = result
                            errorMessage = error
                            isScanning = false
                        }
                    }
                    else -> {
                        // Request permission
                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    }
                }
            },
            enabled = isSDKInitialized && !isScanning && scanResult == null,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
                .testTag("scan_document_button")
        ) {
            if (isScanning) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Icon(Icons.Default.Camera, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Scan ID Document")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Continue button (shown after successful scan)
        if (scanResult != null) {
            Button(
                onClick = onKYCComplete,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp)
                    .testTag("complete_kyc_button")
            ) {
                Text("Complete Verification")
            }
        } else {
            // Skip button (for demo purposes)
            TextButton(
                onClick = onKYCComplete,
                modifier = Modifier.testTag("skip_kyc_button")
            ) {
                Text("Skip for Now")
            }
        }
    }
}

/**
 * Initialize Regula Document Reader SDK
 */
private fun initializeRegulaSDK(
    context: Context,
    callback: (success: Boolean, error: String?) -> Unit
) {
    if (DocumentReader.Instance().isReady) {
        callback(true, null)
        return
    }
    
    try {
        // Initialize with license (for production, use actual license)
        // For demo, SDK will work in trial mode
        val config = DocReaderConfig()
        
        DocumentReader.Instance().initializeReader(
            context,
            config,
            object : IDocumentReaderInitCompletion {
                override fun onSuccess() {
                    callback(true, null)
                }
                
                override fun onError(error: DocumentReaderException?) {
                    callback(
                        false,
                        error?.message ?: "Failed to initialize document reader"
                    )
                }
            }
        )
    } catch (e: Exception) {
        callback(false, "Initialization error: ${e.message}")
    }
}

/**
 * Start document scanning with Regula SDK
 */
private fun startDocumentScanning(
    context: Context,
    callback: (result: String?, error: String?) -> Unit
) {
    try {
        // Configure scanning scenario
        DocumentReader.Instance().functionality().edit().setScenario(
            Scenario.SCENARIO_MRZ  // Machine Readable Zone
        ).apply()
        
        // Start scanning
        DocumentReader.Instance().showScanner(
            context,
            object : IDocumentReaderCompletion {
                override fun onCompleted(
                    action: Int,
                    results: DocumentReaderResults?,
                    error: DocumentReaderException?
                ) {
                    when (action) {
                        DocReaderAction.COMPLETE -> {
                            if (results != null) {
                                // Extract document data
                                val documentType = results.getTextFieldValueByType(
                                    com.regula.documentreader.api.enums.eVisualFieldType.FT_DOCUMENT_CLASS_NAME
                                ) ?: "Unknown"
                                
                                val name = results.getTextFieldValueByType(
                                    com.regula.documentreader.api.enums.eVisualFieldType.FT_SURNAME_AND_GIVEN_NAMES
                                ) ?: "N/A"
                                
                                val documentNumber = results.getTextFieldValueByType(
                                    com.regula.documentreader.api.enums.eVisualFieldType.FT_DOCUMENT_NUMBER
                                ) ?: "N/A"
                                
                                val result = """
                                    Document Type: $documentType
                                    Name: $name
                                    Document Number: $documentNumber
                                """.trimIndent()
                                
                                callback(result, null)
                            } else {
                                callback(null, "No results received")
                            }
                        }
                        DocReaderAction.CANCEL -> {
                            callback(null, "Scanning cancelled")
                        }
                        DocReaderAction.ERROR -> {
                            callback(null, error?.message ?: "Scanning error")
                        }
                        else -> {
                            callback(null, "Unknown action")
                        }
                    }
                }
            }
        )
    } catch (e: Exception) {
        callback(null, "Scanning error: ${e.message}")
    }
}

