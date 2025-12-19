package com.findemo.ui.send

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SendMoneyScreen(
    onNavigateBack: () -> Unit,
    onSendSuccess: () -> Unit,
    modifier: Modifier = Modifier
) {
    var currentStep by remember { mutableStateOf(SendMoneyStep.RECIPIENT_SELECT) }
    var recipientName by remember { mutableStateOf("") }
    var recipientId by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Send Money") },
                navigationIcon = {
                    IconButton(
                        onClick = onNavigateBack,
                        modifier = Modifier.testTag("back_button")
                    ) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (currentStep) {
                SendMoneyStep.RECIPIENT_SELECT -> {
                    RecipientSelectStep(
                        recipientName = recipientName,
                        onRecipientNameChange = { recipientName = it },
                        recipientId = recipientId,
                        onRecipientIdChange = { recipientId = it },
                        onContinue = {
                            if (recipientName.isNotBlank()) {
                                currentStep = SendMoneyStep.AMOUNT_INPUT
                            }
                        }
                    )
                }
                SendMoneyStep.AMOUNT_INPUT -> {
                    AmountInputStep(
                        amount = amount,
                        onAmountChange = { amount = it },
                        note = note,
                        onNoteChange = { note = it },
                        onContinue = {
                            if (amount.isNotBlank()) {
                                currentStep = SendMoneyStep.CONFIRMATION
                            }
                        },
                        onBack = {
                            currentStep = SendMoneyStep.RECIPIENT_SELECT
                        }
                    )
                }
                SendMoneyStep.CONFIRMATION -> {
                    ConfirmationStep(
                        recipientName = recipientName,
                        amount = amount,
                        note = note,
                        onConfirm = {
                            currentStep = SendMoneyStep.SUCCESS
                        },
                        onBack = {
                            currentStep = SendMoneyStep.AMOUNT_INPUT
                        }
                    )
                }
                SendMoneyStep.SUCCESS -> {
                    SuccessStep(
                        recipientName = recipientName,
                        amount = amount,
                        onDone = onSendSuccess
                    )
                }
            }
        }
    }
}

@Composable
private fun RecipientSelectStep(
    recipientName: String,
    onRecipientNameChange: (String) -> Unit,
    recipientId: String,
    onRecipientIdChange: (String) -> Unit,
    onContinue: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("recipient_select_step"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Person,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Who do you want to send money to?",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = recipientName,
            onValueChange = onRecipientNameChange,
            label = { Text("Recipient Name") },
            placeholder = { Text("John Doe") },
            leadingIcon = {
                Icon(Icons.Default.Person, contentDescription = null)
            },
            modifier = Modifier
                .fillMaxWidth()
                .testTag("recipient_name_input"),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = recipientId,
            onValueChange = onRecipientIdChange,
            label = { Text("Phone or Email") },
            placeholder = { Text("+1234567890 or email@example.com") },
            leadingIcon = {
                Icon(Icons.Default.Email, contentDescription = null)
            },
            modifier = Modifier
                .fillMaxWidth()
                .testTag("recipient_id_input"),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Quick select contacts (mock)
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            )
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Recent",
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(8.dp))
                
                RecentRecipientItem(
                    name = "Alice Johnson",
                    identifier = "+1234567890",
                    onClick = {
                        onRecipientNameChange("Alice Johnson")
                        onRecipientIdChange("+1234567890")
                    }
                )
                
                RecentRecipientItem(
                    name = "Bob Smith",
                    identifier = "bob@example.com",
                    onClick = {
                        onRecipientNameChange("Bob Smith")
                        onRecipientIdChange("bob@example.com")
                    }
                )
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = onContinue,
            enabled = recipientName.isNotBlank(),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
                .testTag("continue_button")
        ) {
            Text("Continue")
        }
    }
}

@Composable
private fun RecentRecipientItem(
    name: String,
    identifier: String,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .testTag("recent_recipient_$name")
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(horizontalAlignment = Alignment.Start) {
                Text(text = name, fontWeight = FontWeight.Medium)
                Text(
                    text = identifier,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                )
            }
            Icon(
                imageVector = Icons.Default.KeyboardArrowRight,
                contentDescription = null
            )
        }
    }
}

@Composable
private fun AmountInputStep(
    amount: String,
    onAmountChange: (String) -> Unit,
    note: String,
    onNoteChange: (String) -> Unit,
    onContinue: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("amount_input_step"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Send,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "How much?",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = amount,
            onValueChange = onAmountChange,
            label = { Text("Amount") },
            placeholder = { Text("0.00") },
            prefix = { Text("$") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            modifier = Modifier
                .fillMaxWidth()
                .testTag("amount_input"),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = note,
            onValueChange = onNoteChange,
            label = { Text("Note (optional)") },
            placeholder = { Text("What's this for?") },
            modifier = Modifier
                .fillMaxWidth()
                .testTag("note_input"),
            maxLines = 3
        )

        Spacer(modifier = Modifier.height(32.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedButton(
                onClick = onBack,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp)
                    .testTag("back_button_step")
            ) {
                Text("Back")
            }

            Button(
                onClick = onContinue,
                enabled = amount.isNotBlank() && amount.toDoubleOrNull() != null && amount.toDouble() > 0,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp)
                    .testTag("continue_button")
            ) {
                Text("Review")
            }
        }
    }
}

@Composable
private fun ConfirmationStep(
    recipientName: String,
    amount: String,
    note: String,
    onConfirm: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("confirmation_step"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Review Transfer",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(32.dp))

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "$$amount",
                    style = MaterialTheme.typography.displayMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "to",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                )

                Spacer(modifier = Modifier.height(8.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = recipientName,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                }

                if (note.isNotBlank()) {
                    Spacer(modifier = Modifier.height(16.dp))
                    Divider(color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.2f))
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Note: $note",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedButton(
                onClick = onBack,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp)
                    .testTag("back_button_step")
            ) {
                Text("Back")
            }

            Button(
                onClick = onConfirm,
                modifier = Modifier
                    .weight(1f)
                    .height(56.dp)
                    .testTag("confirm_button")
            ) {
                Text("Send Money")
            }
        }
    }
}

@Composable
private fun SuccessStep(
    recipientName: String,
    amount: String,
    onDone: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .testTag("success_step"),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.CheckCircle,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Money Sent!",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "$$amount sent to $recipientName",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )

        Spacer(modifier = Modifier.height(48.dp))

        Button(
            onClick = onDone,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
                .testTag("done_button")
        ) {
            Text("Done")
        }
    }
}

private enum class SendMoneyStep {
    RECIPIENT_SELECT,
    AMOUNT_INPUT,
    CONFIRMATION,
    SUCCESS
}

