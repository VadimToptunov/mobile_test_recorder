package com.findemo.ui.onboarding

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.accompanist.pager.*
import kotlinx.coroutines.launch

data class OnboardingPage(
    val title: String,
    val description: String,
    val imageRes: Int
)

@OptIn(ExperimentalPagerApi::class)
@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val pages = listOf(
        OnboardingPage(
            title = "Welcome to FinDemo",
            description = "Your simple digital wallet for easy money management",
            imageRes = android.R.drawable.ic_dialog_info // Placeholder
        ),
        OnboardingPage(
            title = "Send Money Instantly",
            description = "Transfer money to friends and family in seconds",
            imageRes = android.R.drawable.ic_dialog_email // Placeholder
        ),
        OnboardingPage(
            title = "Secure & Easy",
            description = "Bank-level security with simple, intuitive interface",
            imageRes = android.R.drawable.ic_lock_lock // Placeholder
        )
    )
    
    val pagerState = rememberPagerState()
    val scope = rememberCoroutineScope()
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .testTag("onboarding_screen")
    ) {
        // Horizontal Pager
        HorizontalPager(
            count = pages.size,
            state = pagerState,
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .testTag("onboarding_pager")
        ) { page ->
            OnboardingPageContent(pages[page])
        }
        
        // Bottom section with indicators and buttons
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Page indicators
            HorizontalPagerIndicator(
                pagerState = pagerState,
                modifier = Modifier
                    .align(Alignment.CenterHorizontally)
                    .padding(16.dp)
                    .testTag("page_indicators"),
                activeColor = MaterialTheme.colorScheme.primary,
                inactiveColor = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Navigation buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Skip button (visible except on last page)
                if (pagerState.currentPage < pages.size - 1) {
                    TextButton(
                        onClick = onComplete,
                        modifier = Modifier.testTag("skip_button")
                    ) {
                        Text("Skip")
                    }
                } else {
                    Spacer(Modifier.width(80.dp))
                }
                
                // Next/Get Started button
                Button(
                    onClick = {
                        if (pagerState.currentPage < pages.size - 1) {
                            // Go to next page
                            scope.launch {
                                pagerState.animateScrollToPage(pagerState.currentPage + 1)
                            }
                        } else {
                            // Complete onboarding
                            onComplete()
                        }
                    },
                    modifier = Modifier.testTag("next_button")
                ) {
                    Text(
                        if (pagerState.currentPage < pages.size - 1) "Next" else "Get Started"
                    )
                }
            }
        }
    }
}

@Composable
fun OnboardingPageContent(page: OnboardingPage) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Image
        Image(
            painter = painterResource(id = page.imageRes),
            contentDescription = page.title,
            modifier = Modifier
                .size(200.dp)
                .padding(bottom = 32.dp)
        )
        
        // Title
        Text(
            text = page.title,
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        
        // Description
        Text(
            text = page.description,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
        )
    }
}

