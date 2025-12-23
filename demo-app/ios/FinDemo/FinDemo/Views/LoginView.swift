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
                
                // Input fields
                VStack(spacing: 15) {
                    TextField("Username", text: $username)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.username)
                        .autocapitalization(.none)
                        .accessibilityIdentifier("login_username_field")
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.password)
                        .accessibilityIdentifier("login_password_field")
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
                
                // Forgot password link
                Button("Forgot Password?") {
                    // TODO: Implement forgot password
                }
                .font(.caption)
                .foregroundColor(.blue)
                .accessibilityIdentifier("login_forgot_password")
                
                Spacer()
                
                // Sign up link
                HStack {
                    Text("Don't have an account?")
                        .foregroundColor(.secondary)
                    Button("Sign Up") {
                        // TODO: Implement sign up
                    }
                    .fontWeight(.semibold)
                    .accessibilityIdentifier("login_signup_button")
                }
                .font(.caption)
                .padding(.bottom, 20)
            }
            .navigationBarHidden(true)
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

