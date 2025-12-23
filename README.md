# 🎯 Mobile Observe & Test Framework

**Intelligent Mobile Testing Platform** - Observe, Analyze, Automate

---

## 📖 Overview

Mobile Observe & Test Framework is a platform for automatic generation of mobile application tests based on observing real user behavior.

### What does it do?

1. **Observe** 👀 - Records QA engineer actions in a special build of the application
2. **Analyze** 🧠 - Creates a semantic model of the application (screens, elements, transitions, APIs)
3. **Correlate** 🔗 - Intelligently links UI events with API calls and navigation
4. **Generate** ⚡ - Automatically generates Page Objects, API tests, and BDD scenarios
5. **Execute** 🚀 - Runs tests on a clean build (without SDK)

### Key Benefits

- ✅ **Minimal Manual Work** - QA engineers just walk through scenarios, tests generate automatically
- ✅ **Intelligent Correlation** - Automatically discovers relationships between UI, API, and navigation
- ✅ **80-90% API Tests** - Fast and stable tests instead of slow UI
- ✅ **Cross-platform Selectors** - Android and iOS from single model
- ✅ **Smart Fallbacks** - Automatic handling of fragile locators
- ✅ **Complex Cases Support** - Swipe, WebView, dynamic UI, hierarchy capture

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────┐
│              CLI / Orchestrator             │
└──────────────┬─────────────────────────────┘
               │
┌──────────────┴─────────────────────────────┐
│        Knowledge Acquisition                │
│  ┌──────────────┐  ┌────────────────────┐  │
│  │ Static       │  │ Observe Runtime    │  │
│  │ Analyzer     │  │ (Android / iOS)    │  │
│  └──────────────┘  └────────────────────┘  │
└──────────────┬─────────────────────────────┘
               │
┌──────────────┴─────────────────────────────┐
│            App Model Core                   │
│   (Screens, States, APIs, Flows)            │
└──────────────┬─────────────────────────────┘
               │
┌──────────────┴─────────────────────────────┐
│          Generators Layer                   │
│  (Python, pytest-bdd, Appium, API)          │
└──────────────┬─────────────────────────────┘
               │
┌──────────────┴─────────────────────────────┐
│      Execution & Reporting Layer            │
│       (Stage builds, CI, TestRail)          │
└─────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
mobile_test_recorder/
├── demo-app/                    # Demo Fintech application
│   ├── android/                 # Android demo app (Jetpack Compose)
│   │   ├── app/
│   │   │   ├── src/
│   │   │   │   ├── main/       # Main code
│   │   │   │   ├── observe/    # Observe build variant
│   │   │   │   └── test/       # Test build variant
│   │   │   └── build.gradle.kts
│   │   └── observe-sdk/         # Android Observe SDK
│   │       └── src/
│   ├── ios/                     # iOS demo app (SwiftUI) ✅
│   └── mock-backend/            # Mock API server
│       └── main.py
│
├── framework/                   # Core Framework
│   ├── cli/                     # CLI interface
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── commands/
│   │       ├── analyze.py
│   │       ├── observe.py
│   │       ├── generate.py
│   │       └── model.py
│   │
│   ├── analyzer/                # Static Analysis
│   │   ├── android_analyzer.py
│   │   └── ios_analyzer.py
│   │
│   ├── model/                   # App Model Core
│   │   ├── app_model.py
│   │   ├── schema.py
│   │   ├── state_machine.py
│   │   └── diff_engine.py
│   │
│   ├── correlation/             # Event Correlation
│   │   ├── correlation_engine.py
│   │   └── strategies.py
│   │
│   ├── storage/                 # Event Store
│   │   ├── event_store.py
│   │   └── sqlite_adapter.py
│   │
│   └── generators/              # Code Generators
│       ├── page_object_gen.py
│       ├── api_client_gen.py
│       ├── selector_gen.py
│       └── bdd_gen.py
│
├── tests/                       # Generated tests (example)
│   ├── pages/
│   ├── api/
│   └── features/
│
├── docs/                        # Documentation
│   ├── architecture.md
│   ├── roadmap.md
│   └── examples/
│
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Python project config
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+ (tested with 3.13.11)
- Android SDK (for demo app)
- Java 17+ (for Android)
- Android Studio or IntelliJ IDEA
- Node.js (for mock backend, optional)

### Installation

```bash
# Clone repository (or navigate to existing)
cd mobile_test_recorder

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Or use the activation script
source activate.sh

# Install Python dependencies
pip install -r requirements.txt

# Install CLI in editable mode
pip install -e .

# Verify installation
observe --help
observe info
```

### Build Demo App

```bash
# Open Android project
# File → Open → demo-app/android in Android Studio

# OR build from command line:
cd demo-app/android

# Build observe variant (with Observe SDK)
./gradlew assembleObserveDebug

# Build test variant (clean, for automation)
./gradlew assembleTestDebug

# Install on device/emulator
adb install app/build/outputs/apk/observe/debug/app-observe-debug.apk

# Run on connected device
./gradlew installObserveDebug
```

### Demo App Features

✅ **Onboarding** - Swipeable welcome screens  
✅ **Login** - Email/password authentication  
✅ **KYC** - Document scanning with Regula SDK  
✅ **Home** - Balance and quick actions  
🚧 **Top-up** - Card top-up with WebView (coming soon)  
🚧 **Send Money** - Transfer to friends (coming soon)

**Note:** KYC camera works best on real device. Use "Skip" button for emulator testing.

### Run Framework

