//
//  LoginView.swift
//  FinDemo
//
//  Login screen with username/password
//

import SwiftUI

struct LoginView: View {
    @EnvironmentObject var appState: AppState
    @State private var username = ""
    @State private var password = ""
    @State private var showError = false
    @State private var showForgotPassword = false
    @State private var showSignUp = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Spacer()
                
                // Logo/Title
                Image(systemName: "building.columns.fill")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 100, height: 100)
                    .foregroundColor(.blue)
                    .accessibilityIdentifier("login_logo")
                
                Text("FinDemo")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .accessibilityIdentifier("login_title")
                
                Spacer()
                
                // Input fields - NO ACCESSIBILITY IDs (test XPath generation)
                VStack(spacing: 15) {
                    TextField("Username", text: $username)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.username)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.password)
                }
                .padding(.horizontal, 40)
                
                if showError {
                    Text("Invalid username or password")
                        .foregroundColor(.red)
                        .font(.caption)
                        .accessibilityIdentifier("login_error_message")
                }
                
                // Login button
                Button(action: login) {
                    Text("Login")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .padding(.horizontal, 40)
                .padding(.top, 20)
                .accessibilityIdentifier("login_button")
                
                // Forgot password link - NO ID (test XPath by text)
                Button("Forgot Password?") {
                    showForgotPassword = true
                }
                .font(.caption)
                .foregroundColor(.blue)
                
                Spacer()
                
                // Sign up link - NO ID (test XPath in HStack)
                HStack {
                    Text("Don't have an account?")
                        .foregroundColor(.secondary)
                    Button("Sign Up") {
                        showSignUp = true
                    }
                    .fontWeight(.semibold)
                }
                .font(.caption)
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
            .alert("Forgot Password", isPresented: $showForgotPassword) {
                Button("OK") { }
            } message: {
                Text("Password reset functionality coming soon!")
            }
            .alert("Sign Up", isPresented: $showSignUp) {
                Button("OK") { }
            } message: {
                Text("Registration functionality coming soon!")
            }
        }
    }
    
    private func login() {
        showError = false
        
        if appState.login(username: username, password: password) {
            // Login successful
        } else {
            showError = true
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AppState())
}

