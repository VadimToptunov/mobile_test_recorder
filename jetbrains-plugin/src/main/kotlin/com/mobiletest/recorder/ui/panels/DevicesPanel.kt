package com.mobiletest.recorder.ui.panels

import com.google.gson.JsonArray
import com.google.gson.JsonObject
import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.table.JBTable
import com.mobiletest.recorder.services.MTRDaemonService
import java.awt.BorderLayout
import javax.swing.*
import javax.swing.table.DefaultTableModel

class DevicesPanel(
    private val project: Project,
    private val daemonService: MTRDaemonService
) {
    private val panel = JPanel(BorderLayout())
    private val tableModel = DefaultTableModel(
        arrayOf("ID", "Name", "Platform", "Status"),
        0
    )
    private val table = JBTable(tableModel)
    
    init {
        // Toolbar
        val toolbar = JPanel()
        val refreshButton = JButton("Refresh")
        refreshButton.addActionListener {
            refreshDevices()
        }
        toolbar.add(refreshButton)
        
        // Table
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        val scrollPane = JBScrollPane(table)
        
        panel.add(toolbar, BorderLayout.NORTH)
        panel.add(scrollPane, BorderLayout.CENTER)
    }
    
    fun refreshDevices() {
        SwingWorker<JsonObject?, Void>().apply {
            override fun doInBackground(): JsonObject? {
                return try {
                    daemonService.listDevices("all")
                } catch (e: Exception) {
                    null
                }
            }
            
            override fun done() {
                val result = get()
                if (result != null) {
                    updateTable(result)
                } else {
                    JOptionPane.showMessageDialog(
                        panel,
                        "Failed to list devices. Is daemon running?",
                        "Error",
                        JOptionPane.ERROR_MESSAGE
                    )
                }
            }
        }.execute()
    }
    
    private fun updateTable(result: JsonObject) {
        tableModel.rowCount = 0
        
        val devices = result.getAsJsonArray("devices") ?: JsonArray()
        for (element in devices) {
            val device = element.asJsonObject
            tableModel.addRow(arrayOf(
                device.get("id")?.asString ?: "",
                device.get("name")?.asString ?: "",
                device.get("platform")?.asString ?: "",
                device.get("status")?.asString ?: ""
            ))
        }
    }
    
    fun getPanel(): JComponent = panel
}
