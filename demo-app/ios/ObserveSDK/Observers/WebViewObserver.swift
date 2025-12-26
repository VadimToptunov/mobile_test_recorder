//
//  WebViewObserver.swift
//  ObserveSDK
//
//  Observes WKWebView interactions and DOM elements
//

import Foundation
import WebKit

/// Observes WKWebView interactions and DOM elements
///
/// Captures:
/// - Page loads
/// - DOM element clicks
/// - Form inputs
/// - Form submissions
/// - Navigation events
/// - Element hierarchy (similar to native)
public class WebViewObserver: NSObject {
    
    private let eventBus: EventBus
    private var isStarted = false
    private var observedWebViews: Set<WKWebView> = []
    
    // JavaScript injection script
    private static let injectionScript = """
        (function() {
            console.log('[ObserveSDK] Injecting WebView observer...');
            
            // Capture click events
            document.addEventListener('click', function(e) {
                var target = e.target;
                var data = {
                    eventType: 'click',
                    tag: target.tagName.toLowerCase(),
                    id: target.id || null,
                    className: target.className || null,
                    text: target.innerText ? target.innerText.substring(0, 100) : null,
                    value: target.value || null,
                    name: target.name || null,
                    href: target.href || null,
                    type: target.type || null,
                    x: e.clientX,
                    y: e.clientY,
                    xpath: getXPath(target),
                    cssSelector: getCSSSelector(target),
                    innerHTML: target.innerHTML ? target.innerHTML.substring(0, 200) : null
                };
                
                try {
                    window.webkit.messageHandlers.observeSDK.postMessage({
                        type: 'interaction',
                        data: data
                    });
                } catch(e) {
                    console.error('[ObserveSDK] Error sending click event:', e);
                }
            }, true);
            
            // Capture input events
            document.addEventListener('input', function(e) {
                var target = e.target;
                if (target.tagName.toLowerCase() === 'input' || 
                    target.tagName.toLowerCase() === 'textarea') {
                    var data = {
                        eventType: 'input',
                        tag: target.tagName.toLowerCase(),
                        id: target.id || null,
                        className: target.className || null,
                        name: target.name || null,
                        type: target.type || null,
                        value: target.value ? '***' : null, // Masked for security
                        xpath: getXPath(target),
                        cssSelector: getCSSSelector(target)
                    };
                    
                    try {
                        window.webkit.messageHandlers.observeSDK.postMessage({
                            type: 'interaction',
                            data: data
                        });
                    } catch(e) {
                        console.error('[ObserveSDK] Error sending input event:', e);
                    }
                }
            }, true);
            
            // Capture form submissions
            document.addEventListener('submit', function(e) {
                var form = e.target;
                var data = {
                    eventType: 'submit',
                    tag: 'form',
                    id: form.id || null,
                    className: form.className || null,
                    action: form.action || null,
                    method: form.method || null,
                    xpath: getXPath(form),
                    cssSelector: getCSSSelector(form)
                };
                
                try {
                    window.webkit.messageHandlers.observeSDK.postMessage({
                        type: 'interaction',
                        data: data
                    });
                } catch(e) {
                    console.error('[ObserveSDK] Error sending submit event:', e);
                }
            }, true);
            
            // Helper: Get XPath of element
            function getXPath(element) {
                if (element.id) {
                    return '//*[@id="' + element.id + '"]';
                }
                
                if (element === document.body) {
                    return '/html/body';
                }
                
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element) {
                        var parentPath = getXPath(element.parentNode);
                        return parentPath + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
            }
            
            // Helper: Get CSS Selector of element
            function getCSSSelector(element) {
                if (element.id) {
                    return '#' + element.id;
                }
                
                if (element.className) {
                    var classes = element.className.split(/\\s+/).filter(c => c.length > 0);
                    if (classes.length > 0) {
                        return element.tagName.toLowerCase() + '.' + classes.join('.');
                    }
                }
                
                return element.tagName.toLowerCase();
            }
            
            // Capture page hierarchy (like HierarchyCollector)
            function captureHierarchy() {
                var elements = [];
                
                function traverse(node, depth) {
                    if (depth > 10) return; // Max depth
                    
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        var rect = node.getBoundingClientRect();
                        
                        elements.push({
                            tag: node.tagName.toLowerCase(),
                            id: node.id || null,
                            className: node.className || null,
                            text: node.innerText ? node.innerText.substring(0, 100) : null,
                            value: node.value || null,
                            name: node.name || null,
                            type: node.type || null,
                            href: node.href || null,
                            clickable: node.onclick != null || node.tagName === 'A' || node.tagName === 'BUTTON',
                            depth: depth,
                            bounds: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            },
                            xpath: getXPath(node),
                            cssSelector: getCSSSelector(node)
                        });
                    }
                    
                    for (var i = 0; i < node.childNodes.length; i++) {
                        traverse(node.childNodes[i], depth + 1);
                    }
                }
                
                traverse(document.body, 0);
                
                return {
                    url: window.location.href,
                    title: document.title,
                    totalElements: elements.length,
                    elements: elements
                };
            }
            
            // Notify SDK that page loaded
            document.addEventListener('DOMContentLoaded', function() {
                try {
                    var hierarchy = captureHierarchy();
                    window.webkit.messageHandlers.observeSDK.postMessage({
                        type: 'pageLoad',
                        url: window.location.href,
                        hierarchy: hierarchy
                    });
                } catch(e) {
                    console.error('[ObserveSDK] Error capturing hierarchy:', e);
                }
            });
            
            // If DOM already loaded
            if (document.readyState === 'complete' || document.readyState === 'interactive') {
                try {
                    var hierarchy = captureHierarchy();
                    window.webkit.messageHandlers.observeSDK.postMessage({
                        type: 'pageLoad',
                        url: window.location.href,
                        hierarchy: hierarchy
                    });
                } catch(e) {
                    console.error('[ObserveSDK] Error capturing hierarchy:', e);
                }
            }
            
            console.log('[ObserveSDK] WebView observer injected successfully');
        })();
    """
    
