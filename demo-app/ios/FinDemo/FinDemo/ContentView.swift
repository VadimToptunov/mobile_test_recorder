//
//  ContentView.swift
//  FinDemo
//
//  Main navigation controller
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Group {
            if !appState.isOnboardingComplete {
                OnboardingView()
            } else if !appState.isLoggedIn {
                LoginView()
            } else if !appState.isKYCComplete {
                KYCView()
            } else {
                HomeView()
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}