```bash
# Initialize project
observe init --platform android

# Analyze source code (optional)
observe analyze android --source demo-app/android

# Start recording session
observe record start --device emulator-5554

# (Use the app - tap, swipe, input text)

# Stop recording
observe record stop

# Generate Page Objects
observe generate pages --output tests/pages/

# Generate tests
observe generate tests --output tests/
```

---

## 📚 Documentation

- [RFC Specification](mobile_observe_test_framework_RFC.md) - Full technical specification
- [Demo App Overview](demo-app/README.md) - Demo app features and setup
- [KYC Integration Guide](demo-app/android/KYC_INTEGRATION.md) - Regula SDK integration
- [Mock Backend API](demo-app/mock-backend/README.md) - Backend API documentation
- [Getting Started](GETTING_STARTED.md) - Quick start guide

---

## 🎯 Roadmap

### ✅ Phase 1: MVP (6-8 weeks) - 100% COMPLETE! 🎉
- [x] Project structure
- [x] Python virtual environment setup (3.13)
- [x] CLI framework (Click)
- [x] App Model Core (Pydantic)
- [x] Demo Android App ✅
  - [x] Onboarding (swipeable screens)
  - [x] Login screen
  - [x] KYC screen with Regula SDK
  - [x] Home screen
  - [x] Top-up with WebView
  - [x] Send Money flow
  - [x] Full navigation
- [x] Mock Backend API (FastAPI)
- [x] Android Observe SDK (90%)
  - [x] UIObserver (full implementation)
  - [x] NavigationObserver (full implementation)
  - [x] NetworkObserver (OkHttp interceptor)
  - [x] EventExporter (JSON export)
  - [x] EventBus & Session management
- [x] Event Store (SQLite) ✅
  - [x] SQLite schema & indexing
  - [x] Event import/export
  - [x] Query API with filters
  - [x] Session management
  - [x] Session tracking
  - [x] Query API
- [x] Code Generators ✅
  - [x] Page Object Generator
  - [x] API Client Generator
  - [x] pytest-bdd Generator
  - [x] Jinja2 templates
  - [x] CLI integration

### ✅ Phase 2: Production Ready (4-6 weeks) - 100% COMPLETE! 🎉
- [x] **Event Correlation Engine** ✅
  - [x] UI → API correlation (5 strategies)
  - [x] API → Navigation correlation
  - [x] Full flow generation
  - [x] Confidence scoring
  - [x] CLI command: `observe record correlate`
- [x] **Automatic Model Builder** ✅
  - [x] Generate AppModel from events
  - [x] Screen inference
  - [x] Element extraction
  - [x] API schema building
  - [x] Flow generation
  - [x] State machine construction
  - [x] CLI command: `observe model build`
- [x] **HierarchyCollector** ✅
  - [x] Full UI hierarchy capture
  - [x] View + Compose support
  - [x] Element attribute extraction
  - [x] Parent-child relationships
- [x] **Android Static Analyzer** ✅
  - [x] Kotlin source code parsing
  - [x] Compose UI detection
  - [x] Navigation routes extraction
  - [x] Retrofit API discovery
  - [x] Test tag extraction
  - [x] CLI command: `observe analyze android`
- [x] **Documentation** ✅
  - [x] Complete usage guide
  - [x] Workflow examples
  - [x] Best practices
- [x] **Advanced Selector Strategies** ✅
  - [x] Selector stability scoring
  - [x] Intelligent selector builder
  - [x] Selector optimizer
  - [x] Fallback chain generation
  - [x] Duplicate detection
  - [x] CLI command: `observe model analyze-selectors`

### ✅ Phase 3: iOS Support (6-8 weeks) - 100% COMPLETE! 🍎
- [x] **iOS Demo App** ✅
  - [x] SwiftUI implementation
  - [x] Onboarding (swipeable TabView)
  - [x] Login screen
  - [x] KYC screen (mock scanning)
  - [x] Home screen with balance
  - [x] Top-up with WebView payment
  - [x] Send Money flow
  - [x] Full accessibility identifiers
- [x] **iOS Observe SDK** ✅
  - [x] Swift SDK architecture
  - [x] UIObserver (UIKit + SwiftUI)
  - [x] NavigationObserver
  - [x] NetworkObserver (URLProtocol)
  - [x] HierarchyCollector
  - [x] EventExporter (JSON)
  - [x] Combine-based EventBus
- [x] **iOS Static Analyzer** ✅
  - [x] Swift/SwiftUI parsing
  - [x] View hierarchy analysis
  - [x] Accessibility identifier extraction
  - [x] Navigation route discovery
  - [x] API endpoint detection
  - [x] CLI command: `observe analyze ios`
- [x] **Cross-platform Generators** ✅
  - [x] Page Object generator (Android + iOS selectors)
  - [x] API client generator (platform-agnostic)
  - [x] BDD generator (unified Gherkin)
  - [x] Platform detection in generated code

### 🔮 Phase 4: Advanced Features
- [ ] ML-based element classification
- [ ] Visual regression testing
- [ ] CI/CD integration
- [ ] TestRail integration
- [ ] Web support (optional)

---

## 🤝 Contributing

This is currently a private project. Contact the maintainer for contribution guidelines.

---

## 📄 License

TBD

---

## 👤 Author

**Vadim Toptunov**

Built with ❤️ for QA Engineers who deserve better tools.

---

## 🙏 Acknowledgments

- Inspired by production testing challenges in fintech
- Built with modern tech stack (Compose, SwiftUI, Python)
- Designed for real-world legacy code scenarios

