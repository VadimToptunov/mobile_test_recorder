package com.mobiletest.recorder.settings

import com.intellij.openapi.options.Configurable
import javax.swing.JComponent
import javax.swing.JPanel
import javax.swing.JLabel
import java.awt.BorderLayout

class MTRSettingsConfigurable : Configurable {
    private var settingsPanel: JPanel? = null
    
    override fun getDisplayName(): String = "Mobile Test Recorder"
    
    override fun createComponent(): JComponent {
        settingsPanel = JPanel(BorderLayout())
        settingsPanel?.add(JLabel("Settings panel - Coming soon in Phase 4"), BorderLayout.CENTER)
        return settingsPanel!!
    }
    
    override fun isModified(): Boolean = false
    
    override fun apply() {
        // TODO: Save settings
    }
    
    override fun reset() {
        // TODO: Reset settings
    }
}
