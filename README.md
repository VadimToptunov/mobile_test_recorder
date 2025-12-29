# Mobile Observe & Test Framework

> **Intelligent Mobile Testing Platform** - Transform user interactions into production-ready automated tests

[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Android](https://img.shields.io/badge/android-native%20%7C%20compose-green.svg)](demo-app/android)
[![iOS](https://img.shields.io/badge/ios-uikit%20%7C%20swiftui-blue.svg)](demo-app/ios)
[![Cross-Platform](https://img.shields.io/badge/cross--platform-flutter%20%7C%20react%20native-purple.svg)](#features)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/VadimToptunov/mobile_test_recorder?style=social)](https://github.com/VadimToptunov/mobile_test_recorder)
[![Lines of Code](https://img.shields.io/badge/lines%20of%20code-63k-informational)](https://github.com/VadimToptunov/mobile_test_recorder)

---

## What It Does

**Stop writing tests manually.** Let your QA team walk through the app once, and get production-ready automated tests automatically.

```
QA explores app  →  AI observes & learns  →  Tests generated  →  Self-healing when UI changes
```

### The Problem

- Writing mobile tests is **slow and tedious**
- Tests break when **UI changes**
- API endpoints are **hard to discover**
- Selectors are **fragile**
- Cross-platform testing requires **double the work**

### The Solution

- **Observe** real user behavior in special build
- **Extract** screens, elements, APIs, flows automatically
- **Generate** Page Objects, API clients, BDD scenarios
- **Self-heal** when selectors break
- **Cross-platform** tests from single model

---

## Key Features

### 🎯 Smart Test Generation
- **API-first approach** - 80% API tests, 20% UI tests
- **Robust selectors** - ID → XPath → CSS → Text fallbacks
- **BDD scenarios** - Human-readable Gherkin features
- **Page Objects** - Maintainable test structure
- **Cross-platform** - One model, tests for Android & iOS

### 🔧 Self-Healing Tests
- **Automatic repair** - Broken selectors fixed by ML
- **Confidence scoring** - Only high-quality fixes applied
- **Interactive dashboard** - Review and approve changes
- **Git integration** - All fixes tracked in version control

### 🚀 Enterprise Ready
- **CI/CD integration** - GitHub Actions, GitLab CI
- **Device management** - Emulators, real devices, BrowserStack
- **Smart test selection** - Run only affected tests
- **Parallel execution** - Intelligent sharding
- **Rich reporting** - HTML, Allure, JUnit

### 🔒 Security & Performance
- **Traffic decryption** - Capture encrypted API calls
- **Security analysis** - OWASP Mobile Top 10 checks
- **Performance profiling** - CPU, memory, FPS monitoring
- **Visual regression** - Screenshot comparison

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mobile_test_recorder.git
cd mobile_test_recorder

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CLI
pip install -e .
```

### Basic Workflow

```bash
# 1. Record user session (run observe build on device)
# QA walks through app features

# 2. Import events
observe import --session-file /path/to/events.json --platform android

# 3. Build app model
observe model build --session my-session --output ./app-model.json

# 4. Generate tests
observe generate all --model ./app-model.json --output ./tests/

# 5. Run tests
pytest tests/
```

### Self-Healing Tests

```bash
# When tests fail due to UI changes:
observe heal auto --test-results junit.xml --commit

# Review changes in dashboard:
observe dashboard
# → http://localhost:8080
```

---

## Documentation

- **[User Guide](USER_GUIDE.md)** - Complete step-by-step guide
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Demo Apps](demo-app/README.md)** - Example Android & iOS applications

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   OBSERVE   │  →   │   ANALYZE    │  →   │  CORRELATE  │  →   │   GENERATE   │
│             │      │              │      │             │      │              │
│ Record user │      │ Build model  │      │ Link UI +   │      │ Page Objects │
│ interactions│      │ from events  │      │ API + flows │      │ + API clients│
│ in observe  │      │ and static   │      │ using ML    │      │ + BDD tests  │
│ build       │      │ code         │      │             │      │              │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

---

## Demo Applications

Two production-grade fintech apps included:

- **Android** (Kotlin + Jetpack Compose) - [demo-app/android](demo-app/android)
- **iOS** (Swift + SwiftUI) - [demo-app/ios](demo-app/ios)

Features: Onboarding, Auth, Dashboard, Transfers, KYC, WebView payments

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **CLI** | Python 3.13, Click |
| **Test Framework** | pytest, pytest-bdd, Appium 3 |
| **ML** | scikit-learn, NumPy, Pandas |
| **Static Analysis** | tree-sitter (Kotlin, Swift) |
| **Mobile SDKs** | Kotlin, Swift |
| **Dashboard** | FastAPI, Alpine.js |
| **CI/CD** | GitHub Actions, GitLab CI |

---

## Project Stats

| Metric | Value |
|--------|-------|
| **Total Code** | ~63,000 lines |
| **Languages** | Python, Kotlin, Swift, HTML/JS |
| **Phases Complete** | 6 of 6 |
| **CLI Commands** | 30+ |
| **Platforms** | Android, iOS, Web Dashboard |
| **Status** | ✅ Production Ready |

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Author

**Vadim Toptunov**

*Built for QA Engineers who deserve better tools.*

---

## Contributing

Contributions are welcome! Please read the [User Guide](USER_GUIDE.md) first.

---

**Ready to transform your mobile testing?** Check out the [User Guide](USER_GUIDE.md) to get started. 🚀