    public init(eventBus: EventBus) {
        self.eventBus = eventBus
        super.init()
    }
    
    public func start() {
        guard !isStarted else {
            print("[WebViewObserver] Already started")
            return
        }
        
        isStarted = true
        print("[WebViewObserver] Started")
    }
    
    public func stop() {
        guard isStarted else { return }
        
        isStarted = false
        observedWebViews.removeAll()
        
        print("[WebViewObserver] Stopped")
    }
    
    /// Register a WKWebView for observation
    /// Call this when WKWebView is created
    public func observe(webView: WKWebView, screenName: String) {
        guard isStarted else {
            print("[WebViewObserver] Not started, cannot observe WebView")
            return
        }
        
        guard !observedWebViews.contains(webView) else {
            print("[WebViewObserver] WebView already observed")
            return
        }
        
        observedWebViews.insert(webView)
        
        // Create message handler
        let handler = WebViewMessageHandler(
            screenName: screenName,
            eventBus: eventBus,
            currentURL: { webView.url?.absoluteString ?? "" }
        )
        
        // Add message handler to configuration
        webView.configuration.userContentController.add(handler, name: "observeSDK")
        
        // Inject observer script
        let script = WKUserScript(
            source: Self.injectionScript,
            injectionTime: .atDocumentEnd,
            forMainFrameOnly: false
        )
        webView.configuration.userContentController.addUserScript(script)
        
        // Store original navigation delegate
        let originalDelegate = webView.navigationDelegate
        
        // Create delegating navigation delegate
        let navigationDelegate = WebViewNavigationDelegate(
            screenName: screenName,
            eventBus: eventBus,
            originalDelegate: originalDelegate
        )
        webView.navigationDelegate = navigationDelegate
        
        // Store delegates to prevent deallocation
        objc_setAssociatedObject(
            webView,
            &AssociatedKeys.messageHandler,
            handler,
            .OBJC_ASSOCIATION_RETAIN_NONATOMIC
        )
        objc_setAssociatedObject(
            webView,
            &AssociatedKeys.navigationDelegate,
            navigationDelegate,
            .OBJC_ASSOCIATION_RETAIN_NONATOMIC
        )
        objc_setAssociatedObject(
            webView,
            &AssociatedKeys.originalNavigationDelegate,
            originalDelegate,
            .OBJC_ASSOCIATION_RETAIN_NONATOMIC
        )
        
        print("[WebViewObserver] WebView observation enabled for screen: \(screenName)")
    }
    
    /// Unregister a WKWebView from observation
    public func stopObserving(webView: WKWebView) {
        observedWebViews.remove(webView)
        
        // Remove message handler
        webView.configuration.userContentController.removeScriptMessageHandler(forName: "observeSDK")
        
        // Remove all user scripts to prevent duplicate injection
        webView.configuration.userContentController.removeAllUserScripts()
        
        // Restore original navigation delegate
        let originalDelegate = objc_getAssociatedObject(
            webView,
            &AssociatedKeys.originalNavigationDelegate
        ) as? WKNavigationDelegate
        webView.navigationDelegate = originalDelegate
        
        // Clear associated objects
        objc_setAssociatedObject(webView, &AssociatedKeys.messageHandler, nil, .OBJC_ASSOCIATION_RETAIN_NONATOMIC)
        objc_setAssociatedObject(webView, &AssociatedKeys.navigationDelegate, nil, .OBJC_ASSOCIATION_RETAIN_NONATOMIC)
        objc_setAssociatedObject(webView, &AssociatedKeys.originalNavigationDelegate, nil, .OBJC_ASSOCIATION_RETAIN_NONATOMIC)
        
        print("[WebViewObserver] WebView observation disabled - all resources cleaned up")
    }
}

// MARK: - Associated Keys

