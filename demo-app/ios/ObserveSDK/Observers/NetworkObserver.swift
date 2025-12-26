//
//  NetworkObserver.swift
//  ObserveSDK
//
//  Observes network requests and responses
//

import Foundation

/// Observes network traffic via URLProtocol
public class NetworkObserver {
    
    // MARK: - Properties
    
    private let eventBus: EventBus
    private var isObserving = false
    
    // MARK: - Initializer
    
    public init(eventBus: EventBus) {
        self.eventBus = eventBus
    }
    
    // MARK: - Public API
    
    /// Start observing network traffic
    public func start() {
        guard !isObserving else {
            print("[NetworkObserver] Already observing")
            return
        }
        
        print("[NetworkObserver] Starting...")
        isObserving = true
        
        // Register custom URLProtocol
        URLProtocol.registerClass(ObserveURLProtocol.self)
        ObserveURLProtocol.eventBus = eventBus
        
        print("[NetworkObserver] Started")
    }
    
    /// Stop observing
    public func stop() {
        guard isObserving else {
            print("[NetworkObserver] Not observing")
            return
        }
        
        print("[NetworkObserver] Stopping...")
        isObserving = false
        
        URLProtocol.unregisterClass(ObserveURLProtocol.self)
        
        print("[NetworkObserver] Stopped")
    }
}

// MARK: - Custom URLProtocol

/// Custom URLProtocol to intercept network requests
class ObserveURLProtocol: URLProtocol {
    
    static var eventBus: EventBus?
    
    private var dataTask: URLSessionDataTask?
    private var requestStartTime: Date?
    private var responseData: Data?
    
    // MARK: - URLProtocol Overrides
    
    override class func canInit(with request: URLRequest) -> Bool {
        // Only intercept if we haven't already processed this request
        guard URLProtocol.property(forKey: "ObserveURLProtocolHandled", in: request) == nil else {
            return false
        }
        return true
    }
    
    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        return request
    }
    
    override func startLoading() {
        guard let newRequest = (request as NSURLRequest).mutableCopy() as? NSMutableURLRequest else {
            return
        }
        
        // Mark request as handled
        URLProtocol.setProperty(true, forKey: "ObserveURLProtocolHandled", in: newRequest)
        
        // Generate correlation ID
        let correlationId = UUID().uuidString
        newRequest.setValue(correlationId, forHTTPHeaderField: "X-Observe-Correlation-ID")
        
        // Capture request start time
        requestStartTime = Date()
        
        // Create session and data task
        let session = URLSession(configuration: .default)
        dataTask = session.dataTask(with: newRequest as URLRequest) { [weak self] data, response, error in
            guard let self = self else { return }
            
            if let error = error {
                self.client?.urlProtocol(self, didFailWithError: error)
                self.captureNetworkEvent(
                    request: newRequest as URLRequest,
                    correlationId: correlationId,
                    response: nil,
                    data: nil,
                    error: error
                )
            } else {
                if let response = response {
                    self.client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .allowed)
                }
                
                if let data = data {
                    self.responseData = data
                    self.client?.urlProtocol(self, didLoad: data)
                }
                
                self.client?.urlProtocolDidFinishLoading(self)
                self.captureNetworkEvent(
                    request: newRequest as URLRequest,
                    correlationId: correlationId,
                    response: response as? HTTPURLResponse,
                    data: data,
                    error: nil
                )
            }
        }
        
        dataTask?.resume()
    }
    
    override func stopLoading() {
        dataTask?.cancel()
    }
    
    // MARK: - Event Capture
    
    private func captureNetworkEvent(
        request: URLRequest,
        correlationId: String,
        response: HTTPURLResponse?,
        data: Data?,
        error: Error?
    ) {
        guard let eventBus = Self.eventBus else { return }
        
        let timestamp = Int64(Date().timeIntervalSince1970 * 1000)
        let sessionId = ObserveSDK.shared.getSession()?.sessionId ?? "unknown"
        
        let duration: Int64?
        if let startTime = requestStartTime {
            duration = Int64(Date().timeIntervalSince(startTime) * 1000)
        } else {
            duration = nil
        }
        
        let requestBody: String?
        if let bodyData = request.httpBody {
            requestBody = String(data: bodyData, encoding: .utf8)
        } else {
            requestBody = nil
        }
        
        let responseBody: String?
        if let responseData = data {
            responseBody = String(data: responseData, encoding: .utf8)
        } else {
            responseBody = nil
        }
        
        let event = NetworkEvent(
            timestamp: timestamp,
            sessionId: sessionId,
            correlationId: correlationId,
            url: request.url?.absoluteString ?? "",
            method: request.httpMethod ?? "GET",
            requestHeaders: request.allHTTPHeaderFields,
            requestBody: requestBody,
            responseCode: response?.statusCode,
            responseHeaders: response?.allHeaderFields as? [String: String],
            responseBody: responseBody,
            duration: duration,
            error: error?.localizedDescription
        )
        
        eventBus.publish(event)
        print("[NetworkObserver] \(request.httpMethod ?? "GET") \(request.url?.path ?? "") → \(response?.statusCode ?? 0)")
    }
}

