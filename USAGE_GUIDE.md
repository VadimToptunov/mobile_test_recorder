# Mobile Observe & Test Framework - Usage Guide

## Quick Start

### Prerequisites

- Python 3.13+
- Android SDK (for Android testing)
- Xcode (for iOS testing, future)
- Appium installed and running

### Installation

```bash
# Clone repository
cd mobile_test_recorder

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install framework in editable mode
pip install -e .
```

### Verify Installation

```bash
observe info
```

---

## Complete Workflow

### Step 1: Initialize Project

```bash
observe init --platform android --output ./my-project
cd my-project
```

This creates:
```
my-project/
├── models/         # App models
├── tests/          # Generated tests
├── sessions/       # Recorded sessions
└── config/         # Configuration files
```

### Step 2: Static Analysis (Optional)

Analyze your app's source code to discover screens, elements, and API endpoints:

```bash
observe analyze android --source ./path/to/android/app
```

**Output:** `models/static_analysis.yaml` with:
- Screens discovered from Composable functions
- UI elements with test tags
- Navigation routes
- Retrofit API definitions

### Step 3: Build and Install Observe Build

Build your app with the Observe SDK integrated:

```bash
cd demo-app/android
./gradlew installObserveDebug
```

The SDK will capture:
- UI interactions (taps, swipes, inputs)
- Navigation events
- Network calls (with OkHttp interceptor)
- UI hierarchy snapshots

### Step 4: Record Session

Start recording:

```bash
observe record start --device emulator-5554 --session-name login_flow
```

**Interact with your app:**
- Navigate through screens
- Fill forms
- Submit data
- Observe different flows

**Stop recording:**
Press `Ctrl+C` or run:
```bash
observe record stop
```

Events are saved to SQLite database and JSON files.

### Step 5: Correlate Events

Discover relationships between UI actions, API calls, and navigation:

```bash
observe record correlate --session-id session_20250119_142345 \
    --output correlations.json
```

**What it does:**
- Correlates UI events with API calls (temporal proximity, thread matching)
- Correlates API responses with navigation
- Builds complete flows (UI → API → Navigation)
- Assigns confidence scores

**Output:** `correlations.json` with:
```json
{
  "ui_to_api": [...],
  "api_to_navigation": [...],
  "full_flows": [...],
  "correlation_rate": 0.85
}
```

### Step 6: Build App Model

Generate structured AppModel from events:

```bash
observe model build --session-id session_20250119_142345 \
    --app-version 1.0.0 \
    --platform android \
    --output models/app_model.yaml
```

**What it does:**
- Infers screens from navigation events
- Extracts elements from UI interactions
- Builds API schema from network events
- Generates flows from correlations
- Creates state machine (states + transitions)

**Output:** `app_model.yaml` with:
```yaml
meta:
  app_version: "1.0.0"
  platform: android
  
screens:
  LoginScreen:
    elements:
      - id: email_input
        type: TextField
        selectors: [...]
    actions:
      - name: tap_login_button
        type: tap
        
api_calls:
  POST_/auth/login:
    method: POST
    endpoint: /auth/login
    
flows:
  - name: login_flow
    steps: [...]
```

### Step 7: Generate Tests

Generate test code from the model:

#### Page Objects

```bash
observe generate pages --model models/app_model.yaml \
    --output tests/pages
```

Generates:
```python
# tests/pages/login_screen.py
class LoginScreenPage:
    def __init__(self, driver):
        self.driver = driver
        self.email_input = (By.ID, "email_input")
        self.password_input = (By.ID, "password_input")
        self.login_button = (By.ID, "login_button")
    
    def enter_email(self, email: str):
        self.driver.find_element(*self.email_input).send_keys(email)
    
    def tap_login(self):
        self.driver.find_element(*self.login_button).click()
```

#### API Clients

```bash
observe generate api --model models/app_model.yaml \
    --output tests/api
```

Generates:
```python
# tests/api/api_client.py
class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def auth_login(self, email: str, password: str):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password}
        )
        return response
```

#### BDD Features

```bash
observe generate features --model models/app_model.yaml \
    --output tests/features
```

