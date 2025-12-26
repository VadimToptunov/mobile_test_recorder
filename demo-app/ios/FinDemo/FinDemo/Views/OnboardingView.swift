//
//  OnboardingView.swift
//  FinDemo
//
//  Swipeable onboarding screens
//

import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var appState: AppState
    @State private var currentPage = 0
    
    private let pages = [
        OnboardingPage(
            title: "Welcome to FinDemo",
            description: "Your digital banking solution for modern finance",
            imageName: "dollarsign.circle.fill",
            color: .blue
        ),
        OnboardingPage(
            title: "Secure Transactions",
            description: "Send and receive money with bank-level security",
            imageName: "lock.shield.fill",
            color: .green
        ),
        OnboardingPage(
            title: "Easy Top-Up",
            description: "Add funds instantly with multiple payment methods",
            imageName: "creditcard.fill",
            color: .purple
        )
    ]
    
    var body: some View {
        VStack {
            TabView(selection: $currentPage) {
                ForEach(0..<pages.count, id: \.self) { index in
                    OnboardingPageView(page: pages[index])
                        .tag(index)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .indexViewStyle(.page(backgroundDisplayMode: .always))
            
            // Navigation buttons
            HStack {
                if currentPage > 0 {
                    Button("Previous") {
                        withAnimation {
                            currentPage -= 1
                        }
                    }
                    .accessibilityIdentifier("onboarding_previous_button")
                }
                
                Spacer()
                
                if currentPage < pages.count - 1 {
                    Button("Next") {
                        withAnimation {
                            currentPage += 1
                        }
                    }
                    .accessibilityIdentifier("onboarding_next_button")
                } else {
                    Button("Get Started") {
                        appState.isOnboardingComplete = true
                    }
                    .accessibilityIdentifier("onboarding_get_started_button")
                }
            }
            .padding()
        }
    }
}

struct OnboardingPage {
    let title: String
    let description: String
    let imageName: String
    let color: Color
}

struct OnboardingPageView: View {
    let page: OnboardingPage
    
    var body: some View {
        VStack(spacing: 30) {
            Spacer()
            
            Image(systemName: page.imageName)
                .resizable()
                .scaledToFit()
                .frame(width: 150, height: 150)
                .foregroundColor(page.color)
                .accessibilityIdentifier("onboarding_image")
            
            Text(page.title)
                .font(.largeTitle)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
                .accessibilityIdentifier("onboarding_title")
            
            Text(page.description)
                .font(.body)
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal, 40)
                .accessibilityIdentifier("onboarding_description")
            
            Spacer()
        }
        .padding()
    }
}

#Preview {
    OnboardingView()
        .environmentObject(AppState())
}

