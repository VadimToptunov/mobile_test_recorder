//
//  FinDemoApp.swift
//  FinDemo
//
//  iOS Demo App for Mobile Test Recorder
//

import SwiftUI

@main
struct FinDemoApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var isOnboardingComplete = false
    @Published var isLoggedIn = false
    @Published var isKYCComplete = false
    @Published var currentBalance: Double = 1000.0
    @Published var username: String = ""
    
    func login(username: String, password: String) -> Bool {
        // Mock login
        if !username.isEmpty && !password.isEmpty {
            self.username = username
            self.isLoggedIn = true
            return true
        }
        return false
    }
    
    func logout() {
        isLoggedIn = false
        username = ""
    }
    
    func completeKYC() {
        isKYCComplete = true
    }
    
    func topUp(amount: Double) {
        currentBalance += amount
    }
    
    func sendMoney(amount: Double) -> Bool {
        if currentBalance >= amount {
            currentBalance -= amount
            return true
        }
        return false
    }
}

