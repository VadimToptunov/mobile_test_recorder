//
//  NavigationObserver.swift
//  ObserveSDK
//
//  Observes navigation events and screen transitions
//

import Foundation
import UIKit
import SwiftUI

/// Observes screen navigation and transitions
public class NavigationObserver {
    
    // MARK: - Properties
    
    private let eventBus: EventBus
    private var isObserving = false
    private var currentScreen: String = "Unknown"
    private var previousScreen: String = "Unknown"
    
    // MARK: - Initializer
    
    public init(eventBus: EventBus) {
        self.eventBus = eventBus
    }
    
    // MARK: - Public API
    
    /// Start observing navigation
    public func start() {
        guard !isObserving else {
            print("[NavigationObserver] Already observing")
            return
        }
        
        print("[NavigationObserver] Starting...")
        isObserving = true
        
        // Register for view controller lifecycle notifications
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(viewControllerDidAppear(_:)),
            name: NSNotification.Name("UIViewControllerDidAppear"),
            object: nil
        )
        
        print("[NavigationObserver] Started")
    }
    
    /// Stop observing
    public func stop() {
        guard isObserving else {
            print("[NavigationObserver] Not observing")
            return
        }
        
        print("[NavigationObserver] Stopping...")
        isObserving = false
        
        NotificationCenter.default.removeObserver(self)
        
        print("[NavigationObserver] Stopped")
    }
    
    /// Track navigation to a new screen
    /// - Parameter screenName: Name of the screen
    public func trackNavigation(to screenName: String) {
        guard isObserving else { return }
        
        let timestamp = Int64(Date().timeIntervalSince1970 * 1000)
        let sessionId = ObserveSDK.shared.getSession()?.sessionId ?? "unknown"
        
        let event = NavigationEvent(
            timestamp: timestamp,
            sessionId: sessionId,
            from: previousScreen,
            to: screenName,
            type: "navigate",
            metadata: nil
        )
        
        eventBus.publish(event)
        print("[NavigationObserver] Navigation: \(previousScreen) → \(screenName)")
        
        previousScreen = currentScreen
        currentScreen = screenName
    }
    
    // MARK: - Private Methods
    
    @objc private func viewControllerDidAppear(_ notification: Notification) {
        guard let viewController = notification.object as? UIViewController else {
            return
        }
        
        let screenName = String(describing: type(of: viewController))
        trackNavigation(to: screenName)
    }
}

