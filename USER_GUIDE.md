# Mobile Observe & Test Framework - User Guide

> Complete guide to automated mobile testing with AI-powered test generation and self-healing

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Step-by-Step Workflow](#step-by-step-workflow)
- [Self-Healing Tests](#self-healing-tests)
- [Advanced Features](#advanced-features)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Usage Scenarios](#usage-scenarios)
- [API Reference](#api-reference)

---

## Overview

### What is Mobile Observe & Test Framework?

A next-generation platform that **automatically generates production-ready mobile tests** by observing real user behavior. Instead of writing tests manually, your QA team walks through the app once, and the framework:

1. **Records** all UI interactions, navigation, and API calls
2. **Analyzes** the app structure using static code analysis + ML
3. **Correlates** UI actions with API requests and responses
4. **Generates** Page Objects, API clients, and BDD test scenarios
5. **Self-heals** when UI changes break selectors

### Why Use It?

**Traditional approach:**
```python
# Manual test writing - tedious and time-consuming
def test_login():
    driver.find_element(By.ID, "email").send_keys("user@example.com")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "login_button").click()
    # Breaks when IDs change!
```

**Our approach:**
```bash
# 1. QA walks through app (no coding)
# 2. Run one command:
observe generate all --model app-model.json --output ./tests/

# 3. Get production-ready tests with:
#    - Robust selectors (ID → XPath → CSS fallbacks)
#    - API-first approach (80% API, 20% UI)
#    - Self-healing when UI changes
#    - Cross-platform support
```

---

## Installation

### Prerequisites

- **Python 3.13+**
- **Android Studio** (for Android apps)
- **Xcode** (for iOS apps)
- **Git**

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/mobile_test_recorder.git
cd mobile_test_recorder
```

### Step 2: Create Virtual Environment

```bash
# Create venv
python3.13 -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install framework
pip install -r requirements.txt

# Install as CLI tool
pip install -e .

# Verify installation
observe --version
```

### Step 4: Install Appium (for test execution)

```bash
# Install Node.js (if not already installed)
# Then install Appium
npm install -g appium
appium driver install uiautomator2  # For Android
appium driver install xcuitest       # For iOS
```

### Step 5: Setup Demo Apps (Optional)

```bash
# Android
cd demo-app/android
./gradlew assembleObserveDebug

# iOS
cd demo-app/ios
xcodebuild -project FinDemo.xcodeproj -scheme ObserveDebug build
```

---

## Quick Start

### 5-Minute Tutorial

**Goal:** Generate tests for a login flow

#### 1. Prepare Observe Build

Your app needs an "observe" build variant that includes the SDK:

```kotlin
// Android: build.gradle.kts
android {
    buildTypes {
        create("observe") {
            initWith(getByName("debug"))
            isDebuggable = true
        }
    }
}

dependencies {
    "observeImplementation"(project(":observe-sdk"))
}
```

#### 2. Record User Session

```bash
# Install observe build on device/emulator
adb install app-observe-debug.apk

# Walk through the app:
# 1. Open app
# 2. Enter email
# 3. Enter password
# 4. Click login
# 5. Verify dashboard appears

# Pull recorded events
adb pull /sdcard/Android/data/com.yourapp/files/observe/session_*.json
```

#### 3. Import Session

```bash
observe import \
  --session-file session_20250129_143022.json \
  --session-id login-flow \
  --platform android
```

#### 4. Build App Model

```bash
observe model build \
  --session login-flow \
  --static-analysis ./app/src/main \
  --output app-model.json
```

#### 5. Generate Tests

```bash
observe generate all \
  --model app-model.json \
  --output ./tests/ \
  --framework pytest-bdd
```

#### 6. Run Tests

```bash
# Start Appium
appium

# Run tests (in another terminal)
pytest tests/ --html=report.html
```

**Done!** You now have:
- `tests/pages/` - Page Object classes
- `tests/api/` - API client
- `tests/features/` - BDD scenarios
- `tests/step_definitions/` - Step implementations

---

## Core Concepts

### 1. Build Variants

Your app needs **three build variants**:

| Variant | Purpose | Includes SDK? | Used By |
|---------|---------|---------------|---------|
| **observe** | QA exploration | ✅ Yes | QA team for recording |
| **test** | Test execution | ❌ No | CI/CD, automation engineers |
| **production** | End users | ❌ No | App Store, Google Play |

**Why three variants?**
- **Zero production impact** - SDK never reaches users
- **Isolation** - Test environment separate from recording
- **Safety** - No risk of data leakage

### 2. App Model

The **App Model** is the central representation of your app:

```json
{
  "screens": [
    {
      "id": "LoginScreen",
      "elements": [
        {
          "id": "email_input",
          "selectors": [
            {"type": "id", "value": "email", "score": 0.95},
            {"type": "xpath", "value": "//input[@type='email']", "score": 0.80}
          ]
        }
      ]
    }
  ],
  "api_endpoints": [
    {
      "method": "POST",
      "path": "/api/v1/auth/login",
      "request_schema": {...},
      "response_schema": {...}
    }
  ],
  "transitions": [
    {
      "from": "LoginScreen",
      "to": "DashboardScreen",
      "trigger": "click:login_button",
      "api_calls": ["POST /api/v1/auth/login"]
    }
  ]
}
```

**Building the model:**
1. **Dynamic analysis** - Events from observe SDK
2. **Static analysis** - Parse Kotlin/Swift source code
3. **Correlation** - Link UI actions to API calls
4. **ML classification** - Identify element types

### 3. Selectors

**Problem:** UI IDs change, tests break.

**Solution:** Multi-strategy selectors with fallbacks:

```python
# Generated Page Object
class LoginPage:
    # Primary selector (high confidence)
    email_input = ("id", "email_field")  # Score: 0.95
    
    # Fallback selectors (if primary fails)
    _email_input_fallbacks = [
        ("xpath", "//input[@type='email']"),  # Score: 0.80
        ("css", "input[placeholder='Email']"),  # Score: 0.75
        ("text", "Email"),  # Score: 0.60
    ]
    
    def find_email_input(self, driver):
        # Try primary first
        try:
            return driver.find_element(*self.email_input)
        except NoSuchElementException:
            # Try fallbacks
            for selector in self._email_input_fallbacks:
                try:
                    return driver.find_element(*selector)
                except NoSuchElementException:
                    continue
            raise  # All selectors failed
```

### 4. API-First Testing

**Traditional:** 100% UI tests (slow, flaky)

**Our approach:** 80% API, 20% UI

```python
# UI test (only when necessary)
def test_login_ui():
    """Verify login button appears and is clickable"""
    page = LoginPage(driver)
    assert page.login_button.is_displayed()
    assert page.login_button.is_enabled()

# API test (fast and reliable)
def test_login_api():
    """Verify login endpoint accepts valid credentials"""
    response = api_client.auth.login(
        email="user@example.com",
        password="password123"
    )
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["user"]["email"] == "user@example.com"
```

**Benefits:**
- **10x faster** - No UI rendering
- **Less flaky** - No timing issues
- **Better coverage** - Test edge cases easily
- **CI-friendly** - Run in parallel

---

## Step-by-Step Workflow

### Phase 1: Observation

#### Step 1.1: Prepare App

Add observe build variant to your app:

**Android (build.gradle.kts):**
```kotlin
android {
    flavorDimensions += "mode"
    productFlavors {
        create("observe") {
            dimension = "mode"
            applicationIdSuffix = ".observe"
        }
        create("test") {
            dimension = "mode"
            applicationIdSuffix = ".test"
        }
        create("production") {
            dimension = "mode"
        }
    }
}

dependencies {
    "observeImplementation"(project(":observe-sdk"))
}
```

**iOS (Xcode schemes):**
1. Duplicate your scheme
2. Rename to "ObserveDebug"
3. Add `OBSERVE_BUILD` preprocessor macro
4. Link `ObserveSDK.framework`

#### Step 1.2: Initialize SDK

**Android:**
```kotlin
// Application.kt
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.FLAVOR == "observe") {
            ObserveSDK.initialize(
                context = this,
                config = ObserveConfig(
                    sessionId = "session_${System.currentTimeMillis()}",
                    exportIntervalMs = 30000
                )
            )
            ObserveSDK.start()
        }
    }
}
```

**iOS:**
```swift
// AppDelegate.swift
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(...) -> Bool {
        #if OBSERVE_BUILD
        ObserveSDK.shared.initialize(config: ObserveConfig(
            sessionId: "session_\(Date().timeIntervalSince1970)",
            exportInterval: 30.0
        ))
        ObserveSDK.shared.start()
        #endif
        return true
    }
}
```

#### Step 1.3: Record Session

```bash
# Build observe variant
./gradlew assembleObserveDebug  # Android
# or
xcodebuild -scheme ObserveDebug  # iOS

