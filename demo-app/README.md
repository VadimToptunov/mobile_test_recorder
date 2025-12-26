#  Demo FinTech Application

Simplified fintech application to demonstrate Mobile Observe & Test Framework capabilities.

---

##  Features

### Core Flows:
1. **Onboarding** (Swipeable screens)
   - Welcome screen
   - Features showcase
   - Get Started

2. **Authentication**
   - Login
   - Registration
   - Forgot password

3. **Wallet**
   - Balance display
   - Transaction history
   - Quick actions

4. **Top-up** (with WebView)
   - Enter amount
   - Card details
   - WebView payment gateway
   - Success/Failure handling

5. **Send Money**
   - Select recipient
   - Enter amount
   - Confirmation
   - Transaction receipt

---

##  Architecture

### Tech Stack:
- **Kotlin** - Primary language
- **Jetpack Compose** - Modern UI
- **Navigation Component** - Navigation
- **ViewModel + StateFlow** - State management
- **Retrofit** - API client
- **Room** - Local database
- **OkHttp** - Network layer
- **Hilt** - Dependency injection (optional)

### Build Variants:
```
observe  - Instrumented build with Observe SDK
test     - Clean build for automated testing
prod     - Production build (future)
```

---

##  Getting Started

### Prerequisites:
- Android Studio Hedgehog+ (2023.1.1+)
- JDK 17
- Android SDK 34
- Gradle 8.2+

### Build & Run:

```bash
# Clone and navigate
cd demo-app/android

# Build observe variant
./gradlew assembleObserveDebug

# Install on device
adb install app/build/outputs/apk/observe/debug/app-observe-debug.apk

# Or run directly from Android Studio
# Select "observe" build variant
# Click Run
```

---

##  Project Structure

```
android/
 app/
    src/
       main/              # Shared code
          java/
             com/findemo/
                 ui/
                    onboarding/
                    auth/
                    home/
                    topup/
                    send/
                 data/
                 domain/
          res/
      
       observe/           # Observe build specific
          java/
              ObserveInitializer.kt
      
       test/              # Test build specific
           java/
   
    build.gradle.kts

 observe-sdk/               # Observe SDK module
     src/
        main/
            java/
                com/observe/sdk/
                    core/
                    observers/
                    export/
     build.gradle.kts
```

---

##  Screens Overview

### 1. Onboarding (ViewPager)
```kotlin
OnboardingScreen
 Page 1: Welcome
 Page 2: Features
 Page 3: Get Started
     → LoginScreen
```

### 2. Authentication
```kotlin
LoginScreen
 Username input
 Password input
 Login button → HomeScreen
 Register link → RegisterScreen

RegisterScreen
 Email input
 Password input
 Confirm password
 Register button → HomeScreen
```

### 3. Home
```kotlin
HomeScreen
 Balance Card
 Quick Actions
    Top-up → TopUpScreen
    Send → SendMoneyScreen
 Transaction List
```

### 4. Top-up (with WebView)
```kotlin
TopUpScreen
 Amount input
     → TopUpWebViewScreen
         WebView (payment gateway)
             Card number
             Expiry
             CVV
             Confirm → TopUpSuccessScreen
```

### 5. Send Money
```kotlin
SendMoneyScreen
 Recipient input
 Amount input
     → SendConfirmationScreen
         Confirm → SendSuccessScreen
```

---

##  Configuration

### Build Variants

Edit `app/build.gradle.kts`:

```kotlin
productFlavors {
    create("observe") {
        applicationIdSuffix = ".observe"
        versionNameSuffix = "-observe"
        buildConfigField("boolean", "OBSERVE_ENABLED", "true")
    }
    
    create("test") {
        applicationIdSuffix = ".test"
        versionNameSuffix = "-test"
        buildConfigField("boolean", "OBSERVE_ENABLED", "false")
        buildConfigField("boolean", "TEST_MODE", "true")
    }
}
```

### Mock API

Start mock backend:

```bash
cd demo-app/mock-backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be available at: `http://localhost:8000`

---

## 🧪 Testing

### Manual Testing:
```bash
# Install observe build
./gradlew installObserveDebug

# Use app and observe SDK will record events
```

### Automated Testing:
```bash
# Install test build
./gradlew installTestDebug

# Run Appium tests
pytest tests/
```

---

##  Notes

- **Observe build** includes SDK and records events
- **Test build** is clean, without SDK, for automated tests
- WebView payment gateway is a mock HTML page
- All API calls go to mock backend

---

##  Troubleshooting

### Build fails:
```bash
# Clean and rebuild
./gradlew clean
./gradlew assembleObserveDebug
```

### SDK not recording:
- Check that observe build is installed (not test)
- Check logcat: `adb logcat | grep ObserveSDK`

---

##  Resources

- [Jetpack Compose Docs](https://developer.android.com/jetpack/compose)
- [Navigation Component](https://developer.android.com/guide/navigation)
- [ViewPager2](https://developer.android.com/jetpack/androidx/releases/viewpager2)
- [WebView](https://developer.android.com/guide/webapps/webview)

---

**Status:**  In Development  
**Last Updated:** 2025-12-19

