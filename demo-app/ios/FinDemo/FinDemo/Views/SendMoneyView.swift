//
//  SendMoneyView.swift
//  FinDemo
//
//  Send money screen with recipient selection and amount input
//

import SwiftUI

struct SendMoneyView: View {
    @EnvironmentObject var appState: AppState
    @Environment(\.dismiss) var dismiss
    @State private var selectedRecipient: Recipient?
    @State private var amount = ""
    @State private var note = ""
    @State private var showConfirmation = false
    @State private var showSuccess = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    private let recipients = [
        Recipient(name: "John Doe", email: "john@example.com", avatar: "person.circle.fill", color: .blue),
        Recipient(name: "Jane Smith", email: "jane@example.com", avatar: "person.circle.fill", color: .purple),
        Recipient(name: "Bob Johnson", email: "bob@example.com", avatar: "person.circle.fill", color: .green)
    ]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 30) {
                    // Recipient selection
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Select Recipient")
                            .font(.headline)
                            .padding(.horizontal)
                            .accessibilityIdentifier("send_recipient_label")
                        
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 15) {
                                ForEach(recipients) { recipient in
                                    RecipientButton(
                                        recipient: recipient,
                                        isSelected: selectedRecipient?.id == recipient.id,
                                        action: { selectedRecipient = recipient }
                                    )
                                    .accessibilityIdentifier("send_recipient_\(recipient.name.replacingOccurrences(of: " ", with: "_"))")
                                }
                            }
                            .padding(.horizontal)
                        }
                    }
                    .padding(.top, 20)
                    
                    // Amount input
                    VStack(spacing: 20) {
                        Text("Enter Amount")
                            .font(.headline)
                            .accessibilityIdentifier("send_amount_label")
                        
                        // NO ID - test XPath with placeholder and HStack structure
                        HStack {
                            Text("$")
                                .font(.system(size: 48, weight: .bold))
                                .foregroundColor(.secondary)
                            
                            TextField("0.00", text: $amount)
                                .font(.system(size: 48, weight: .bold))
                                .keyboardType(.decimalPad)
                                .multilineTextAlignment(.center)
                        }
                        .padding()
                        .background(Color.secondary.opacity(0.1))
                        .cornerRadius(15)
                        .padding(.horizontal)
                        
                        // Quick amount buttons
                        HStack(spacing: 15) {
                            ForEach([10, 25, 50, 100], id: \.self) { value in
                                Button("$\(value)") {
                                    amount = String(value)
                                }
                                .buttonStyle(.bordered)
                                .accessibilityIdentifier("send_quick_\(value)")
                            }
                        }
                        .accessibilityIdentifier("send_quick_amounts")
                        
                        // Available balance
                        Text("Available: $\(String(format: "%.2f", appState.currentBalance))")
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .accessibilityIdentifier("send_available_balance")
                    }
                    
                    // Note field
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Add a Note (Optional)")
                            .font(.headline)
                            .padding(.horizontal)
                            .accessibilityIdentifier("send_note_label")
                        
                        TextField("What's this for?", text: $note)
                            .textFieldStyle(.roundedBorder)
                            .padding(.horizontal)
                            .accessibilityIdentifier("send_note_field")
                    }
                    
                    Spacer()
                    
                    // Send button
                    Button(action: { showConfirmation = true }) {
                        Text("Review Transfer")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(canSend ? Color.blue : Color.gray)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .disabled(!canSend)
                    .padding(.horizontal)
                    .padding(.bottom, 30)
                    .accessibilityIdentifier("send_review_button")
                }
            }
            .navigationTitle("Send Money")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .accessibilityIdentifier("send_cancel_button")
                }
            }
            .sheet(isPresented: $showConfirmation) {
                ConfirmationView(
                    recipient: selectedRecipient,
                    amount: amount,
                    note: note,
                    onConfirm: sendMoney,
                    onCancel: { showConfirmation = false }
                )
            }
            .alert("Transfer Successful", isPresented: $showSuccess) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text("$\(amount) sent to \(selectedRecipient?.name ?? "")")
            }
            .alert("Transfer Failed", isPresented: $showError) {
                Button("OK") { }
            } message: {
                Text(errorMessage)
            }
        }
    }
    
    private var canSend: Bool {
        guard let recipient = selectedRecipient,
              let amountValue = Double(amount),
              amountValue > 0 else {
            return false
        }
        return true
    }
    
    private func sendMoney() {
        guard let amountValue = Double(amount) else { return }
        
        showConfirmation = false
        
        if appState.sendMoney(amount: amountValue) {
            showSuccess = true
        } else {
            errorMessage = "Insufficient funds"
            showError = true
        }
    }
}

struct Recipient: Identifiable {
    let id = UUID()
    let name: String
    let email: String
    let avatar: String
    let color: Color
}

struct RecipientButton: View {
    let recipient: Recipient
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: recipient.avatar)
                    .font(.system(size: 40))
                    .foregroundColor(.white)
                    .frame(width: 70, height: 70)
                    .background(isSelected ? recipient.color : Color.gray.opacity(0.3))
                    .clipShape(Circle())
                    .overlay(
                        Circle()
                            .stroke(isSelected ? recipient.color : Color.clear, lineWidth: 3)
                    )
                
                Text(recipient.name.components(separatedBy: " ").first ?? "")
                    .font(.caption)
                    .foregroundColor(.primary)
            }
        }
    }
}

struct ConfirmationView: View {
    let recipient: Recipient?
    let amount: String
    let note: String
    let onConfirm: () -> Void
    let onCancel: () -> Void
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                Spacer()
                
                // Recipient info
                if let recipient = recipient {
                    VStack(spacing: 15) {
                        Image(systemName: recipient.avatar)
                            .font(.system(size: 60))
                            .foregroundColor(.white)
                            .frame(width: 100, height: 100)
                            .background(recipient.color)
                            .clipShape(Circle())
                        
                        Text(recipient.name)
                            .font(.title2)
                            .fontWeight(.semibold)
                        
                        Text(recipient.email)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .accessibilityIdentifier("send_confirm_recipient")
                }
                
                // Amount
                VStack(spacing: 10) {
                    Text("Transfer Amount")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    
                    Text("$\(amount)")
                        .font(.system(size: 48, weight: .bold))
                        .accessibilityIdentifier("send_confirm_amount")
                }
                
                // Note
                if !note.isEmpty {
                    VStack(spacing: 5) {
                        Text("Note")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Text(note)
                            .font(.body)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                            .accessibilityIdentifier("send_confirm_note")
                    }
                }
                
                Spacer()
                
                // Confirmation buttons
                VStack(spacing: 15) {
                    Button(action: onConfirm) {
                        Text("Confirm Transfer")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                    .accessibilityIdentifier("send_confirm_button")
                    
                    Button(action: onCancel) {
                        Text("Cancel")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.secondary.opacity(0.2))
                            .foregroundColor(.primary)
                            .cornerRadius(10)
                    }
                    .accessibilityIdentifier("send_confirm_cancel")
                }
                .padding(.horizontal)
                .padding(.bottom, 30)
            }
            .navigationTitle("Confirm Transfer")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    SendMoneyView()
        .environmentObject(AppState())
}