# Install on device
adb install app-observe-debug.apk

# Use the app (QA walks through features)
# - Complete login flow
# - Navigate to key screens
# - Perform important actions
# - Trigger API calls

# Export events (automatically saved)
adb pull /sdcard/Android/data/com.yourapp/files/observe/ ./sessions/
```

#### Step 1.4: Import Events

```bash
observe import \
  --session-file sessions/session_20250129_143022.json \
  --session-id my-app-session \
  --platform android \
  --app-package com.yourapp
```

**Expected output:**
```
✅ Session imported: my-app-session
   Platform: android
   Events: 247
   Duration: 3m 42s
   Screens: 8
   API calls: 23
   Stored in: ~/.observe/sessions/my-app-session/
```

### Phase 2: Analysis

#### Step 2.1: Static Code Analysis

```bash
observe analyze static \
  --platform android \
  --source ./app/src/main \
  --output analysis-result.json
```

**What it does:**
- Parses Kotlin/Swift files using tree-sitter
- Extracts activities/fragments, ViewControllers
- Identifies UI elements (buttons, inputs, etc.)
- Finds API endpoint definitions
- Discovers navigation patterns

#### Step 2.2: Build App Model

```bash
observe model build \
  --session my-app-session \
  --static-analysis analysis-result.json \
  --ml-model ml_models/universal_element_classifier.pkl \
  --output app-model.json \
  --correlation-strategy temporal
```

**Options:**
- `--correlation-strategy` - How to link UI → API:
  - `temporal` - By timestamp proximity (default)
  - `thread` - By thread ID
  - `tag` - By request tag
- `--ml-model` - Path to pre-trained ML model
- `--min-confidence` - Minimum selector confidence (default: 0.7)

**Expected output:**
```
🔍 Building app model...
   ✅ Loaded 247 events
   ✅ Found 8 screens
   ✅ Extracted 56 UI elements
   ✅ Discovered 23 API endpoints
   ✅ Identified 12 transitions
   ✅ Correlated 19 UI→API links
   
📊 Model statistics:
   Screens: 8
   Elements: 56
   Actions: 34
   API endpoints: 23
   Transitions: 12
   
💾 Model saved: app-model.json (234 KB)
```

### Phase 3: Test Generation

#### Step 3.1: Generate Page Objects

```bash
observe generate pages \
  --model app-model.json \
  --output tests/pages/ \
  --language python \
  --pattern page-object
```

**Generated:**
```python
# tests/pages/login_page.py
from appium.webdriver.common.mobileby import MobileBy

