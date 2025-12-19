package com.findemo.ui.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class Transaction(
    val id: String,
    val description: String,
    val amount: Double,
    val isDebit: Boolean
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToTopUp: () -> Unit,
    onNavigateToSendMoney: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Mock data
    val balance = 1250.50
    val transactions = listOf(
        Transaction("1", "Coffee Shop", -4.50, true),
        Transaction("2", "Salary Deposit", 2500.00, false),
        Transaction("3", "Grocery Store", -125.30, true),
        Transaction("4", "Friend Transfer", -50.00, true),
    )
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("FinDemo") },
                modifier = Modifier.testTag("home_toolbar")
            )
        },
        modifier = modifier.testTag("home_screen")
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            // Balance Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
                    .testTag("balance_card"),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp)
                ) {
                    Text(
                        text = "Total Balance",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "$${"%.2f".format(balance)}",
                        style = MaterialTheme.typography.displayMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }
            }
            
            // Quick Actions
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Top-up button
                OutlinedButton(
                    onClick = onNavigateToTopUp,
                    modifier = Modifier
                        .weight(1f)
                        .testTag("topup_button")
                ) {
                    Icon(Icons.Default.Add, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Top Up")
                }
                
                // Send money button
                Button(
                    onClick = onNavigateToSendMoney,
                    modifier = Modifier
                        .weight(1f)
                        .testTag("send_money_button")
                ) {
                    Icon(Icons.Default.Send, contentDescription = null)
                    Spacer(Modifier.width(8.dp))
                    Text("Send")
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Transactions section
            Text(
                text = "Recent Transactions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
            )
            
            // Transaction list
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .testTag("transactions_list")
            ) {
                items(transactions) { transaction ->
                    TransactionItem(transaction)
                    Divider()
                }
            }
        }
    }
}

@Composable
fun TransactionItem(transaction: Transaction) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
            .testTag("transaction_item_${transaction.id}"),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = transaction.description,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = "Transaction ID: ${transaction.id}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }
        
        Text(
            text = "${if (transaction.isDebit) "-" else "+"}$${"%.2f".format(transaction.amount)}",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = if (transaction.isDebit) {
                MaterialTheme.colorScheme.error
            } else {
                MaterialTheme.colorScheme.primary
            }
        )
    }
}

