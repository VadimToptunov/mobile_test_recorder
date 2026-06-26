package com.mobiletest.recorder.ui.panels

import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.mobiletest.recorder.services.MTRDaemonService
import java.awt.BorderLayout
import javax.swing.*

class LogsPanel(
    private val project: Project,
    private val daemonService: MTRDaemonService
) {
    private val panel = JPanel(BorderLayout())
    private val logsTextArea = JTextArea()
    
    init {
        logsTextArea.isEditable = false
        logsTextArea.font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 11)
        
        val scrollPane = JBScrollPane(logsTextArea)
        
        // Toolbar
        val toolbar = JPanel()
        val clearButton = JButton("Clear")
        clearButton.addActionListener {
            logsTextArea.text = ""
        }
        toolbar.add(clearButton)
        
        panel.add(toolbar, BorderLayout.NORTH)
        panel.add(scrollPane, BorderLayout.CENTER)
        
        // Listen for daemon logs
        daemonService.addNotificationListener { notification ->
            if (notification.method == "logs/message") {
                val params = notification.params
                val message = params.get("message")?.asString ?: ""
                val timestamp = params.get("timestamp")?.asString ?: ""
                val level = params.get("level")?.asString ?: "INFO"
                
                SwingUtilities.invokeLater {
                    logsTextArea.append("[$timestamp] $level: $message\n")
                    logsTextArea.caretPosition = logsTextArea.document.length
                }
            }
        }
    }
    
    fun getPanel(): JComponent = panel
}
