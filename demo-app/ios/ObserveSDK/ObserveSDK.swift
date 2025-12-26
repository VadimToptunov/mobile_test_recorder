//
//  ObserveSDK.swift
//  ObserveSDK
//
//  Main entry point for iOS Observe SDK
//

import Foundation
import UIKit
import SwiftUI
import WebKit

/// Main SDK class for observing app behavior
public class ObserveSDK {
    
    // MARK: - Singleton
    
    public static let shared = ObserveSDK()
    
    private init() {}
    
    // MARK: - Properties
    
    private var isInitializedFlag = false
    private var isStarted = false
    
    private var application: UIApplication?
    private var config: ObserveConfig?
    private var session: ObserveSession?
    
    private var eventBus: EventBus?
    private var eventExporter: EventExporter?
    
    private var uiObserver: UIObserver?
    private var navigationObserver: NavigationObserver?
    private var networkObserver: NetworkObserver?
    private var hierarchyCollector: HierarchyCollector?
    private var webViewObserver: WebViewObserver?
    
    // MARK: - Public API
    
    /// Initialize the Observe SDK
    /// - Parameters:
    ///   - application: UIApplication instance
    ///   - config: Configuration for the SDK
    public func initialize(application: UIApplication, config: ObserveConfig) {
        guard !isInitializedFlag else {
            print("[ObserveSDK] Already initialized")
            return
        }
        
        self.application = application
        self.config = config
        
        // Mark as initialized before checking enabled flag
        isInitializedFlag = true
        
        guard config.enabled else {
            print("[ObserveSDK] Disabled by config (initialized but inactive)")
            return
        }
        
        print("[ObserveSDK] Initializing...")
        
        // Create session
        session = ObserveSession.create()
        
        // Initialize components
        eventBus = EventBus()
        eventExporter = EventExporter(config: EventExporter.ExportConfig(
            bufferSize: config.eventBufferSize,
            maxStoredFiles: config.maxStoredFiles,
            exportIntervalMs: config.flushIntervalMs
        ))
        
        // Initialize observers
        uiObserver = UIObserver(eventBus: eventBus!)
        navigationObserver = NavigationObserver(eventBus: eventBus!)
        networkObserver = NetworkObserver(eventBus: eventBus!)
        hierarchyCollector = HierarchyCollector(eventBus: eventBus!)
        webViewObserver = WebViewObserver(eventBus: eventBus!)
        
        // Subscribe to events
        subscribeToEvents()
        
        // Auto-start if configured
        if config.autoStart {
            start()
        }
        
        print("[ObserveSDK] Initialized successfully. Session: \(session?.sessionId ?? "unknown")")
    }
    
    /// Start observing
    public func start() {
        guard isInitializedFlag else {
            print("[ObserveSDK] Cannot start - not initialized")
            return
        }
        
        guard !isStarted else {
            print("[ObserveSDK] Already started")
            return
        }
        
        guard config?.enabled == true else {
            print("[ObserveSDK] Cannot start - disabled by config")
            return
        }
        
        print("[ObserveSDK] Starting observation...")
        
        isStarted = true
        
        // Start components
        eventExporter?.start()
        uiObserver?.start()
        navigationObserver?.start()
        networkObserver?.start()
        hierarchyCollector?.start()
        webViewObserver?.start()
        
        print("[ObserveSDK] Started")
    }
    
    /// Stop observing
    public func stop() {
        guard isStarted else {
            print("[ObserveSDK] Not started")
            return
        }
        
        print("[ObserveSDK] Stopping...")
        
        // Stop observers first
        uiObserver?.stop()
        navigationObserver?.stop()
        networkObserver?.stop()
        hierarchyCollector?.stop()
        webViewObserver?.stop()
        
        // Stop exporter (will flush remaining events)
        eventExporter?.stop()
        
        isStarted = false
        
        print("[ObserveSDK] Stopped")
    }
    
    /// Shutdown SDK completely
    public func shutdown() {
        stop()
        
        // Clear all components
        uiObserver = nil
        navigationObserver = nil
        networkObserver = nil
        hierarchyCollector = nil
        webViewObserver = nil
        eventExporter = nil
        eventBus = nil
        
        session = nil
        config = nil
        application = nil
        
        isInitializedFlag = false
        
        print("[ObserveSDK] Shutdown complete")
    }
    
    // MARK: - Getters
    
    public func isInitialized() -> Bool {
        return isInitializedFlag
    }
    
    public func isRunning() -> Bool {
        return isStarted
    }
    
    public func getSession() -> ObserveSession? {
        return session
    }
    
    public func getConfig() -> ObserveConfig? {
        return config
    }
    
    public func getNetworkObserver() -> NetworkObserver? {
        return networkObserver
    }
    
    public func getHierarchyCollector() -> HierarchyCollector? {
        return hierarchyCollector
    }
    
    internal func getUIObserver() -> UIObserver? {
        return uiObserver
    }
    
    // MARK: - WebView Observation
    
    /// Register a WKWebView for observation
    /// Call this when a WKWebView is displayed on screen
    /// - Parameters:
    ///   - webView: The WKWebView instance to observe
    ///   - screenName: Name of the screen containing the WebView
    public func observeWebView(_ webView: WKWebView, screenName: String) {
        guard isInitializedFlag else {
            print("[ObserveSDK] Cannot observe WebView - not initialized")
            return
        }
        
        guard config?.enabled == true else {
            print("[ObserveSDK] Cannot observe WebView - disabled by config")
            return
        }
        
        webViewObserver?.observe(webView: webView, screenName: screenName)
    }
    
    /// Stop observing a WKWebView
    /// Call this when the WebView is removed from screen
    /// - Parameter webView: The WKWebView instance to stop observing
    public func stopObservingWebView(_ webView: WKWebView) {
        webViewObserver?.stopObserving(webView: webView)
    }
    
    // MARK: - Private Methods
    
    private func subscribeToEvents() {
        guard let eventBus = eventBus, let eventExporter = eventExporter else {
            return
        }
        
        // Subscribe to all event types
        eventBus.events
            .sink { [weak eventExporter] event in
                eventExporter?.queueEvent(event)
            }
            .store(in: &cancellables)
    }
    
    private var cancellables = Set<AnyCancellable>()
}

// Import Combine for sink
import Combine

