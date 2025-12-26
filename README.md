# Mobile Observe & Test Framework

> **Intelligent Mobile Testing Platform** - Observe, Analyze, Automate

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Android Support](https://img.shields.io/badge/android-native%20%7C%20compose-green.svg)](demo-app/android)
[![iOS Support](https://img.shields.io/badge/ios-uikit%20%7C%20swiftui-blue.svg)](demo-app/ios)
[![Cross-Platform](https://img.shields.io/badge/cross--platform-flutter%20%7C%20react%20native-purple.svg)](#universal-ml-model)
[![Phase 5](https://img.shields.io/badge/development-phase%205%20in%20progress-yellow.svg)](#roadmap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Demo Applications](#demo-applications)
- [CLI Reference](#cli-reference)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Technology Stack](#technology-stack)

---

## Overview

Mobile Observe & Test Framework is a next-generation platform for automatic mobile test generation based on observing real user behavior. It bridges the gap between manual QA work and automated testing by intelligently converting user interactions into maintainable test code.

### How It Works

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   OBSERVE   │  →   │   ANALYZE    │  →   │  CORRELATE  │  →   │   GENERATE   │
│             │      │              │      │             │      │              │
│ QA walks    │      │ Build App    │      │ Link UI →   │      │ Page Objects │
│ through app │      │ Model from   │      │ API → Nav   │      │ API Clients  │
│ in observe  │      │ events +     │      │ using ML &  │      │ BDD Scenarios│
│ build       │      │ static code  │      │ heuristics  │      │ Test Scripts │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

### What Makes It Different

| Traditional Approach | Our Framework |
|---------------------|---------------|
| Manual selector writing | Automatic robust selector generation with fallbacks |
| UI-only tests (slow & flaky) | 80-90% API tests, 10-20% UI tests |
| Manual API endpoint discovery | Automatic network traffic analysis |
| Platform-specific tests | Cross-platform from single model |
| Breaks on UI changes | Self-healing selectors with ML |
| No flow understanding | Intelligent flow pattern recognition |

---

## Key Features

### Core Capabilities

<table>
<tr>
<td width="50%">

**Observation & Recording**
- Non-invasive SDK for Android & iOS
- Captures UI events, navigation, network calls
- WebView interaction support
- Zero impact on production builds
- Real device & emulator support

</td>
<td width="50%">

**Intelligent Analysis**
- Static code analysis (Kotlin, Swift)
- Dynamic event correlation
- ML-based element classification
- Flow pattern recognition
- API schema inference

</td>
</tr>
<tr>
<td width="50%">

**Smart Test Generation**
- Page Object pattern with robust selectors
- API-first testing approach
- pytest-bdd with Gherkin scenarios
- Cross-platform test suites
- Automatic test data extraction

</td>
<td width="50%">

**Advanced Features**
- Self-healing selectors
- Visual regression testing
- Universal ML model (no training needed)
- Analytics dashboards
- Traffic decryption for HTTPS

</td>
</tr>
</table>

### Universal ML Model

The framework includes a **pre-trained universal element classifier** that works out-of-the-box with:

- **Native Android** (View, Jetpack Compose, Material Design)
- **Native iOS** (UIKit, SwiftUI)
- **Flutter** (Dart, cross-platform)
- **React Native** (JavaScript/TypeScript, cross-platform)

**No app-specific training required** - just install and use.

### Robust Selectors

Generated selectors include:
- Primary strategy (ID, accessibility ID, name)
- 5-10 fallback strategies (XPath, CSS, text, class)
- Stability scoring (HIGH/MEDIUM/LOW)
- Automatic healing on failure
- Platform-specific optimizations

Example:
```python
LOGIN_BUTTON_SELECTOR = {
    "android": "id:login_button",
    "ios": "accessibility:loginButton",
    "android_fallback": [
        "xpath://android.widget.Button[@text='Login']",
        "xpath://android.widget.Button[contains(@text,'Log')]",
        "text:Login",
        "class:androidx.compose.material3.Button"
    ],
    "ios_fallback": [
        "xpath://XCUIElementTypeButton[@label='Login']",
        "accessibility:submit_button",
        "text:Login"
    ],
    "stability": "high"
}
```

---

## Architecture

### High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         CLI / Orchestrator                                │
│                    (Python Click, Single Entry Point)                     │
└───────────────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌────────────────┐          ┌────────────────┐
│    Static     │          │    Observe     │          │  Correlation   │
│   Analyzer    │          │    Runtime     │          │     Engine     │
│               │          │     (SDK)      │          │                │
│ • Android     │          │                │          │ • UI → API     │
│ • iOS         │          │ • Android SDK  │          │ • API → Nav    │
│ • Tree-sitter │          │ • iOS SDK      │          │ • 5 strategies │
│               │          │ • WebView      │          │ • ML scoring   │
└───────────────┘          └────────────────┘          └────────────────┘
        │                            │                            │
        └────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
                    ┌────────────────────────────┐
                    │      App Model Core        │
                    │                            │
                    │ • Screens & Elements       │
                    │ • Actions & Transitions    │
                    │ • API Calls & Schemas      │
                    │ • State Machine            │
                    │ • Flows & Preconditions    │
                    └────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌───────────────┐          ┌────────────────┐          ┌────────────────┐
│  Generators   │          │   ML / AI      │          │   Analytics    │
│               │          │                │          │                │
│ • Page        │          │ • Classifier   │          │ • Dashboards   │
│   Objects     │          │ • Healing      │          │ • Reports      │
│ • API Clients │          │ • Visual Diff  │          │ • Metrics      │
│ • BDD Tests   │          │ • Patterns     │          │ • Coverage     │
└───────────────┘          └────────────────┘          └────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **CLI** | Python Click | Single entry point for all operations |
| **App Model** | Pydantic | Canonical representation of app structure |
| **Event Store** | SQLite | Persistent storage for captured events |
| **Static Analyzer** | tree-sitter | Parse source code without compilation |
| **Observe SDK (Android)** | Kotlin | Capture UI/network events in Android apps |
| **Observe SDK (iOS)** | Swift | Capture UI/network events in iOS apps |
| **Correlation Engine** | Python | Link UI → API → Navigation intelligently |
| **Generators** | Jinja2 | Templated code generation |
| **ML Classifier** | scikit-learn | Element type prediction |
| **Selector Builder** | Python | Multi-strategy robust selectors |

---

## Quick Start

### Prerequisites

```
Required:
  • Python 3.13+
  • Android SDK (for Android demo)
  • Xcode 14+ (for iOS demo)
  • Java 17+ (for Android builds)

Optional:
  • Android Studio / IntelliJ IDEA
  • Xcode
  • ADB tools
```

### Installation

```bash
# 1. Clone or navigate to project
cd mobile_test_recorder

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install CLI in editable mode
pip install -e .

# 5. Verify installation
observe --help
observe info
```

### Build Demo Apps

#### Android

```bash
cd demo-app/android

# Build observe variant (with SDK)
./gradlew assembleObserveDebug

# Build test variant (without SDK)
./gradlew assembleTestDebug

# Install on device/emulator
./gradlew installObserveDebug

# Check installed packages
adb shell pm list packages | grep findemo
```

#### iOS

```bash
cd demo-app/ios

# Open in Xcode
open FinDemo/FinDemo.xcodeproj

# Select Observe scheme
# Product → Scheme → Observe

# Build and run (⌘R)
# Or build from command line:
xcodebuild -scheme Observe -configuration Debug -sdk iphonesimulator
```

### First Recording Session

```bash
# 1. Initialize project
observe init --platform android

# 2. Start mock backend (optional)
cd demo-app/mock-backend
pip install -r requirements.txt
python main.py &

# 3. Start recording
observe record start --device emulator-5554 --package com.findemo.observe

# 4. Use the app
#    - Complete onboarding
#    - Login
#    - Navigate through screens
#    - Perform transactions

# 5. Stop recording
observe record stop --device emulator-5554 --package com.findemo.observe

# 6. Import events
observe record import --input observe_events.json

# 7. Correlate events
observe record correlate --session <session-id>

# 8. Build app model
observe model build --session <session-id> --output app_model.json

# 9. Generate tests
observe generate pages --model app_model.json --output tests/pages/
observe generate api --model app_model.json --output tests/api/
observe generate features --model app_model.json --output tests/features/
```

---

## Demo Applications

Both Android and iOS demo apps implement a **production-grade fintech application** (inspired by Revolut/Wise) with comprehensive security features.

### Features Implemented

<table>
<tr>
<th>Feature</th>
<th>Android</th>
<th>iOS</th>
<th>Description</th>
</tr>
<tr>
<td>Onboarding</td>
<td>✓</td>
<td>✓</td>
<td>Swipeable welcome screens</td>
</tr>
<tr>
<td>Authentication</td>
<td>✓</td>
<td>✓</td>
<td>Login with biometrics support</td>
</tr>
<tr>
<td>KYC</td>
<td>✓</td>
<td>✓</td>
<td>Document scanning (Regula SDK)</td>
</tr>
<tr>
<td>Home Screen</td>
<td>✓</td>
<td>✓</td>
<td>Balance, cards, quick actions</td>
</tr>
<tr>
<td>Top-up</td>
<td>✓</td>
<td>✓</td>
<td>Card payment via WebView</td>
</tr>
<tr>
<td>Send Money</td>
<td>✓</td>
<td>✓</td>
<td>P2P transfers</td>
</tr>
<tr>
<td>Multi-currency</td>
<td>✓</td>
<td>✓</td>
<td>20+ currencies, exchange</td>
</tr>
<tr>
<td>Cards</td>
<td>✓</td>
<td>✓</td>
<td>Virtual/physical card management</td>
</tr>
</table>

### Security Features

Both apps include **production-grade security**:

- Certificate pinning (bypass-able in observe builds)
- Root/jailbreak detection
- Secure storage (Keystore/Keychain)
- Biometric authentication
- Code obfuscation (ProGuard/R8)
- Traffic encryption with key export for testing

See [Android Security Guide](demo-app/android/observe-sdk/SECURITY.md) for details on crypto key export and traffic decryption.

### Build Variants

| Variant | SDK Included | Purpose | Security |
|---------|--------------|---------|----------|
| **observe** | ✓ | Recording sessions | Bypassed |
| **test** | ✗ | Automated tests | Minimal |
| **production** | ✗ | Production release | Full |

**Important:** The observe SDK is **completely isolated** from production builds using Gradle flavors (Android) and Xcode schemes (iOS).

---

## CLI Reference

### Main Commands

```bash
observe init          # Initialize project
observe info          # Show project info
observe analyze       # Static code analysis
observe record        # Record user sessions
observe model         # Manage app model
observe generate      # Generate test code
observe ml            # Machine learning features
observe crypto        # Crypto key management (Android)
```

### Recording Workflow

```bash
# Start recording
observe record start --device <device-id> --package <package-name>

# Stop recording
observe record stop --device <device-id> --package <package-name>

# Import events
observe record import --input <events.json>

# List sessions
observe record list

# Show session details
observe record show --session <session-id>

# Correlate events
observe record correlate --session <session-id>
```

### Model Management

```bash
# Build model from session
observe model build --session <session-id> --output model.json

# Build with ML classifier
observe model build --session <session-id> --use-ml --output model.json

# Validate model
observe model validate --model model.json

# Show model diff
observe model diff --model1 old.json --model2 new.json

# Analyze selectors
observe model analyze-selectors --model model.json
```

### Code Generation

```bash
# Generate Page Objects
observe generate pages --model model.json --output tests/pages/

# Generate API clients
observe generate api --model model.json --output tests/api/

# Generate BDD features
observe generate features --model model.json --output tests/features/
```

### ML Features

```bash
# Create universal model (no training data needed)
observe ml create-universal-model --output ml_models/universal.pkl

# Analyze flow patterns
observe ml analyze-patterns --session <session-id>

# Heal broken selectors
observe ml heal-selectors --page-object tests/pages/login.py

# Visual diff
observe ml visual-diff --screenshot1 before.png --screenshot2 after.png

# Generate analytics report
observe ml report --model model.json --output report.html

# Show fallback statistics
observe ml fallback-stats --page-object tests/pages/
```

### Static Analysis

```bash
# Analyze Android project
observe analyze android --source demo-app/android --output analysis.json

# Analyze iOS project
observe analyze ios --source demo-app/ios --output analysis.json
```

### Crypto Key Management (Android)

```bash
# Pull all crypto keys from device
observe crypto pull --device <device-id> --package <package-name>

# Show key statistics
observe crypto show --device <device-id> --package <package-name>

# Export keys for Wireshark
observe crypto export --input crypto_keys.json --format nss-keylog
```

For detailed usage, see [USAGE_GUIDE.md](USAGE_GUIDE.md).

---

## Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [RFC Specification](mobile_observe_test_framework_RFC.md) | Complete technical specification |
| [Usage Guide](USAGE_GUIDE.md) | Step-by-step workflows and examples |

### Demo Application

| Document | Description |
|----------|-------------|
| [Demo App Overview](demo-app/README.md) | Features and setup guide |
| [KYC Integration](demo-app/android/KYC_INTEGRATION.md) | Regula SDK integration details |
| [Mock Backend API](demo-app/mock-backend/README.md) | API endpoints and mock data |
| [XPath Test Elements](demo-app/XPATH_TEST_ELEMENTS.md) | Elements without IDs for XPath testing |

### SDK Documentation

| Document | Description |
|----------|-------------|
| [Android SDK Security](demo-app/android/observe-sdk/SECURITY.md) | Crypto keys & traffic decryption |
| [iOS SDK Guide](demo-app/ios/ObserveSDK/README.md) | iOS SDK integration guide |

### Technical References

| Document | Description |
|----------|-------------|
| [Element Selectors Guide](docs/ELEMENT_SELECTORS_COMPREHENSIVE.md) | All selector types (Android/iOS/Flutter/RN) |
| [Enhanced Selectors](docs/ENHANCED_SELECTORS.md) | Multi-strategy selector generation |
| [Universal ML Model](docs/UNIVERSAL_ML_MODEL.md) | Pre-trained element classifier |

---

## Roadmap

### Phase 1: MVP (6-8 weeks) - ✓ 100% COMPLETE

**Core Infrastructure & Android Foundation**

<details>
<summary>View Phase 1 Deliverables</summary>

- [x] Project structure & setup
- [x] Python 3.13+ virtual environment
- [x] CLI framework (Click)
- [x] App Model Core (Pydantic schemas)
- [x] Demo Android App (Jetpack Compose)
  - [x] Onboarding screens (swipeable)
  - [x] Login with validation
  - [x] KYC with Regula SDK
  - [x] Home screen with balance
  - [x] Top-up flow with WebView
  - [x] Send Money multi-step flow
  - [x] Full navigation graph
- [x] Mock Backend API (FastAPI)
  - [x] Authentication endpoints
  - [x] Account management
  - [x] Transaction APIs
- [x] Android Observe SDK
  - [x] UIObserver (tap, swipe, input)
  - [x] NavigationObserver (screen tracking)
  - [x] NetworkObserver (OkHttp interceptor)
  - [x] EventExporter (JSON files)
  - [x] EventBus & session management
- [x] Event Store (SQLite)
  - [x] Schema & indexing
  - [x] Import/export
  - [x] Query API with filters
  - [x] Session tracking
- [x] Code Generators
  - [x] Page Object generator
  - [x] API client generator
  - [x] pytest-bdd generator
  - [x] Jinja2 templates
  - [x] CLI integration

**Lines of Code:** ~15,000  
**Duration:** 8 weeks

</details>

### Phase 2: Production Ready (4-6 weeks) - ✓ 100% COMPLETE

**Event Correlation & Model Building**

<details>
<summary>View Phase 2 Deliverables</summary>

- [x] Event Correlation Engine
  - [x] UI → API correlation (5 strategies)
  - [x] API → Navigation correlation
  - [x] Full flow generation
  - [x] Confidence scoring
  - [x] CLI: `observe record correlate`
- [x] Automatic Model Builder
  - [x] Generate AppModel from events
  - [x] Screen inference from navigation
  - [x] Element extraction from hierarchy
  - [x] API schema building
  - [x] Flow generation
  - [x] State machine construction
  - [x] CLI: `observe model build`
- [x] HierarchyCollector
  - [x] Full UI hierarchy capture
  - [x] Android View + Compose support
  - [x] Element attribute extraction
  - [x] Parent-child relationships
- [x] Android Static Analyzer
  - [x] Kotlin/Gradle parsing (tree-sitter)
  - [x] Compose UI detection
  - [x] Navigation routes extraction
  - [x] Retrofit API discovery
  - [x] Test tag extraction
  - [x] CLI: `observe analyze android`
- [x] Advanced Selector Strategies
  - [x] Stability scoring (HIGH/MEDIUM/LOW)
  - [x] Intelligent selector builder
  - [x] Selector optimizer
  - [x] Fallback chain generation (5-10 fallbacks)
  - [x] Duplicate detection
  - [x] CLI: `observe model analyze-selectors`
- [x] Documentation
  - [x] Complete usage guide
  - [x] Workflow examples
  - [x] Best practices

**Lines of Code:** ~12,000  
**Duration:** 6 weeks

</details>

### Phase 3: iOS Support (6-8 weeks) - ✓ 100% COMPLETE

**Full Cross-Platform Capability**

<details>
<summary>View Phase 3 Deliverables</summary>

- [x] iOS Demo App (SwiftUI)
  - [x] Onboarding with TabView
  - [x] Login screen
  - [x] KYC screen (mock scanning)
  - [x] Home with balance
  - [x] Top-up with WKWebView
  - [x] Send Money flow
  - [x] Full accessibility identifiers
- [x] iOS Observe SDK (Swift)
  - [x] UIObserver (UIKit + SwiftUI)
  - [x] NavigationObserver
  - [x] NetworkObserver (URLProtocol)
  - [x] HierarchyCollector (UIView traversal)
  - [x] EventExporter (JSON)
  - [x] Combine-based EventBus
- [x] iOS Static Analyzer
  - [x] Swift/SwiftUI parsing
  - [x] View hierarchy analysis
  - [x] Accessibility identifier extraction
  - [x] Navigation route discovery
  - [x] URLSession API detection
  - [x] CLI: `observe analyze ios`
- [x] Cross-Platform Generators
  - [x] Page Objects (Android + iOS selectors)
  - [x] API clients (platform-agnostic)
  - [x] BDD features (unified Gherkin)
  - [x] Platform detection in code
- [x] Production-Grade Security
  - [x] Certificate pinning (Android + iOS)
  - [x] Root/jailbreak detection
  - [x] Secure storage (Keystore/Keychain)
  - [x] Biometric authentication
  - [x] Code obfuscation
  - [x] Traffic encryption
  - [x] Crypto key export for testing
  - [x] Traffic decryption utility

**Lines of Code:** ~18,000  
**Duration:** 8 weeks  
**Feature Parity:** 100% (Android ↔ iOS)

</details>

### Phase 4: AI/ML & Advanced Features (8-10 weeks) - ✓ 100% COMPLETE

**Intelligence & Automation**

<details>
<summary>View Phase 4 Deliverables</summary>

- [x] Universal Pre-Trained ML Model
  - [x] 2500+ synthetic training samples
  - [x] Native Android support (View, Compose, Material Design)
  - [x] Native iOS support (UIKit, SwiftUI)
  - [x] Flutter support (Dart, widgets)
  - [x] React Native support (JS/TS, components)
  - [x] >85% accuracy across all platforms
  - [x] No app-specific training required
  - [x] One-command setup
  - [x] CLI: `observe ml create-universal-model`
- [x] ML-Based Element Classification
  - [x] Element type prediction
  - [x] Confidence-based fallback to rules
  - [x] Integration into ModelBuilder
  - [x] CLI: `observe model build --use-ml`
- [x] Visual Element Detection
  - [x] Screenshot capture & processing
  - [x] Image similarity (SSIM, MSE, Histogram)
  - [x] OCR integration (Tesseract)
  - [x] Visual regression testing
  - [x] Template matching (OpenCV)
  - [x] CLI: `observe ml visual-diff`
- [x] Smart Selector Healing
  - [x] Broken selector detection
  - [x] Alternative selector generation
  - [x] Self-healing test scripts
  - [x] 5 healing strategies with prioritization
  - [x] Healing statistics tracking
  - [x] Automatic model updates
  - [x] CLI: `observe ml heal-selectors`
- [x] Flow Pattern Recognition
  - [x] Common flow detection
  - [x] Critical path identification
  - [x] Test scenario suggestions
  - [x] Anomaly detection (dead ends, loops)
  - [x] Sequential pattern mining
  - [x] Automatic Gherkin generation
  - [x] CLI: `observe ml analyze-patterns`
- [x] Analytics Dashboard
  - [x] Interactive HTML reports (Plotly)
  - [x] Test execution metrics
  - [x] Coverage analysis (screens, flows, APIs)
  - [x] Selector stability reports
  - [x] Visual charts & gauges
  - [x] Trend analysis
  - [x] CLI: `observe ml report`
- [x] WebView Support
  - [x] JavaScript injection for DOM observation
  - [x] Enhanced selector generation (10+ strategies)
  - [x] Page reload handling
  - [x] Android WebView observer
  - [x] iOS WKWebView observer
  - [x] Non-invasive delegation pattern
  - [x] Resource leak prevention

**Lines of Code:** ~15,000  
**Duration:** 10 weeks  
**ML Model Size:** 2.1 MB  
**Training Samples:** 2500

</details>

### Phase 5: Enterprise Integration & Deep Analysis (12-16 weeks) - 🚧 IN PROGRESS

**Existing Project Integration, Multi-Environment, & Advanced Analysis**

<details>
<summary>View Phase 5 Features</summary>

- [x] **Project Integration** (`observe framework`)
  - [x] Existing test project detector
  - [x] Structure analysis (Page Objects, tests, fixtures)
  - [x] Framework detection (pytest, unittest, Robot, behave)
  - [x] Code style analyzer
  - [x] Coverage analysis
  - [x] Integration recommendations
  - [ ] Adaptive code generator (matches existing style)
  - [ ] Side-by-side test execution

- [ ] **Device Management** (`observe devices`)
  - [ ] Unified device interface (Android + iOS)
  - [ ] Auto-detect connected devices (ADB, instruments)
  - [ ] Emulator/Simulator management
  - [ ] Device pool system
  - [ ] Health checks & recovery
  - [ ] Load balancing for parallel execution

- [ ] **Cloud Platform Integration**
  - [ ] BrowserStack API integration
  - [ ] Sauce Labs support
  - [ ] AWS Device Farm support
  - [ ] Automatic session management
  - [ ] APK/IPA upload
  - [ ] Video recording & logs

- [ ] **CI/CD Integration** (`observe ci`)
  - [ ] GitHub Actions workflow generator
  - [ ] GitLab CI pipeline generator
  - [ ] Jenkins Jenkinsfile generator
  - [ ] CircleCI config generator
  - [ ] Azure Pipelines YAML generator
  - [ ] Artifact management
  - [ ] PR commenting
  - [ ] Test impact analysis

- [ ] **Advanced Reporting** (`observe report`)
  - [ ] Enhanced HTML dashboard (v2)
  - [ ] Allure report integration
  - [ ] JUnit XML for CI
  - [ ] PDF summary reports
  - [ ] Historical trends & analytics
  - [ ] Flaky test detection
  - [ ] TestRail/Zephyr/qTest integration

- [ ] **Notification System** (`observe notify`)
  - [ ] Slack integration
  - [ ] Microsoft Teams integration
  - [ ] Email notifications
  - [ ] Telegram bot
  - [ ] Custom webhooks
  - [ ] Configurable templates

- [ ] **Smart Test Execution** (`observe test`)
  - [ ] Test selection (changed code only)
  - [ ] Execution modes (smoke, regression, exploratory)
  - [ ] Smart retry strategies
  - [ ] Test sharding
  - [ ] Mixed local + cloud execution
  - [ ] Performance testing mode

- [ ] **Comprehensive Analysis** (`observe analyze`)
  - [ ] Security scanner (OWASP Mobile Top 10)
  - [ ] Performance profiler (CPU, memory, network)
  - [ ] Visual diff system
  - [ ] Architecture visualizer
  - [ ] Dependency vulnerability scanner
  - [ ] Accessibility checker

</details>

**Status**: Framework detection and project analysis complete. Device management in progress.

**Lines of Code (estimated):** ~18,000  
**Duration:** ~12 weeks (3 months)

---

### Phase 6: Future Enhancements

**Planned Features**

- [ ] CI/CD Integration
  - [ ] Jenkins plugin
  - [ ] GitHub Actions workflow
  - [ ] GitLab CI templates
- [ ] Test Management Integration
  - [ ] TestRail sync
  - [ ] Xray integration
  - [ ] Allure reports
- [ ] Web Support
  - [ ] Selenium/Playwright integration
  - [ ] Browser automation
  - [ ] Responsive testing
- [ ] Performance Testing
  - [ ] Load time analysis
  - [ ] Memory profiling
  - [ ] Battery consumption
- [ ] Advanced ML Models
  - [ ] Deep learning for element detection
  - [ ] NLP for test generation
  - [ ] Anomaly detection in flows
- [ ] Test Data Management
  - [ ] Synthetic data generation
  - [ ] Test data masking
  - [ ] State restoration

---

## Technology Stack

### Framework (Python)

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.13+ |
| **CLI** | Click | 8.x |
| **Models** | Pydantic | 2.x |
| **Templates** | Jinja2 | 3.x |
| **Testing** | pytest, pytest-bdd | Latest |
| **Automation** | Appium, Selenium | Latest |
| **ML/AI** | scikit-learn, numpy, pandas | Latest |
| **Image Processing** | Pillow, OpenCV, Tesseract | Latest |
| **Visualization** | matplotlib, seaborn, plotly | Latest |
| **Database** | SQLite, SQLAlchemy | Latest |
| **HTTP** | requests, FastAPI | Latest |
| **Parsing** | tree-sitter, lxml | Latest |

### Android SDK (Kotlin)

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Kotlin | 1.9+ |
| **UI** | Jetpack Compose | 1.5+ |
| **Navigation** | Compose Navigation | Latest |
| **Networking** | OkHttp, Retrofit | Latest |
| **Storage** | Room, SQLite | Latest |
| **Coroutines** | Kotlin Coroutines | 1.7+ |
| **Security** | Android Keystore, Biometric | Latest |
| **KYC** | Regula Document Reader | Latest |
| **Build** | Gradle | 8.x |

### iOS SDK (Swift)

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Swift | 5.9+ |
| **UI** | SwiftUI, UIKit | iOS 16+ |
| **Navigation** | NavigationStack | iOS 16+ |
| **Networking** | URLSession, Alamofire | Latest |
| **Storage** | CoreData, UserDefaults | Latest |
| **Reactive** | Combine | Latest |
| **Security** | Keychain, LocalAuthentication | Latest |
| **Build** | Xcode | 14+ |

### Demo Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | Latest |
| **Server** | Uvicorn | Latest |
| **Validation** | Pydantic | 2.x |

---

## Project Structure

```
mobile_test_recorder/
├── demo-app/                          # Demo Applications
│   ├── android/                       # Android Fintech App
│   │   ├── app/                       # Main application module
│   │   │   ├── src/
│   │   │   │   ├── main/              # Shared code
│   │   │   │   ├── observe/           # Observe build variant
│   │   │   │   ├── test/              # Test build variant
│   │   │   │   └── production/        # Production build variant
│   │   │   └── build.gradle.kts
│   │   ├── observe-sdk/               # Android Observe SDK
│   │   │   └── src/main/java/com/observe/sdk/
│   │   │       ├── ObserveSDK.kt      # Main SDK entry point
│   │   │       ├── core/              # Configuration & session
│   │   │       ├── events/            # Event definitions
│   │   │       ├── observers/         # UI, Network, Navigation observers
│   │   │       ├── export/            # Event exporter
│   │   │       └── security/          # Crypto & security features
│   │   ├── KYC_INTEGRATION.md
│   │   └── README.md
│   ├── ios/                           # iOS Fintech App
│   │   ├── FinDemo/                   # Main Xcode project
│   │   │   ├── FinDemo.xcodeproj
│   │   │   └── FinDemo/               # Source code
│   │   │       ├── Views/             # SwiftUI views
│   │   │       ├── Models/            # Data models
│   │   │       └── Assets.xcassets
│   │   └── ObserveSDK/                # iOS Observe SDK
│   │       ├── ObserveSDK.swift       # Main SDK entry point
│   │       ├── Core/                  # Configuration & session
│   │       ├── Events/                # Event definitions
│   │       ├── Observers/             # UI, Network, Navigation observers
│   │       └── Export/                # Event exporter
│   ├── mock-backend/                  # FastAPI Mock Server
│   │   ├── main.py                    # API implementation
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── README.md                      # Demo app overview
│   └── XPATH_TEST_ELEMENTS.md         # Test elements without IDs
│
├── framework/                         # Core Framework (Python)
│   ├── cli/                           # Command-line interface
│   │   └── main.py                    # CLI entry point (Click)
│   ├── model/                         # App Model Core
│   │   └── app_model.py               # Pydantic schemas
│   ├── storage/                       # Event persistence
│   │   └── event_store.py             # SQLite storage
│   ├── analyzers/                     # Static code analysis
│   │   ├── android_analyzer.py        # Android/Kotlin parser
│   │   └── ios_analyzer.py            # iOS/Swift parser
│   ├── correlation/                   # Event correlation
│   │   ├── correlator.py              # Main engine
│   │   ├── strategies.py              # Correlation strategies
│   │   └── types.py                   # Result types
│   ├── model_builder/                 # Automatic model building
│   │   └── builder.py                 # Build AppModel from events
│   ├── generators/                    # Code generation
│   │   ├── page_object_gen.py         # Page Object generator
│   │   ├── api_client_gen.py          # API client generator
│   │   └── bdd_gen.py                 # BDD feature generator
│   ├── selectors/                     # Selector strategies
│   │   ├── selector_builder.py        # Multi-strategy builder
│   │   ├── selector_scorer.py         # Stability scoring
│   │   └── selector_optimizer.py      # Optimization & deduplication
│   ├── ml/                            # Machine Learning features
│   │   ├── element_classifier.py      # ML element classifier
│   │   ├── universal_model.py         # Universal pre-trained model
│   │   ├── selector_healer.py         # Self-healing selectors
│   │   ├── visual_detector.py         # Visual element detection
│   │   ├── pattern_analyzer.py        # Flow pattern recognition
│   │   ├── analytics_dashboard.py     # Interactive reports
│   │   └── training_data_generator.py # Synthetic training data
│   └── security/                      # Security & crypto
│       └── traffic_decryptor.py       # Decrypt captured traffic
│
├── ml_models/                         # Machine Learning Models
│   ├── universal_element_classifier.pkl   # Pre-trained universal model
│   └── training_metadata.json         # Model metadata
│
├── docs/                              # Documentation
│   ├── ELEMENT_SELECTORS_COMPREHENSIVE.md   # Selector reference
│   ├── ENHANCED_SELECTORS.md          # Multi-strategy selectors
│   └── UNIVERSAL_ML_MODEL.md          # ML model documentation
│
├── tests/                             # Generated Tests (Example)
│   ├── pages/                         # Page Objects
│   ├── api/                           # API clients
│   └── features/                      # BDD features
│
├── .venv/                             # Python virtual environment
├── requirements.txt                   # Python dependencies
├── pyproject.toml                     # Python project config
├── README.md                          # This file
├── USAGE_GUIDE.md                     # Complete usage guide
└── mobile_observe_test_framework_RFC.md   # Technical specification
```

**Total Lines of Code:** ~60,000  
**Languages:** Python, Kotlin, Swift  
**Platforms:** Android, iOS, CLI

---

## Contributing

This is currently a private project. For contribution guidelines or access requests, please contact the maintainer.

---

## License

MIT License

Copyright (c) 2025 Vadim Toptunov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Author

**Vadim Toptunov**

*Built for QA Engineers who deserve better tools.*

---

## Acknowledgments

- Inspired by real-world testing challenges in fintech
- Designed to handle legacy code and complex UI scenarios
- Built with modern technologies: Jetpack Compose, SwiftUI, Python 3.13
- Special thanks to the open-source community for excellent libraries

---

## Support & Contact

For questions, bug reports, or feature requests, please contact the maintainer.

---

**Last Updated:** December 2025  
**Current Phase:** Phase 4 Complete  
**Status:** Production Ready
