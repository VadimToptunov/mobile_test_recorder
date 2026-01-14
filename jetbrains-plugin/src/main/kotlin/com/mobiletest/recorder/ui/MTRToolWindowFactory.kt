package com.mobiletest.recorder.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory

class MTRToolWindowFactory : ToolWindowFactory {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val mtrToolWindow = MTRToolWindow(project)
        val contentFactory = ContentFactory.getInstance()
        val content = contentFactory.createContent(mtrToolWindow.getContent(), "", false)
        toolWindow.contentManager.addContent(content)
    }
}
