package com.mobiletest.recorder.ui.panels

import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.mobiletest.recorder.services.MTRDaemonService
import java.awt.BorderLayout
import javax.swing.*

class InspectorPanel(
    private val project: Project,
    private val daemonService: MTRDaemonService
) {
    private val panel = JPanel(BorderLayout())
    private val xmlTextArea = JTextArea()
    
    init {
        xmlTextArea.isEditable = false
        xmlTextArea.font = java.awt.Font("Monospaced", java.awt.Font.PLAIN, 12)
        
        val scrollPane = JBScrollPane(xmlTextArea)
        
        // Toolbar
        val toolbar = JPanel()
        val captureButton = JButton("Capture UI Tree")
        captureButton.addActionListener {
            captureUiTree()
        }
        toolbar.add(captureButton)
        
        panel.add(toolbar, BorderLayout.NORTH)
        panel.add(scrollPane, BorderLayout.CENTER)
    }
    
    private fun captureUiTree() {
        // TODO: Implement when session management is ready
        xmlTextArea.text = "UI Tree capture will be available in Phase 2"
    }
    
    fun getPanel(): JComponent = panel
}
