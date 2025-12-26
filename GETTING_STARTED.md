#  Getting Started

Quick guide to start working with Mobile Observe & Test Framework

---

##  What's Already Built

### 1. **Python Framework (40% complete)**
-  Full CLI with all commands
-  Complete data models (Pydantic)
-  Project structure
- ⏳ Implementations (stubs, need full implementation)

### 2. **Android Demo App (30% complete)**
-  Gradle project with 3 build variants
-  Onboarding screens (swipeable)
-  Login screen
-  Home screen with transactions
- ⏳ Top-up flow with WebView (TODO)
- ⏳ Send money flow (TODO)

### 3. **Observe SDK (10% complete)**
-  Project structure
-  Core classes (SDK, Config, Session)
-  Event system (EventBus, Event models)
-  Observer stubs
- ⏳ Full implementation (TODO)

---

##  Quick Start

### Step 1: Install Python Framework

```bash
cd /Users/vadimtoptunov/PycharmProjects/mobile_test_recorder

# Install in development mode
pip install -e .

# Verify installation
observe --help
```

**Expected output:**
```
 Mobile Observe & Test Framework

Usage: observe [OPTIONS] COMMAND [ARGS]...

Commands:
  init       - Initialize new observe project
  analyze    - Analyze source code (static analysis)
  record     - Record observe sessions
  generate   - Generate test code
  model      - App model operations
  info       - Show framework information
```

### Step 2: Try CLI Commands

```bash
# Create test project
observe init --platform android --output ./test-project

# See info
observe info
```

---

### Step 3: Open Android Project

```bash
# Open Android Studio
# File → Open → /Users/vadimtoptunov/PycharmProjects/mobile_test_recorder/demo-app/android
```

**In Android Studio:**
1. Wait for Gradle sync to complete
2. Select build variant: **observe** (View → Tool Windows → Build Variants)
3. Try to build: Build → Make Project

**Expected issues:**
- Some dependencies might need syncing
- Accompanist pager version might need adjustment
- This is normal for first build!

---

### Step 4: Fix Build Issues (if any)

Common fixes:

```kotlin
// If accompanist pager fails, try this in app/build.gradle.kts:
implementation("com.google.accompanist:accompanist-pager:0.30.1")
implementation("com.google.accompanist:accompanist-pager-indicators:0.30.1")

// Make sure compose BOM is correct:
implementation(platform("androidx.compose:compose-bom:2024.01.00"))
```

---

##  Project Structure

```
mobile_test_recorder/
 framework/              # Python framework
    cli/               # CLI commands (working)
    model/             # Data models (complete)
    analyzer/          # Static analyzers (TODO)
    generators/        # Code generators (TODO)
    storage/           # Event store (TODO)

 demo-app/
    android/
        app/           # Main app
           src/
              main/       # Shared code
              observe/    # Observe build specific
           build.gradle.kts
       
        observe-sdk/   # Observe SDK library
            src/main/

 docs/                  # Documentation
 tests/                 # Generated tests (will be here)
 README.md
 PROGRESS.md           # Detailed progress
 GETTING_STARTED.md    # This file
 pyproject.toml
```

---

##  Next Steps (Development)

### Immediate (This week):
1. **Test what's built**
   - Run CLI commands
   - Build Android app
   - Fix any build issues

2. **Implement Observe SDK observers**
   - UIObserver - capture taps, swipes
   - NavigationObserver - track screens
   - NetworkObserver - intercept API calls

3. **Add Top-up WebView screen**
   - Amount input
   - WebView payment gateway
   - Success/Failure screens

### Week 2-3:
4. **Complete Event Store**
   - SQLite implementation
   - Event recording and replay

5. **Implement Correlation Engine**
   - Link UI actions to API calls
   - Build app model from events

6. **Start Code Generators**
   - Page Object generator
   - Basic test generation

---

## 🧪 Testing Current State

### Test Python CLI:
```bash
# Create project
observe init --platform android

# Check structure
ls -la ./config
ls -la ./models
ls -la ./tests
```

### Test Android App:
```bash
# Build observe variant
cd demo-app/android
./gradlew assembleObserveDebug

# Install on emulator (start emulator first)
adb devices
adb install app/build/outputs/apk/observe/debug/app-observe-debug.apk

# Check logs
adb logcat | grep ObserveSDK
```

---

##  Notes

- **All code is in English** (except our conversation)
- **Build variants are working** (observe/test/prod)
- **Test tags are in place** for all UI elements
- **SDK structure is ready** for implementation
- **Project follows clean architecture**

---

##  Known Issues & Solutions

### Issue 1: Gradle Sync Fails
**Solution:**
- Check Java version: `java -version` (should be 17+)
- Sync project: File → Sync Project with Gradle Files
- Invalidate caches: File → Invalidate Caches / Restart

### Issue 2: Compose Preview Not Working
**Solution:**
- This is normal for first setup
- Try building first: Build → Make Project
- Then refresh preview

### Issue 3: ObserveSDK Not Found
**Solution:**
- Make sure you selected **observe** build variant
- Clean and rebuild: Build → Clean Project → Rebuild

---

##  Tips

1. **Use observe build variant** for development
2. **Check logs** with `adb logcat | grep FinDemo`
3. **Test incrementally** - one screen at a time
4. **Ask questions** if something is unclear!

---

##  Resources

- [Jetpack Compose Docs](https://developer.android.com/jetpack/compose)
- [Click Framework](https://click.palletsprojects.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Appium](https://appium.io/)

---

**Status:** 🟢 Ready for development  
**Last Updated:** 2025-12-19

**Questions?** Check PROGRESS.md for detailed status or README.md for overview.