Generates:
```gherkin
# tests/features/login_flow.feature
Feature: Login Flow
  
  Scenario: Successful login
    Given I am on LoginScreen
    When I enter email "user@test.com"
    And I enter password "password123"
    And I tap login button
    Then I should be on HomeScreen
```

### Step 8: Run Tests

#### UI Tests (Appium)

```bash
# Start Appium server
appium

# Run tests
pytest tests/features/ --appium-url http://localhost:4723
```

#### API Tests

```bash
pytest tests/api/
```

---

## Advanced Features

### Model Comparison

Compare two app models to detect changes:

```bash
observe model diff model_v1.yaml model_v2.yaml \
    --output model_diff.md
```

Shows:
- New screens
- Removed screens
- Changed elements
- New API endpoints

### Model Validation

Validate model structure:

```bash
observe model validate models/app_model.yaml
```

### Custom Correlation Strategies

Tune correlation parameters in code:

```python
from framework.correlation import EventCorrelator
from framework.correlation.strategies import TemporalProximityStrategy

correlator = EventCorrelator()
correlator.ui_strategy = TemporalProximityStrategy(
    max_time_delta_ms=3000  # Allow 3 seconds between UI and API
)
```

---

## Configuration

Edit `config/observe.yaml`:

```yaml
platform: android

observe_build:
  app_path: "app/build/outputs/apk/observe/debug/app-observe-debug.apk"
  
appium:
  server_url: "http://localhost:4723"
  capabilities:
    platformName: Android
    automationName: UiAutomator2
    deviceName: emulator-5554
    
model:
  output: "models/app_model.yaml"
  
generation:
  page_objects_output: "tests/pages"
  api_client_output: "tests/api"
  features_output: "tests/features"
```

---

## Best Practices

### 1. Use Meaningful Session Names

```bash
observe record start --session-name user_registration_happy_path
observe record start --session-name payment_error_scenarios
```

### 2. Record Multiple Scenarios

Record different user journeys:
- Happy path
- Error scenarios
- Edge cases

### 3. Add Test Tags to UI Elements

In your Compose UI:
```kotlin
Button(
    onClick = { },
    modifier = Modifier.testTag("login_button")  // ✅ Good
) {
    Text("Login")
}
```

### 4. Use Correlation IDs

In your network layer:
```kotlin
val request = originalRequest.newBuilder()
    .header("X-Correlation-ID", UUID.randomUUID().toString())
    .build()
```

This enables **strong correlation** between UI and API events.

### 5. Review Generated Code

Always review and refine generated tests:
- Add assertions
- Handle edge cases
- Add waits for async operations

### 6. Combine Static + Dynamic Analysis

```bash
# Step 1: Static analysis
observe analyze android --source ./app

# Step 2: Dynamic recording
observe record start

# Step 3: Merge results
observe model build --session-id <id> \
    --static-analysis models/static_analysis.yaml
```

---

## Troubleshooting

### SDK Not Capturing Events

1. Check SDK initialization:
```kotlin
if (BuildConfig.DEBUG) {
    ObserveSDK.initialize(this, ObserveConfig(enabled = true))
}
```

2. Verify build variant: `observeDebug`

3. Check logs:
```bash
adb logcat | grep ObserveSDK
```

### Low Correlation Rate

If correlation rate < 50%:

1. Add correlation IDs to API calls
2. Reduce `max_time_delta_ms` if too many false positives
3. Add more test tags to UI elements

### Generated Tests Failing

1. Check selectors:
   - Add stable IDs (resourceId, testTag)
   - Avoid text-based selectors for dynamic content

2. Add waits:
```python
from selenium.webdriver.support.ui import WebDriverWait

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element_id"))
)
```

---

## Examples

See `examples/` directory for:
- Complete demo app (Android)
- Sample test suites
- Custom correlation strategies
- CI/CD integration scripts

---

## Support

- Documentation: [README.md](README.md)
- Architecture: [mobile_observe_test_framework_RFC.md](mobile_observe_test_framework_RFC.md)
- Issues: GitHub Issues

---

## Next Steps

After mastering the basics:

1. **iOS Support** (coming in Phase 3)
2. **Visual Regression Testing**
3. **ML-based Element Classification**
4. **CI/CD Integration Templates**
5. **TestRail/Allure Integration**

