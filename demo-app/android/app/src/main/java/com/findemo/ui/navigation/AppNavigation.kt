package com.findemo.ui.navigation

import androidx.compose.runtime.*
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.findemo.ui.auth.LoginScreen
import com.findemo.ui.home.HomeScreen
import com.findemo.ui.kyc.KYCScreen
import com.findemo.ui.onboarding.OnboardingScreen
import com.findemo.ui.send.SendMoneyScreen
import com.findemo.ui.topup.TopUpScreen

sealed class Screen(val route: String) {
    object Onboarding : Screen("onboarding")
    object Login : Screen("login")
    object Register : Screen("register")
    object KYC : Screen("kyc")
    object Home : Screen("home")
    object TopUp : Screen("topup")
    object TopUpWebView : Screen("topup_webview")
    object SendMoney : Screen("send_money")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    // Check if onboarding is completed (in real app, use DataStore)
    var onboardingCompleted by remember { mutableStateOf(false) }
    
    val startDestination = if (onboardingCompleted) {
        Screen.Login.route
    } else {
        Screen.Onboarding.route
    }
    
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    onboardingCompleted = true
                    navController.navigate(Screen.Login.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.KYC.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                }
            )
        }
        
        composable(Screen.KYC.route) {
            KYCScreen(
                onKYCComplete = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.KYC.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToTopUp = {
                    navController.navigate(Screen.TopUp.route)
                },
                onNavigateToSendMoney = {
                    navController.navigate(Screen.SendMoney.route)
                }
            )
        }
        
        composable(Screen.TopUp.route) {
            TopUpScreen(
                onNavigateBack = {
                    navController.navigateUp()
                },
                onTopUpSuccess = {
                    // Pop TopUp screen to return to Home (already in backstack)
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.SendMoney.route) {
            SendMoneyScreen(
                onNavigateBack = {
                    navController.navigateUp()
                },
                onSendSuccess = {
                    // Pop SendMoney screen to return to Home (already in backstack)
                    navController.popBackStack()
                }
            )
        }
    }
}

