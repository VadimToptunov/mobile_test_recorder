//
//  HomeView.swift
//  FinDemo
//
//  Main home screen with balance and actions
//

import SwiftUI

struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @State private var showTopUp = false
    @State private var showSendMoney = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 30) {
                    // Balance card
                    VStack(spacing: 10) {
                        Text("Available Balance")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .accessibilityIdentifier("home_balance_label")
                        
                        Text("$\(String(format: "%.2f", appState.currentBalance))")
                            .font(.system(size: 48, weight: .bold))
                            .accessibilityIdentifier("home_balance_value")
                        
                        HStack {
                            Image(systemName: "arrow.up.circle.fill")
                                .foregroundColor(.green)
                            Text("Updated just now")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .accessibilityIdentifier("home_balance_status")
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 40)
                    .background(
                        LinearGradient(
                            colors: [.blue.opacity(0.6), .purple.opacity(0.6)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .foregroundColor(.white)
                    .cornerRadius(20)
                    .padding(.horizontal)
                    
                    // Quick actions
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Quick Actions")
                            .font(.headline)
                            .padding(.horizontal)
                            .accessibilityIdentifier("home_quick_actions_title")
                        
                        HStack(spacing: 15) {
                            QuickActionButton(
                                icon: "plus.circle.fill",
                                title: "Top Up",
                                color: .green,
                                action: { showTopUp = true }
                            )
                            .accessibilityIdentifier("home_topup_button")
                            
                            QuickActionButton(
                                icon: "paperplane.fill",
                                title: "Send",
                                color: .blue,
                                action: { showSendMoney = true }
                            )
                            .accessibilityIdentifier("home_send_button")
                            
                            QuickActionButton(
                                icon: "qrcode.viewfinder",
                                title: "Scan QR",
                                color: .orange,
                                action: { /* TODO */ }
                            )
                            .accessibilityIdentifier("home_scanqr_button")
                        }
                        .padding(.horizontal)
                    }
                    
                    // Recent transactions
                    VStack(alignment: .leading, spacing: 15) {
                        Text("Recent Transactions")
                            .font(.headline)
                            .padding(.horizontal)
                            .accessibilityIdentifier("home_transactions_title")
                        
                        TransactionRow(
                            icon: "cart.fill",
                            title: "Online Purchase",
                            date: "Today",
                            amount: -45.99,
                            color: .red
                        )
                        
                        TransactionRow(
                            icon: "arrow.down.circle.fill",
                            title: "Salary Deposit",
                            date: "Yesterday",
                            amount: 3500.00,
                            color: .green
                        )
                        
                        TransactionRow(
                            icon: "fork.knife",
                            title: "Restaurant",
                            date: "2 days ago",
                            amount: -78.50,
                            color: .orange
                        )
                    }
                    
                    Spacer()
                }
                .padding(.vertical)
            }
            .navigationTitle("Home")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { appState.logout() }) {
                        Image(systemName: "rectangle.portrait.and.arrow.right")
                    }
                    .accessibilityIdentifier("home_logout_button")
                }
            }
            .sheet(isPresented: $showTopUp) {
                TopUpView()
            }
            .sheet(isPresented: $showSendMoney) {
                SendMoneyView()
            }
        }
    }
}

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 10) {
                Image(systemName: icon)
                    .font(.system(size: 30))
                    .foregroundColor(.white)
                    .frame(width: 60, height: 60)
                    .background(color)
                    .clipShape(Circle())
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
        }
        .frame(maxWidth: .infinity)
    }
}

struct TransactionRow: View {
    let icon: String
    let title: String
    let date: String
    let amount: Double
    let color: Color
    
    var body: some View {
        HStack(spacing: 15) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 50, height: 50)
                .background(color.opacity(0.8))
                .clipShape(Circle())
            
            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.body)
                    .fontWeight(.medium)
                
                Text(date)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Text(amount >= 0 ? "+$\(String(format: "%.2f", amount))" : "-$\(String(format: "%.2f", abs(amount)))")
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(amount >= 0 ? .green : .primary)
        }
        .padding()
        .background(Color.secondary.opacity(0.1))
        .cornerRadius(10)
        .padding(.horizontal)
    }
}

#Preview {
    HomeView()
        .environmentObject(AppState())
}