class LoginPage:
    """Login screen page object"""
    
    # Selectors with fallbacks
    email_input = (MobileBy.ID, "email_field")
    password_input = (MobileBy.ID, "password_field")
    login_button = (MobileBy.ID, "login_button")
    
    def __init__(self, driver):
        self.driver = driver
    
    def enter_email(self, email: str):
        """Enter email address"""
        self.driver.find_element(*self.email_input).send_keys(email)
    
    def enter_password(self, password: str):
        """Enter password"""
        self.driver.find_element(*self.password_input).send_keys(password)
    
    def click_login(self):
        """Click login button"""
        self.driver.find_element(*self.login_button).click()
    
    def login(self, email: str, password: str):
        """Complete login flow"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()
```

#### Step 3.2: Generate API Client

```bash
observe generate api \
  --model app-model.json \
  --output tests/api/ \
  --base-url https://api.yourapp.com
```

**Generated:**
```python
# tests/api/auth_client.py
import requests

class AuthClient:
    """Authentication API client"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, email: str, password: str) -> dict:
        """
        POST /api/v1/auth/login
        
        Authenticate user and return token
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    def logout(self, token: str) -> None:
        """POST /api/v1/auth/logout"""
        self.session.post(
            f"{self.base_url}/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
```

#### Step 3.3: Generate BDD Scenarios

```bash
observe generate bdd \
  --model app-model.json \
  --output tests/features/ \
  --language gherkin
```

**Generated:**
```gherkin
# tests/features/login.feature
Feature: User Authentication
  As a user
  I want to log in to the app
  So that I can access my account

  Scenario: Successful login with valid credentials
    Given the app is launched
    And I am on the login screen
    When I enter email "user@example.com"
    And I enter password "password123"
    And I click the login button
    Then I should see the dashboard screen
    And I should be authenticated

  Scenario: Failed login with invalid credentials
    Given the app is launched
    And I am on the login screen
    When I enter email "invalid@example.com"
    And I enter password "wrongpassword"
    And I click the login button
    Then I should see an error message "Invalid credentials"
    And I should remain on the login screen
```

#### Step 3.4: Generate Step Definitions

```bash
observe generate steps \
  --model app-model.json \
  --features tests/features/ \
  --output tests/step_definitions/
```

**Generated:**
```python
# tests/step_definitions/test_login_steps.py
from pytest_bdd import scenarios, given, when, then, parsers
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

scenarios('../features/login.feature')

@given('I am on the login screen')
def on_login_screen(driver):
    page = LoginPage(driver)
    assert page.is_displayed()

@when(parsers.parse('I enter email "{email}"'))
def enter_email(driver, email):
    page = LoginPage(driver)
    page.enter_email(email)

@when(parsers.parse('I enter password "{password}"'))
def enter_password(driver, password):
    page = LoginPage(driver)
    page.enter_password(password)

@when('I click the login button')
def click_login(driver):
    page = LoginPage(driver)
    page.click_login()

@then('I should see the dashboard screen')
def verify_dashboard(driver):
    page = DashboardPage(driver)
    assert page.is_displayed()
```

#### Step 3.5: Generate All at Once

```bash
observe generate all \
  --model app-model.json \
  --output tests/ \
  --framework pytest-bdd \
  --language python
```

Creates complete test structure:
```
tests/
├── conftest.py           # Pytest fixtures
├── pages/                # Page Objects
│   ├── login_page.py
│   ├── dashboard_page.py
│   └── transfer_page.py
├── api/                  # API clients
│   ├── auth_client.py
│   ├── transfer_client.py
│   └── account_client.py
├── features/             # BDD scenarios
│   ├── login.feature
│   ├── transfer.feature
│   └── account.feature
└── step_definitions/     # Step implementations
    ├── test_login_steps.py
    ├── test_transfer_steps.py
    └── test_account_steps.py
```

### Phase 4: Test Execution

#### Step 4.1: Configure Appium

```python
# tests/conftest.py
import pytest
from appium import webdriver

@pytest.fixture(scope="session")
def driver():
    """Appium driver for Android"""
    caps = {
        "platformName": "Android",
        "platformVersion": "13",
        "deviceName": "emulator-5554",
        "app": "/path/to/app-test-debug.apk",
        "automationName": "UiAutomator2",
        "newCommandTimeout": 300
    }
    
    driver = webdriver.Remote(
        "http://localhost:4723",
        desired_capabilities=caps
    )
    
    yield driver
    
    driver.quit()
```

#### Step 4.2: Run Tests

```bash
# Start Appium server
appium &

# Run all tests
pytest tests/ -v

# Run specific feature
pytest tests/step_definitions/test_login_steps.py

# Run with HTML report
pytest tests/ --html=report.html --self-contained-html

# Run in parallel
pytest tests/ -n 4

# Run with JUnit XML (for CI)
pytest tests/ --junit-xml=results.xml
```

---

## Self-Healing Tests

### When Tests Break

Tests fail when UI changes:
```
NoSuchElementException: Element with id 'login_button' not found
```

**Traditional approach:** Manually fix selectors 😫

**Our approach:** Automatic healing 🎯

### How It Works

```
Test fails  →  Capture page state  →  Try alternatives  →  ML picks best  →  Update code  →  Commit
```

### Step 1: Analyze Failures

```bash
# Tests failed, you have junit.xml with results
pytest tests/ --junit-xml=results.xml

# Analyze what broke
observe heal analyze \
  --test-results results.xml \
  --screenshots ./screenshots \
  --page-source ./page-dumps \
  --page-objects ./tests/pages
```

**Output:**
```
🔍 Analyzing test failures...

SELECTOR FAILURE ANALYSIS
================================================================================

Found 3 selector failure(s):

1. Test: test_login_flow
   Selector: (id, 'login_button')
   File: tests/pages/login_page.py
   Page Object: LoginPage
   Screenshot: screenshots/test_login_flow.png
   Page Source: page-dumps/test_login_flow.xml
   Error: NoSuchElementException: Element not found...

2. Test: test_transfer_flow
   Selector: (id, 'amount_input')
   ...

💡 3/3 failures can be auto-healed
```

### Step 2: Test Healing (Dry Run)

```bash
observe heal auto \
  --test-results results.xml \
  --page-source ./page-dumps \
  --page-objects ./tests/pages \
  --min-confidence 0.8 \
  --dry-run
```

**Output:**
```
🔧 Auto-healing (DRY RUN)...
🔍 Analyzing failures...
Found 3 selector failure(s)

🔧 Healing selectors...

HEALING REPORT
================================================================================
Found 3 selector failure(s):

SUCCESSFUL HEALINGS:

1. test_login_flow
   Element: login_button
   Old: (id, 'login_button')
   New: (xpath, '//button[@text="Login"]')
   Confidence: 0.92
   Strategy: xpath
   File: tests/pages/login_page.py

2. test_transfer_flow
   Element: amount_input
   Old: (id, 'amount_input')
   New: (id, 'transfer_amount_field')
   Confidence: 0.95
   Strategy: id
   File: tests/pages/transfer_page.py

================================================================================

💡 2 selector(s) would be healed
   Remove --dry-run to apply changes
```

### Step 3: Apply Healing

```bash
observe heal auto \
  --test-results results.xml \
  --page-source ./page-dumps \
  --page-objects ./tests/pages \
  --commit \
  --branch auto-heal-jan29
```

**What happens:**
1. ✅ Selectors updated in Page Objects
2. ✅ Backup files created (`.bak`)
3. ✅ Git commit with details
4. ✅ New branch created

**Updated Page Object:**
```python
class LoginPage:
    # Auto-healed: 2025-01-29 14:30:12
    # Original: ('id', 'login_button') - element not found
    # New: xpath strategy, confidence: 0.92
    login_button = ("xpath", "//button[@text='Login']")
    # Fallback: ('id', 'login_button')
```

**Git commit:**
```
commit a1b2c3d4
Auto-heal: Fixed broken selectors

Healed 2 selector(s) automatically:

1. login_button
   File: tests/pages/login_page.py
   Old: ('id', 'login_button')
   New: ('xpath', '//button[@text="Login"]')
   Confidence: 0.92
   Strategy: xpath

2. amount_input
   File: tests/pages/transfer_page.py
   Old: ('id', 'amount_input')
   New: ('id', 'transfer_amount_field')
   Confidence: 0.95
   Strategy: id

Generated by Mobile Test Recorder healing system
Timestamp: 2025-01-29T14:30:12
```

### Step 4: Review in Dashboard

```bash
observe dashboard
```

Open http://localhost:8080 and review:

**Dashboard shows:**
- ✅ Which selectors were healed
- ✅ Old vs new selector
- ✅ Confidence score (color-coded)
- ✅ Test runs after healing
- ✅ Success rate

**Actions:**
- 👍 **Approve** - Keep the change, commit to master
- 👎 **Reject** - Revert to original, manual fix needed

### Step 5: Re-run Tests

```bash
pytest tests/
```

**Result:** ✅ All tests pass!

### Healing History

```bash
observe heal history --limit 10
```

**Output:**
```
📜 Healing history...

1. a1b2c3d4 - 2025-01-29 14:30
   Files: 2, Selectors: 2
   Auto-heal: Fixed broken selectors

2. e5f6g7h8 - 2025-01-28 09:45
   Files: 1, Selectors: 1
   Auto-heal: Fixed broken selectors
```

### Revert Healing

```bash
# If healing caused issues
observe heal revert a1b2c3d4

# Confirm
Are you sure? [y/N]: y

✅ Commit reverted successfully
```

---

## Advanced Features

### Device Management

#### List Available Devices

```bash
observe devices list --platform android
```

**Output:**
```
📱 Available devices:

Emulators:
  1. emulator-5554 (Android 13, Pixel 6)
  2. emulator-5556 (Android 12, Pixel 5)

Real Devices:
  3. RF8N12ABC (Android 14, Samsung Galaxy S23)

BrowserStack:
  4. Samsung Galaxy S22 (Android 13)
  5. Google Pixel 7 (Android 14)
```

#### Filter Devices

```bash
observe devices list \
  --platform android \
  --min-version 12 \
  --device-type real
```

### Smart Test Selection

Run only tests affected by code changes:

```bash
observe select \
  --since HEAD~5 \
  --test-dir tests/ \
  --output selected-tests.txt

pytest $(cat selected-tests.txt)
```

**How it works:**
1. Analyze git diff
2. Find changed files
3. Map to test dependencies
4. Select impacted tests only

**Benefits:**
- **10x faster** CI builds
- Run only relevant tests
- Still catch regressions

### Parallel Execution

```bash
observe execute parallel \
  --tests tests/ \
  --devices emulator-5554,emulator-5556 \
  --sharding duration \
  --workers 4
```

**Sharding strategies:**
- `count` - Equal number of tests per shard
- `duration` - Balance by test duration
- `file` - One file per shard
- `scenario` - One BDD scenario per shard

### Security Analysis

```bash
observe analyze security \
  --apk app-release.apk \
  --output security-report.json
```

**Checks:**
- ✅ Hardcoded secrets (API keys, passwords)
- ✅ Certificate pinning
- ✅ Root/jailbreak detection
- ✅ Code obfuscation
- ✅ Insecure network traffic
- ✅ OWASP Mobile Top 10

### Performance Profiling

```bash
observe analyze performance \
  --device emulator-5554 \
  --app com.yourapp \
  --duration 60 \
  --output perf-report.json
```

**Metrics:**
- CPU usage
- Memory consumption
- FPS (frames per second)
- Network latency
- Battery drain

### Visual Regression

```bash
observe analyze visual \
  --test-screenshots current/ \
  --baseline-screenshots baseline/ \
  --threshold 0.95 \
  --output visual-diff.html
```

---

## CI/CD Integration

### GitHub Actions

#### Generate Workflow

```bash
observe ci init \
  --provider github \
  --platforms android,ios \
  --output .github/workflows/tests.yml
```

#### Generated Workflow

```yaml
name: Mobile Tests

on: [push, pull_request]

jobs:
  test-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Setup Android emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 33
          target: google_apis
      
      - name: Run tests
        run: pytest tests/ --junit-xml=results.xml
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: results.xml
```

### GitLab CI

```bash
observe ci init \
  --provider gitlab \
  --platforms android,ios \
  --output .gitlab-ci.yml
```

### Advanced CI Features

#### Self-Healing in CI

```yaml
- name: Run tests with auto-healing
  run: |
    pytest tests/ --junit-xml=results.xml || true
    observe heal auto --test-results results.xml --commit
    pytest tests/ --junit-xml=results-healed.xml
```

#### Smart Test Selection

```yaml
- name: Select impacted tests
  run: |
    observe select --since origin/master --output tests.txt
    pytest $(cat tests.txt)
```

#### Parallel Execution

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]

steps:
  - name: Run tests
    run: |
      pytest tests/ \
        --shard-id=${{ matrix.shard }} \
        --num-shards=4
```

---

## Troubleshooting

### Common Issues

#### Issue: "ObserveSDK not initialized"

**Cause:** SDK not started in Application class

**Solution:**
```kotlin
// Add to Application.onCreate()
if (BuildConfig.FLAVOR == "observe") {
    ObserveSDK.initialize(this, ObserveConfig(...))
    ObserveSDK.start()
}
```

#### Issue: "No events recorded"

**Cause:** Events not exported or file permissions

**Solution:**
```bash
# Check if events exist
adb shell ls /sdcard/Android/data/com.yourapp/files/observe/

# Grant storage permission
adb shell pm grant com.yourapp android.permission.WRITE_EXTERNAL_STORAGE

# Pull events manually
adb pull /sdcard/Android/data/com.yourapp/files/observe/ ./
```

#### Issue: "Element not found" in tests

**Cause:** Timing issues, element not loaded

**Solution:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Use explicit waits
wait = WebDriverWait(driver, 10)
element = wait.until(EC.presence_of_element_located((By.ID, "login_button")))
```

#### Issue: "Healing confidence too low"

**Cause:** ML model unsure about element match

**Solution:**
```bash
# Lower confidence threshold (use with caution)
observe heal auto --min-confidence 0.6

# Or manually fix and add to training data
observe ml train --examples ./manual-fixes/
```

#### Issue: "Tests fail in CI but pass locally"

**Cause:** Environment differences, timing

**Solution:**
```python
# conftest.py - Add longer timeouts for CI
import os

TIMEOUT = 30 if os.getenv('CI') else 10

@pytest.fixture
def driver():
    caps = {
        ...
        "newCommandTimeout": TIMEOUT,
    }
```

### Debug Mode

```bash
# Enable verbose logging
export OBSERVE_LOG_LEVEL=DEBUG

# Run with debug output
observe --debug model build ...

# Check logs
tail -f ~/.observe/logs/observe.log
```

---

## Best Practices

### 1. Recording Sessions

✅ **Do:**
- Record complete user flows (start to finish)
- Include happy paths and common scenarios
- Interact naturally (no rushing)
- Wait for screens to fully load
- Test with realistic data

❌ **Don't:**
- Record incomplete flows
- Skip authentication
- Use placeholder data like "test@test.com"
- Record too many flows at once (keep sessions focused)

### 2. Selector Strategies

✅ **Do:**
- Prefer stable IDs over XPath
- Use multiple fallback strategies
- Set confidence thresholds appropriately
- Review auto-healed selectors

❌ **Don't:**
- Rely only on absolute XPath
- Use dynamic IDs like `button_12345`
- Accept low-confidence healings (<0.7)
- Skip manual review for critical flows

### 3. Test Organization

✅ **Do:**
```
tests/
├── api/              # API tests (80%)
│   ├── test_auth_api.py
│   └── test_transfer_api.py
├── ui/               # UI tests (20%)
│   ├── test_login_ui.py
│   └── test_dashboard_ui.py
└── e2e/              # End-to-end flows
    └── test_full_transfer.py
```

❌ **Don't:**
- Mix API and UI tests in same file
- Write only UI tests
- Create giant test files (>500 lines)

### 4. CI/CD Integration

✅ **Do:**
- Run API tests first (fast feedback)
- Use smart test selection
- Enable auto-healing
- Generate HTML reports
- Cache dependencies

❌ **Don't:**
- Run all tests on every commit
- Skip failing tests
- Disable healing in CI
- Ignore flaky tests

### 5. Maintenance

✅ **Do:**
- Review healing dashboard weekly
- Update selectors proactively
- Keep ML model updated
- Archive old sessions
- Document test data requirements

❌ **Don't:**
- Auto-approve all healings blindly
- Keep broken tests disabled
- Let technical debt accumulate

---

## Usage Scenarios

Complete guide to all possible use cases and scenarios for using the framework.

### Scenario 1: First-Time Project Setup

**Goal:** Set up testing for a new mobile app from scratch.

**Steps:**

```bash
# 1. Initialize new test project
observe init --platform android --output ./my-app-tests

# 2. Configure observe SDK in your app
# Edit app/build.gradle.kts and add observe build variant

# 3. Build and install observe variant
./gradlew assembleObserveDebug
adb install app/build/outputs/apk/observe/debug/app-observe-debug.apk

# 4. Record first session (QA walks through app)
# SDK automatically records events

# 5. Pull events from device
adb pull /sdcard/Android/data/com.yourapp/files/observe/ ./sessions/

# 6. Import session
observe import \
  --session-file sessions/session_*.json \
  --session-id onboarding-flow \
  --platform android

# 7. Analyze codebase
observe analyze static \
  --platform android \
  --source ./app/src/main \
  --output analysis.json

# 8. Build app model
observe model build \
  --session onboarding-flow \
  --static-analysis analysis.json \
  --output app-model.json

# 9. Generate all test artifacts
observe generate all \
  --model app-model.json \
  --output ./tests/ \
  --framework pytest-bdd

# 10. Run first tests
pytest tests/ --html=report.html
```

**Result:** Complete test suite ready in ~30 minutes.

---

### Scenario 2: Adding Tests for New Feature

**Goal:** Your app added a new "Money Transfer" feature, need tests.

**Steps:**

```bash
# 1. Record only the new feature
# Install observe build, walk through transfer flow

# 2. Import as separate session
observe import \
  --session-file transfer_session.json \
  --session-id transfer-feature \
  --platform android

# 3. Build incremental model (merge with existing)
observe model build \
  --session transfer-feature \
  --merge-with existing-model.json \
  --output updated-model.json

# 4. Generate only new pages/tests
observe generate pages \
  --model updated-model.json \
  --output tests/pages/ \
  --only-new

observe generate bdd \
  --model updated-model.json \
  --output tests/features/ \
  --filter "transfer"

# 5. Run new tests
pytest tests/features/transfer.feature -v
```

**Result:** New tests without regenerating existing ones.

---

### Scenario 3: Cross-Platform Testing (Android + iOS)

**Goal:** Generate tests for both Android and iOS from separate observations.

**Steps:**

```bash
# 1. Record Android session
observe import \
  --session-file android_session.json \
  --session-id app-android \
  --platform android

# 2. Record iOS session  
observe import \
  --session-file ios_session.json \
  --session-id app-ios \
  --platform ios

# 3. Build unified model
observe model build \
  --session app-android \
  --session app-ios \
  --cross-platform \
  --output unified-model.json

# 4. Generate platform-specific tests
observe generate all \
  --model unified-model.json \
  --output tests/ \
  --platforms android,ios

# Result structure:
tests/
├── android/
│   ├── pages/
│   └── features/
├── ios/
│   ├── pages/
│   └── features/
└── shared/
    └── api/  # Same API tests for both
```

**Result:** Shared API tests + platform-specific UI tests.

---

### Scenario 4: API-First Testing Strategy

**Goal:** Focus on API testing, minimal UI tests.

**Steps:**

```bash
# 1. Build model with API emphasis
observe model build \
  --session my-session \
  --correlation-strategy temporal \
  --api-first \
  --output model.json

# 2. Generate mostly API tests
observe generate api \
  --model model.json \
  --output tests/api/ \
  --full-coverage

# 3. Generate minimal UI tests (smoke only)
observe generate ui \
  --model model.json \
  --output tests/ui/ \
  --smoke-only

# 4. Run API tests (fast)
pytest tests/api/ -v --maxfail=1

# 5. Run UI tests (only if APIs pass)
pytest tests/ui/ -v
```

**Test ratio achieved:** 85% API, 15% UI

---

### Scenario 5: Handling Flaky Tests

**Goal:** Identify and fix flaky tests using dashboard.

**Steps:**

```bash
# 1. Run tests multiple times and collect results
for i in {1..30}; do
  pytest tests/ --junit-xml=results/run_$i.xml
done

# 2. Aggregate results into database
for file in results/*.xml; do
  observe dashboard import --junit-xml $file
done

# 3. Start dashboard
observe dashboard

# 4. In browser (http://localhost:8080):
#    - Go to "Test Health" tab
#    - Sort by "Pass Rate" (ascending)
#    - Find tests with 20-80% pass rate
#    - Click on test to see details

# 5. Fix identified issues:
#    - Add explicit waits
#    - Use better selectors
#    - Fix timing dependencies

# 6. Re-run and verify
pytest tests/ --count=10 --flaky-test-marker
```

**Result:** Reduced flaky tests from 15% to <3%.

---

### Scenario 6: Self-Healing in CI Pipeline

**Goal:** Automatically fix broken selectors in CI.

**Create workflow:**

```yaml
# .github/workflows/tests-with-healing.yml
name: Tests with Self-Healing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Start Appium
        run: appium &
      
      - name: Run tests
        id: tests
        run: |
          pytest tests/ --junit-xml=results.xml || true
      
      - name: Auto-heal broken selectors
        if: failure()
        run: |
          observe heal auto \
            --test-results results.xml \
            --page-source ./page-dumps \
            --page-objects ./tests/pages \
            --commit \
            --branch auto-heal-${{ github.run_id }}
      
      - name: Re-run tests after healing
        if: failure()
        run: pytest tests/ --junit-xml=results-healed.xml
      
      - name: Create PR with fixes
        if: success()
        uses: peter-evans/create-pull-request@v5
        with:
          branch: auto-heal-${{ github.run_id }}
          title: "Auto-heal: Fixed selectors from run ${{ github.run_id }}"
          body: "Automatically healed broken selectors. Review changes before merging."
```

**Result:** CI auto-fixes selectors and creates PR for review.

---

### Scenario 7: Performance Regression Testing

**Goal:** Monitor app performance across releases.

**Steps:**

```bash
# 1. Baseline measurement (v1.0)
observe analyze performance \
  --device emulator-5554 \
  --app com.yourapp \
  --duration 120 \
  --scenario "login,dashboard,transfer" \
  --output baseline-v1.0.json

# 2. New release measurement (v1.1)
observe analyze performance \
  --device emulator-5554 \
  --app com.yourapp \
  --duration 120 \
  --scenario "login,dashboard,transfer" \
  --output current-v1.1.json

# 3. Compare results
observe analyze performance compare \
  --baseline baseline-v1.0.json \
  --current current-v1.1.json \
  --threshold 10% \
  --output comparison-report.html

# 4. Fail CI if regression detected
observe analyze performance compare \
  --baseline baseline-v1.0.json \
  --current current-v1.1.json \
  --threshold 10% \
  --fail-on-regression
```

**Metrics tracked:**
- CPU usage
- Memory consumption
- FPS (UI smoothness)
- Network latency
- Battery drain

---

### Scenario 8: Security Audit

**Goal:** Scan app for security vulnerabilities.

**Steps:**

```bash
# 1. Decompile and analyze APK
observe analyze security \
  --apk app-release.apk \
  --deep-scan \
  --output security-report.json

# 2. Check for common vulnerabilities
observe analyze security \
  --apk app-release.apk \
  --checks hardcoded-secrets,weak-crypto,insecure-network \
  --severity high,critical

# 3. Verify certificate pinning
observe analyze security \
  --apk app-release.apk \
  --check-pinning \
  --expected-pins sha256/abc123,sha256/def456

# 4. Test for root detection bypass
observe analyze security \
  --apk app-release.apk \
  --test-root-detection \
  --rooted-device true

# 5. Generate compliance report
observe analyze security \
  --apk app-release.apk \
  --compliance OWASP-MASVS \
  --output compliance-report.pdf
```

**Checks performed:**
- Hardcoded API keys/passwords
- Weak encryption algorithms
- Insecure network traffic
- Certificate pinning status
- Root/jailbreak detection
- Code obfuscation level
- SQL injection vulnerabilities
- XSS vulnerabilities

---

### Scenario 9: Visual Regression Testing

**Goal:** Detect unintended UI changes.

**Steps:**

```bash
# 1. Capture baseline screenshots (v1.0)
observe analyze visual capture \
  --app com.yourapp \
  --device emulator-5554 \
  --flows login,dashboard,transfer \
  --output baselines/v1.0/

# 2. After UI update, capture new screenshots
observe analyze visual capture \
  --app com.yourapp \
  --device emulator-5554 \
  --flows login,dashboard,transfer \
  --output current/

# 3. Compare screenshots
observe analyze visual compare \
  --baseline baselines/v1.0/ \
  --current current/ \
  --threshold 0.95 \
  --output visual-diff-report.html

# 4. Review differences in browser
open visual-diff-report.html

# 5. Accept intentional changes
observe analyze visual approve \
  --screen login \
  --update-baseline

# 6. Fail CI on unintended changes
observe analyze visual compare \
  --baseline baselines/v1.0/ \
  --current current/ \
  --threshold 0.95 \
  --fail-on-difference
```

**Features:**
- Pixel-perfect comparison
- Ignore regions (dynamic content)
- Multiple viewport sizes
- Cross-device comparison

---

### Scenario 10: Multi-Device Testing

**Goal:** Run tests on multiple devices in parallel.

**Steps:**

```bash
# 1. List available devices
observe devices list --platform android

# Output:
# Emulators:
#   1. emulator-5554 (Pixel 6, Android 13)
#   2. emulator-5556 (Pixel 5, Android 12)
# Real Devices:
#   3. RF8N12ABC (Galaxy S23, Android 14)

# 2. Create device pool
observe devices pool create \
  --name android-pool \
  --devices emulator-5554,emulator-5556,RF8N12ABC

# 3. Run tests in parallel
observe execute parallel \
  --tests tests/ \
  --pool android-pool \
  --sharding duration \
  --workers 3

# 4. Alternative: Use BrowserStack
observe devices pool create \
  --name cloud-pool \
  --provider browserstack \
  --devices "Samsung Galaxy S22,Google Pixel 7,OnePlus 10"

observe execute parallel \
  --tests tests/ \
  --pool cloud-pool \
  --workers 3
```

**Result:** Tests run 3x faster with parallel execution.

---

### Scenario 11: Smart Test Selection (CI Optimization)

**Goal:** Run only tests affected by code changes.

**Steps:**

```bash
# 1. Analyze what changed
observe select \
  --since origin/master \
  --test-dir tests/ \
  --source-dir app/src/main \
  --output selected-tests.txt

# Output:
# Changed files:
#   - app/src/main/java/com/app/LoginActivity.kt
#   - app/src/main/java/com/app/api/AuthClient.kt
# 
# Affected tests:
#   - tests/features/login.feature
#   - tests/api/test_auth_api.py
#   - tests/ui/test_login_ui.py

# 2. Run only selected tests
pytest $(cat selected-tests.txt) -v

# 3. In CI:
observe select \
  --since $CI_COMMIT_BEFORE_SHA \
  --test-dir tests/ \
  --impact-analysis \
  --output selected.txt

pytest $(cat selected.txt) --junit-xml=results.xml
```

**Time savings:** 10x faster CI builds (run 10% of tests instead of 100%).

---

### Scenario 12: Test Data Management

**Goal:** Generate and manage test data for different scenarios.

**Steps:**

```bash
# 1. Extract test data from observations
observe data extract \
  --session my-session \
  --output test-data.json

# Output:
# {
#   "users": [
#     {"email": "user@example.com", "password": "..."},
#     {"email": "admin@example.com", "password": "..."}
#   ],
#   "transfers": [
#     {"amount": 100, "currency": "USD", "to": "..."}
#   ]
# }

# 2. Generate synthetic test data
observe data generate \
  --model app-model.json \
  --scenario login \
  --count 100 \
  --output synthetic-users.json

# 3. Parametrize tests with data
pytest tests/test_login.py \
  --test-data synthetic-users.json \
  --parallel

# 4. Clean up test data after run
observe data cleanup \
  --app com.yourapp \
  --test-users-only
```

---

### Scenario 13: WebView Testing

**Goal:** Test interactions within embedded WebViews.

**Steps:**

```bash
# 1. Enable WebView observation in SDK
# ObserveSDK.observeWebView(webView) in app code

# 2. Record session with WebView interactions
# QA fills payment form in WebView

# 3. Import and build model
observe import --session-file webview-session.json --session-id payment
observe model build --session payment --output model.json

# 4. Generate WebView-aware tests
observe generate all \
  --model model.json \
  --output tests/ \
  --webview-support

# Result: Tests with context switching
def test_payment_in_webview(driver):
    page = CheckoutPage(driver)
    page.click_pay_button()
    
    # Switch to WebView context
    driver.switch_to.context('WEBVIEW_com.yourapp')
    
    # Interact with web elements
    driver.find_element(By.ID, "card-number").send_keys("4242424242424242")
    driver.find_element(By.ID, "submit").click()
    
    # Switch back to native
    driver.switch_to.context('NATIVE_APP')
    
    assert page.payment_success_message.is_displayed()
```

---

### Scenario 14: ML Model Training/Update

**Goal:** Improve ML element classification with app-specific data.

**Steps:**

```bash
# 1. Export current model performance
observe ml evaluate \
  --model ml_models/universal_element_classifier.pkl \
  --test-data validation-set.json \
  --output metrics.json

# 2. Collect misclassified examples
observe ml collect-errors \
  --sessions sessions/*.json \
  --min-confidence 0.7 \
  --output misclassified.json

# 3. Manually label corrections
# Edit misclassified.json and fix labels

# 4. Fine-tune model
observe ml train \
  --base-model ml_models/universal_element_classifier.pkl \
  --training-data misclassified.json \
  --epochs 10 \
  --output ml_models/fine_tuned_model.pkl

# 5. Evaluate improved model
observe ml evaluate \
  --model ml_models/fine_tuned_model.pkl \
  --test-data validation-set.json

# 6. Use updated model
observe model build \
  --session my-session \
  --ml-model ml_models/fine_tuned_model.pkl \
  --output model.json
```

**Improvement:** 90% → 95% element classification accuracy.

---

### Scenario 15: Integration with Existing Test Suite

**Goal:** Add observe-generated tests to existing pytest project.

**Steps:**

```bash
# 1. Detect existing project structure
observe framework detect --path ./existing-tests/

# Output:
# Framework: pytest
# Test files: 45
# Page Objects: Yes (Page Object Model)
# BDD: No
# API tests: 12
# UI tests: 33

# 2. Generate compatible tests
observe generate all \
  --model app-model.json \
  --output ./existing-tests/ \
  --integrate \
  --match-style

# 3. Merge fixtures
observe framework merge-fixtures \
  --source generated-tests/conftest.py \
  --target existing-tests/conftest.py

# 4. Run combined suite
pytest existing-tests/ generated-tests/ -v

# 5. Update CI configuration
observe ci init \
  --provider github \
  --existing-workflow .github/workflows/tests.yml \
  --append
```

**Result:** Seamless integration with existing tests.

---

### Scenario 16: Debugging Failed Tests

**Goal:** Investigate why tests fail.

**Steps:**

```bash
# 1. Run test with detailed output
pytest tests/test_login.py -vv --capture=no --tb=long

# 2. Capture screenshot on failure
pytest tests/test_login.py \
  --screenshot-on-failure \
  --screenshot-dir=./failures/

# 3. Save page source on failure
pytest tests/test_login.py \
  --page-source-on-failure \
  --page-source-dir=./failures/

# 4. Record video of test execution
observe execute record \
  --test tests/test_login.py \
  --output-video login-test.mp4

# 5. Analyze failure with healing
observe heal analyze \
  --test-results junit.xml \
  --screenshots ./failures/ \
  --page-source ./failures/ \
  --detailed-report

# 6. Get AI suggestions
observe heal suggest \
  --failure "NoSuchElementException: login_button" \
  --page-source ./failures/page.xml \
  --confidence-threshold 0.8
```

---

### Scenario 17: Load/Stress Testing

**Goal:** Test app under heavy load.

**Steps:**

```bash
# 1. Define load scenario
cat > load-scenario.yml <<EOF
scenarios:
  - name: concurrent-logins
    users: 100
    duration: 300s
    ramp-up: 30s
    actions:
      - login
      - view-dashboard
      - logout

  - name: heavy-transfers
    users: 50
    duration: 600s
    actions:
      - login
      - create-transfer (repeat: 10)
      - logout
EOF

# 2. Run load test
observe execute load \
  --scenario load-scenario.yml \
  --devices 10 \
  --output load-results.json

# 3. Analyze results
observe analyze load \
  --results load-results.json \
  --metrics response-time,error-rate,throughput \
  --output load-report.html

# 4. Compare with baseline
observe analyze load compare \
  --baseline baseline-load.json \
  --current load-results.json \
  --threshold 20%
```

---

### Scenario 18: Monitoring Dashboard Usage

**Goal:** Track test health over time.

**Steps:**

```bash
# 1. Run tests and import results daily
# In cron job or CI:
pytest tests/ --junit-xml=results-$(date +%Y%m%d).xml
observe dashboard import --junit-xml results-$(date +%Y%m%d).xml

# 2. Start dashboard
observe dashboard --port 8080

# 3. View trends:
#    - Go to http://localhost:8080
#    - "Test Health" tab
#    - Sort by "Trend" column
#    - Identify degrading tests

# 4. Export metrics for external monitoring
observe dashboard export \
  --format prometheus \
  --output metrics.txt

# 5. Set up alerts
cat > alerts.yml <<EOF
alerts:
  - name: flaky-test-threshold
    condition: flaky_tests_count > 5
    action: email-team

  - name: pass-rate-drop
    condition: pass_rate < 0.85
    action: slack-notification
EOF

observe dashboard alerts --config alerts.yml
```

---

### Scenario 19: Accessibility Testing

**Goal:** Verify app meets accessibility standards.

**Steps:**

```bash
# 1. Run accessibility scan
observe analyze accessibility \
  --app com.yourapp \
  --device emulator-5554 \
  --screens login,dashboard,transfer \
  --standards WCAG-2.1-AA \
  --output accessibility-report.html

# 2. Check specific issues
observe analyze accessibility \
  --app com.yourapp \
  --checks \
    contrast-ratio,\
    touch-target-size,\
    text-scaling,\
    screen-reader-support

# 3. Generate compliance report
observe analyze accessibility \
  --app com.yourapp \
  --compliance ADA \
  --output ada-compliance.pdf

# 4. Fix detected issues and re-test
observe analyze accessibility \
  --app com.yourapp \
  --baseline accessibility-baseline.json \
  --show-improvements
```

---

### Scenario 20: Continuous Test Generation

**Goal:** Automatically update tests as app evolves.

**Setup recurring job:**

```bash
#!/bin/bash
# update-tests.sh - Run weekly

# 1. Record latest app version
observe record-session \
  --app com.yourapp.observe \
  --device emulator-5554 \
  --scenario automated-walkthrough \
  --output session-$(date +%Y%m%d).json

# 2. Import session
observe import \
  --session-file session-$(date +%Y%m%d).json \
  --session-id weekly-$(date +%Y%m%d) \
  --platform android

# 3. Build updated model
observe model build \
  --session weekly-$(date +%Y%m%d) \
  --merge-with current-model.json \
  --output updated-model.json

# 4. Detect changes
observe model diff \
  --old current-model.json \
  --new updated-model.json \
  --output changes.json

# 5. Generate tests for new/changed screens only
observe generate incremental \
  --model updated-model.json \
  --changes changes.json \
  --output tests/

# 6. Run new tests
pytest tests/ --new-tests-only -v

# 7. Commit if successful
if [ $? -eq 0 ]; then
  git add tests/
  git commit -m "Auto-update: Generated tests for $(date +%Y-%m-%d)"
  git push origin auto-tests-$(date +%Y%m%d)
fi
```

**Schedule in cron:**
```bash
# Run every Sunday at 2 AM
0 2 * * 0 /path/to/update-tests.sh
```

---

## Summary of All Scenarios

| # | Scenario | Primary Commands | Use Case |
|---|----------|------------------|----------|
| 1 | First-Time Setup | `init`, `import`, `model build`, `generate` | New project |
| 2 | New Feature | `import`, `model build --merge`, `generate` | Incremental |
| 3 | Cross-Platform | `model build --cross-platform` | Android + iOS |
| 4 | API-First | `generate api --full-coverage` | Fast tests |
| 5 | Flaky Tests | `dashboard`, `analyze` | Quality |
| 6 | Auto-Healing CI | `heal auto --commit` | Maintenance |
| 7 | Performance | `analyze performance` | Regression |
| 8 | Security | `analyze security` | Audit |
| 9 | Visual Regression | `analyze visual` | UI changes |
| 10 | Multi-Device | `devices pool`, `execute parallel` | Scale |
| 11 | Smart Selection | `select --since` | CI optimization |
| 12 | Test Data | `data extract`, `data generate` | Data management |
| 13 | WebView | `generate --webview-support` | Hybrid apps |
| 14 | ML Training | `ml train`, `ml evaluate` | Accuracy |
| 15 | Integration | `framework detect`, `integrate` | Existing tests |
| 16 | Debugging | `heal suggest`, `execute record` | Troubleshooting |
| 17 | Load Testing | `execute load` | Performance |
| 18 | Dashboard | `dashboard`, `export` | Monitoring |
| 19 | Accessibility | `analyze accessibility` | Compliance |
| 20 | Continuous | `model build --merge`, `generate incremental` | Automation |

---

## API Reference

### CLI Commands

#### `observe import`

Import recorded session events.

```bash
observe import \
  --session-file <path> \
  --session-id <id> \
  --platform <android|ios> \
  [--app-package <package>]
```

#### `observe model build`

Build app model from events and static analysis.

```bash
observe model build \
  --session <id> \
  [--static-analysis <path>] \
  [--ml-model <path>] \
  --output <path> \
  [--correlation-strategy <temporal|thread|tag>] \
  [--min-confidence <float>]
```

#### `observe generate`

Generate test artifacts.

```bash
# Generate everything
observe generate all --model <path> --output <dir>

# Individual generators
observe generate pages --model <path> --output <dir>
observe generate api --model <path> --output <dir>
observe generate bdd --model <path> --output <dir>
observe generate steps --model <path> --output <dir>
```

#### `observe heal`

Self-healing commands.

```bash
# Analyze failures
observe heal analyze --test-results <junit-xml>

# Auto-heal
observe heal auto --test-results <junit-xml> [--commit] [--dry-run]

# View history
observe heal history [--limit <n>]

# Revert healing
observe heal revert <commit-hash>
```

#### `observe dashboard`

Launch maintenance dashboard.

```bash
observe dashboard [--port <port>] [--host <host>]
```

#### Full Command Reference

See `observe --help` for complete list of commands and options.

---

## Need Help?

### Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: This guide + inline code comments
- **Demo Apps**: Working examples in `demo-app/`

### Getting Support

1. **Check this guide** - Most questions answered here
2. **Search issues** - Someone might have had the same problem
3. **Open new issue** - Provide details: OS, Python version, error logs
4. **Include context** - What were you trying to do? What happened?

---

**Happy Testing!** 🚀

Remember: The best test is one that writes itself.