private struct AssociatedKeys {
    static var messageHandler = "messageHandler"
    static var navigationDelegate = "navigationDelegate"
    static var originalNavigationDelegate = "originalNavigationDelegate"
}

// MARK: - Message Handler

private class WebViewMessageHandler: NSObject, WKScriptMessageHandler {
    
    private let screenName: String
    private let eventBus: EventBus
    private let currentURL: () -> String
    
    init(screenName: String, eventBus: EventBus, currentURL: @escaping () -> String) {
        self.screenName = screenName
        self.eventBus = eventBus
        self.currentURL = currentURL
    }
    
    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any],
              let type = body["type"] as? String else {
            print("[WebViewObserver] Invalid message format")
            return
        }
        
        switch type {
        case "interaction":
            handleInteraction(body: body)
        case "pageLoad":
            handlePageLoad(body: body)
        default:
            print("[WebViewObserver] Unknown message type: \(type)")
        }
    }
    
    private func handleInteraction(body: [String: Any]) {
        guard let data = body["data"] as? [String: Any],
              let eventType = data["eventType"] as? String else {
            return
        }
        
        var attributes: [String: String] = [:]
        if let id = data["id"] as? String, !id.isEmpty {
            attributes["id"] = id
        }
        if let className = data["className"] as? String, !className.isEmpty {
            attributes["class"] = className
        }
        if let name = data["name"] as? String, !name.isEmpty {
            attributes["name"] = name
        }
        if let type = data["type"] as? String, !type.isEmpty {
            attributes["type"] = type
        }
        if let href = data["href"] as? String, !href.isEmpty {
            attributes["href"] = href
        }
        
        let event = WebViewEvent(
            timestamp: Int64(Date().timeIntervalSince1970 * 1000),
            sessionId: ObserveSDK.shared.session?.id ?? "",
            screen: screenName,
            url: currentURL(),
            action: eventType,
            elementSelector: data["cssSelector"] as? String,
            elementTag: data["tag"] as? String,
            elementText: data["text"] as? String,
            elementValue: data["value"] as? String,
            elementAttributes: attributes.isEmpty ? nil : attributes,
            x: data["x"] as? Double,
            y: data["y"] as? Double,
            innerHTML: data["innerHTML"] as? String
        )
        
        eventBus.publish(event: event)
    }
    
    private func handlePageLoad(body: [String: Any]) {
        guard let url = body["url"] as? String,
              let hierarchyDict = body["hierarchy"] as? [String: Any] else {
            return
        }
        
        // Convert hierarchy to JSON string
        if let hierarchyData = try? JSONSerialization.data(withJSONObject: hierarchyDict, options: []),
           let hierarchyJSON = String(data: hierarchyData, encoding: .utf8) {
            
            let event = HierarchyEvent(
                timestamp: Int64(Date().timeIntervalSince1970 * 1000),
                sessionId: ObserveSDK.shared.session?.id ?? "",
                screen: "\(screenName) (WebView)",
                hierarchy: hierarchyJSON
            )
            
            eventBus.publish(event: event)
        }
        
        // Emit page load event
        let pageLoadEvent = WebViewEvent(
            timestamp: Int64(Date().timeIntervalSince1970 * 1000),
            sessionId: ObserveSDK.shared.session?.id ?? "",
            screen: screenName,
            url: url,
            action: "page_load"
        )
        
        eventBus.publish(event: pageLoadEvent)
    }
}

// MARK: - Navigation Delegate

private class WebViewNavigationDelegate: NSObject, WKNavigationDelegate {
    
    private let screenName: String
    private let eventBus: EventBus
    private weak var originalDelegate: WKNavigationDelegate?
    
    init(screenName: String, eventBus: EventBus, originalDelegate: WKNavigationDelegate?) {
        self.screenName = screenName
        self.eventBus = eventBus
        self.originalDelegate = originalDelegate
    }
    
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // Call original delegate first
        originalDelegate?.webView?(webView, didFinish: navigation)
        
        // Then add SDK logic
        guard let url = webView.url?.absoluteString else { return }
        
        print("[WebViewObserver] Page finished loading: \(url)")
        
        let event = WebViewEvent(
            timestamp: Int64(Date().timeIntervalSince1970 * 1000),
            sessionId: ObserveSDK.shared.session?.id ?? "",
            screen: screenName,
            url: url,
            action: "page_finished"
        )
        
        eventBus.publish(event: event)
    }
    
    // Delegate decidePolicyFor to original delegate
    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let originalDelegate = originalDelegate {
            originalDelegate.webView?(webView, decidePolicyFor: navigationAction, decisionHandler: decisionHandler)
        } else {
            decisionHandler(.allow)
        }
    }
    
    // Delegate all other navigation methods
    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        originalDelegate?.webView?(webView, didStartProvisionalNavigation: navigation)
    }
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        originalDelegate?.webView?(webView, didFail: navigation, withError: error)
    }
    
    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        originalDelegate?.webView?(webView, didFailProvisionalNavigation: navigation, withError: error)
    }
}

