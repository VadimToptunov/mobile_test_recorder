//
//  KYCView.swift
//  FinDemo
//
//  KYC (Know Your Customer) screen with document verification
//

import SwiftUI

struct KYCView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedDocumentType = "Passport"
    @State private var showCamera = false
    @State private var documentScanned = false
    
    private let documentTypes = ["Passport", "Driver's License", "ID Card"]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Header
                Text("Verify Your Identity")
                    .font(.title)
                    .fontWeight(.bold)
                    .accessibilityIdentifier("kyc_title")
                
                Text("We need to verify your identity to comply with regulations")
                    .font(.body)
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
                    .accessibilityIdentifier("kyc_description")
                
                Spacer()
                
                // Document type selector
                VStack(alignment: .leading, spacing: 10) {
                    Text("Select Document Type")
                        .font(.headline)
                        .accessibilityIdentifier("kyc_document_type_label")
                    
                    Picker("Document Type", selection: $selectedDocumentType) {
                        ForEach(documentTypes, id: \.self) { type in
                            Text(type)
                        }
                    }
                    .pickerStyle(.segmented)
                    .accessibilityIdentifier("kyc_document_type_picker")
                }
                .padding(.horizontal)
                
                // Document scanning section
                VStack(spacing: 20) {
                    Image(systemName: documentScanned ? "checkmark.circle.fill" : "doc.text.viewfinder")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 100, height: 100)
                        .foregroundColor(documentScanned ? .green : .blue)
                        .accessibilityIdentifier("kyc_document_icon")
                    
                    if documentScanned {
                        Text("Document Verified ✓")
                            .font(.headline)
                            .foregroundColor(.green)
                            .accessibilityIdentifier("kyc_verification_status")
                    } else {
                        Text("Tap to scan your \(selectedDocumentType.lowercased())")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .accessibilityIdentifier("kyc_scan_instruction")
                    }
                    
                    Button(action: scanDocument) {
                        HStack {
                            Image(systemName: "camera.fill")
                            Text(documentScanned ? "Scan Again" : "Scan Document")
                        }
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                    .padding(.horizontal, 40)
                    .accessibilityIdentifier("kyc_scan_button")
                }
                
                Spacer()
                
                // Continue button
                if documentScanned {
                    Button(action: completeKYC) {
                        Text("Continue")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal, 40)
                    .accessibilityIdentifier("kyc_continue_button")
                }
                
                // Skip button (for demo purposes)
                Button("Skip for now") {
                    completeKYC()
                }
                .font(.caption)
                .foregroundColor(.secondary)
                .padding(.bottom, 20)
                .accessibilityIdentifier("kyc_skip_button")
            }
            .navigationBarHidden(true)
        }
    }
    
    private func scanDocument() {
        // Mock document scanning
        // In production, this would integrate with Regula SDK
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation {
                documentScanned = true
            }
        }
    }
    
    private func completeKYC() {
        appState.completeKYC()
    }
}

#Preview {
    KYCView()
        .environmentObject(AppState())
}

