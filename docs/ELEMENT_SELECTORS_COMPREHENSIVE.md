# Complete Guide to Mobile Element Selectors

## Overview

This document describes **ALL possible element types and selector strategies** for mobile testing across different tools and frameworks.

---

## Table of Contents

1. [Appium 2 vs Appium 3](#appium-2-vs-appium-3)
2. [Android Selectors](#android-selectors)
3. [iOS Selectors](#ios-selectors)
4. [Cross-Platform Selectors](#cross-platform-selectors)
5. [Native Tools](#native-tools)
6. [Framework-Specific](#framework-specific)
7. [WebView/Hybrid](#webviewhybrid)
8. [Best Practices](#best-practices)

---

## Appium 2 vs Appium 3

### Key Differences

| Feature | Appium 2 | Appium 3 |
|---------|----------|----------|
| **Architecture** | Monolithic | Plugin-based |
| **Driver Installation** | Built-in | Install separately |
| **Selector Strategies** | 8 built-in | Extensible via plugins |
| **WebDriver Protocol** | W3C + JSONWP | W3C only |
| **Element Commands** | Legacy + W3C | W3C standard |
| **Performance** | Good | Better (optimized) |

### Appium 2 Selector Strategies

```python
# Built-in strategies (Appium 2.x)
STRATEGIES = [
    'id',                    # Resource ID (Android), Accessibility ID (iOS)
    'accessibility id',      # Accessibility identifier
    'class name',           # Element class
    'xpath',                # XPath expression
    '-android uiautomator', # UIAutomator selector (Android)
    '-ios predicate string', # NSPredicate (iOS)
    '-ios class chain',     # iOS class chain
    'name',                 # Element name (deprecated)
]
```

### Appium 3 Selector Strategies

```python
# Appium 3.x strategies (more standardized)
STRATEGIES = [
    'id',                    # Resource ID / Accessibility ID
    'accessibility id',      # Accessibility identifier
    'class name',           # Element class
    'xpath',                # XPath 1.0 expression
    'name',                 # Element name (legacy)
    
    # Platform-specific (via plugins)
    '-android uiautomator', # UIAutomator2 selector
    '-ios predicate string', # NSPredicate query
    '-ios class chain',     # iOS class chain query
    
    # New in Appium 3
    '-image',               # Image-based element finding
    '-custom',              # Custom plugin selectors
]
```

### Migration Guide

```python
# Appium 2 → Appium 3
# Most selectors work the same, but:

# 1. Driver initialization changed
# Appium 2
driver = webdriver.Remote('http://localhost:4723/wd/hub', capabilities)

# Appium 3
driver = webdriver.Remote('http://localhost:4723', capabilities)

# 2. Some capabilities renamed
# Appium 2: 'appium:automationName'
# Appium 3: 'appium:automationName' (same, but stricter)

# 3. Selector strategies are more strict
# XPath must be valid XPath 1.0 (not 2.0)
```

---

## Android Selectors

### 1. Resource ID (Best Practice)

**Appium 2 & 3:**

```python
# By ID
element = driver.find_element(AppiumBy.ID, "com.example:id/login_button")

# Shorthand (if unique)
element = driver.find_element(AppiumBy.ID, "login_button")
```

**Page Object:**

```python
class LoginScreen:
    login_button = (AppiumBy.ID, "com.example:id/login_button")
    
    def tap_login(self):
        self.driver.find_element(*self.login_button).click()
```

**Frameworks:**

- **View:** `android:id="@+id/login_button"`
- **Compose:** `Modifier.testTag("login_button")`
- **Flutter:** `key: Key('login_button')`
- **React Native:** `testID="login_button"`

---

### 2. Accessibility ID

**Appium 2 & 3:**

```python
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Login Button")
```

**Frameworks:**

- **View:** `android:contentDescription="Login Button"`
- **Compose:** `Modifier.semantics { contentDescription = "Login Button" }`
- **Flutter:** `Semantics(label: "Login Button")`
- **React Native:** `accessibilityLabel="Login Button"`

---

### 3. Class Name

**Appium 2 & 3:**

```python
# Find by class
buttons = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.Button")
inputs = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
```

**Common Android Classes:**

| Class | Element Type |
|-------|--------------|
| `android.widget.Button` | Button |
| `android.widget.ImageButton` | Image Button |
| `android.widget.EditText` | Text Input |
| `android.widget.TextView` | Text/Label |
| `android.widget.ImageView` | Image |
| `android.widget.CheckBox` | Checkbox |
| `android.widget.Switch` | Switch |
| `android.widget.RadioButton` | Radio Button |
| `android.widget.ListView` | List |
| `android.widget.RecyclerView` | Recycler View |
| `android.webkit.WebView` | WebView |

**Jetpack Compose Classes:**

```python
"androidx.compose.ui.platform.ComposeView"
"androidx.compose.material.Button"
"androidx.compose.material.TextField"
"androidx.compose.material.Text"
```

**Flutter Classes:**

```python
"FlutterView"
"io.flutter.view.FlutterView"
```

**React Native Classes:**

```python
"android.view.ViewGroup"  # RN components render as ViewGroups
"android.widget.EditText"  # TextInput
"android.widget.TextView"  # Text
```

---

### 4. XPath (Fallback)

**Appium 2 & 3:**

```python
# By text
element = driver.find_element(AppiumBy.XPATH, "//android.widget.Button[@text='Login']")

# By resource-id
element = driver.find_element(AppiumBy.XPATH, "//*[@resource-id='com.example:id/login']")

# By content-desc
element = driver.find_element(AppiumBy.XPATH, "//*[@content-desc='Login Button']")

# By class and text
element = driver.find_element(AppiumBy.XPATH, 
    "//android.widget.EditText[@text='Email']")

# Multiple conditions
element = driver.find_element(AppiumBy.XPATH,
    "//*[@resource-id='submit' and @enabled='true']")

# Parent/child relationships
element = driver.find_element(AppiumBy.XPATH,
    "//android.widget.LinearLayout/android.widget.Button[1]")

# Contains
element = driver.find_element(AppiumBy.XPATH,
    "//*[contains(@text, 'Login')]")
```

**XPath Attributes (Android):**

- `@resource-id` - Resource ID
- `@text` - Visible text
- `@content-desc` - Content description
- `@class` - Element class
- `@package` - App package name
- `@checkable` - Is checkable (true/false)
- `@checked` - Is checked (true/false)
- `@clickable` - Is clickable (true/false)
- `@enabled` - Is enabled (true/false)
- `@focusable` - Is focusable (true/false)
- `@focused` - Is focused (true/false)
- `@long-clickable` - Supports long click (true/false)
- `@password` - Is password field (true/false)
- `@scrollable` - Is scrollable (true/false)
- `@selected` - Is selected (true/false)
- `@bounds` - Element bounds [x1,y1][x2,y2]
- `@index` - Child index

---

### 5. UIAutomator Selector (Android Only)

**Appium 2 & 3:**

```python
# By text
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().text("Login")')

# By resourceId
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().resourceId("com.example:id/login")')

# By description
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().description("Login Button")')

# By className
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().className("android.widget.Button")')

# Combined selectors
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().className("android.widget.EditText").instance(0)')

# Text contains
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().textContains("Log")')

# Text starts with
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().textStartsWith("Login")')

# Text matches regex
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().textMatches("Log.*")')

# Scrollable
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().scrollable(true)')

# Checkable
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().checkable(true).checked(false)')

# Child selector
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiSelector().className("android.widget.ListView").childSelector(new UiSelector().text("Item 1"))')

# Scroll to element
element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    'new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView(new UiSelector().text("Item 50"))')
```

**UIAutomator Methods:**

| Method | Description |
|--------|-------------|
| `.text(String)` | Exact text match |
| `.textContains(String)` | Partial text match |
| `.textStartsWith(String)` | Text starts with |
| `.textMatches(String)` | Regex match |
| `.resourceId(String)` | Resource ID |
| `.description(String)` | Content description |
| `.className(String)` | Element class |
| `.packageName(String)` | Package name |
| `.enabled(boolean)` | Enabled state |
| `.clickable(boolean)` | Clickable state |
| `.checkable(boolean)` | Checkable state |
| `.checked(boolean)` | Checked state |
| `.focusable(boolean)` | Focusable state |
| `.scrollable(boolean)` | Scrollable state |
| `.instance(int)` | Instance index |
| `.childSelector(UiSelector)` | Child element |
| `.fromParent(UiSelector)` | Parent element |

---

## iOS Selectors

### 1. Accessibility ID (Best Practice)

**Appium 2 & 3:**

```python
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "loginButton")
```

**Frameworks:**

- **UIKit:** `accessibilityIdentifier = "loginButton"`
- **SwiftUI:** `.accessibilityIdentifier("loginButton")`
- **Flutter:** `key: Key('loginButton')`
- **React Native:** `testID="loginButton"` (maps to accessibilityIdentifier on iOS)

---

### 2. Class Name

**Appium 2 & 3:**

```python
buttons = driver.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypeButton")
inputs = driver.find_elements(AppiumBy.CLASS_NAME, "XCUIElementTypeTextField")
```

**Common iOS Classes (XCUITest):**

| Class | Element Type |
|-------|--------------|
| `XCUIElementTypeButton` | Button |
| `XCUIElementTypeTextField` | Text Input |
| `XCUIElementTypeSecureTextField` | Password Input |
| `XCUIElementTypeStaticText` | Label/Text |
| `XCUIElementTypeImage` | Image |
| `XCUIElementTypeSwitch` | Switch |
| `XCUIElementTypeCheckBox` | Checkbox (iOS 14+) |
| `XCUIElementTypeTable` | Table View |
| `XCUIElementTypeCell` | Table/Collection Cell |
| `XCUIElementTypeScrollView` | Scroll View |
| `XCUIElementTypeWebView` | Web View |
| `XCUIElementTypeNavigationBar` | Navigation Bar |
| `XCUIElementTypeTabBar` | Tab Bar |
| `XCUIElementTypeToolbar` | Toolbar |
| `XCUIElementTypePicker` | Picker |
| `XCUIElementTypePickerWheel` | Picker Wheel |
| `XCUIElementTypeSlider` | Slider |
| `XCUIElementTypeAlert` | Alert |
| `XCUIElementTypeSheet` | Action Sheet |
| `XCUIElementTypeSegmentedControl` | Segmented Control |

---

### 3. XPath (Fallback)

**Appium 2 & 3:**

```python
# By name (label)
element = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeButton[@name='Login']")

# By label
element = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeButton[@label='Login']")

# By value
element = driver.find_element(AppiumBy.XPATH, "//XCUIElementTypeTextField[@value='email@example.com']")

# By type
buttons = driver.find_elements(AppiumBy.XPATH, "//XCUIElementTypeButton")

# Multiple conditions
element = driver.find_element(AppiumBy.XPATH,
    "//XCUIElementTypeButton[@name='Login' and @enabled='true']")

# Parent/child
element = driver.find_element(AppiumBy.XPATH,
    "//XCUIElementTypeNavigationBar/XCUIElementTypeButton[1]")

# Contains
element = driver.find_element(AppiumBy.XPATH,
    "//XCUIElementTypeButton[contains(@name, 'Login')]")
```

**XPath Attributes (iOS):**

- `@name` - Accessibility label or text
- `@label` - Accessibility label
- `@value` - Current value (for inputs, sliders, etc.)
- `@type` - Element type
- `@enabled` - Is enabled (true/false)
- `@visible` - Is visible (true/false)
- `@selected` - Is selected (true/false)
- `@index` - Child index

---

### 4. iOS Predicate String (iOS Only)

**Appium 2 & 3:**

```python
# By label
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label == "Login"')

# By name
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'name == "loginButton"')

# By type
buttons = driver.find_elements(AppiumBy.IOS_PREDICATE,
    'type == "XCUIElementTypeButton"')

# Contains
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label CONTAINS "Login"')

# Begins with
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label BEGINSWITH "Log"')

# Ends with
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label ENDSWITH "in"')

# Case-insensitive
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label ==[c] "login"')

# Multiple conditions (AND)
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'type == "XCUIElementTypeButton" AND label == "Login"')

# Multiple conditions (OR)
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label == "Login" OR label == "Sign In"')

# Enabled
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'enabled == 1')

# Visible
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'visible == 1')

# Regex
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'label MATCHES "Log.*"')

# Value (for inputs)
element = driver.find_element(AppiumBy.IOS_PREDICATE,
    'value == "email@example.com"')
```

**Predicate Operators:**

| Operator | Description |
|----------|-------------|
| `==` | Equal |
| `!=` | Not equal |
| `>`, `<`, `>=`, `<=` | Comparison |
| `CONTAINS` | Contains substring |
| `BEGINSWITH` | Starts with |
| `ENDSWITH` | Ends with |
| `MATCHES` | Regex match |
| `IN` | Value in array |
| `AND`, `OR`, `NOT` | Logical operators |
| `[c]` | Case-insensitive modifier |
| `[d]` | Diacritic-insensitive modifier |

---

### 5. iOS Class Chain (iOS Only)

**Appium 2 & 3:**

```python
# Direct child
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeNavigationBar/XCUIElementTypeButton[1]')

# Descendant
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeButton[`label == "Login"`]')

# Multiple levels
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeTable/XCUIElementTypeCell[1]/XCUIElementTypeButton')

# By predicate
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeButton[`name CONTAINS "Login"`]')

# Index and predicate
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/XCUIElementTypeTable/XCUIElementTypeCell[`name == "Settings"`]')

# Wildcard
element = driver.find_element(AppiumBy.IOS_CLASS_CHAIN,
    '**/*[`name == "loginButton"`]')
```

---

## Cross-Platform Selectors

### Abstraction Layer

```python
class LoginScreen:
    """Cross-platform login screen"""
    
    def __init__(self, driver):
        self.driver = driver
        self.platform = driver.capabilities['platformName'].lower()
    
    @property
    def login_button(self):
        if self.platform == 'android':
            return (AppiumBy.ID, "com.example:id/login_button")
        else:  # iOS
            return (AppiumBy.ACCESSIBILITY_ID, "loginButton")
    
    @property
    def email_input(self):
        if self.platform == 'android':
            return (AppiumBy.XPATH, "//android.widget.EditText[@content-desc='Email']")
        else:  # iOS
            return (AppiumBy.XPATH, "//XCUIElementTypeTextField[@name='Email']")
    
    def tap_login(self):
        self.driver.find_element(*self.login_button).click()
```

### Framework's Approach

```python
# Our generated Page Object uses unified selector format
class LoginScreen:
    login_button = Selector(
        android="id:com.example:id/login_button",
        ios="accessibility_id:loginButton",
        fallback_android="xpath://android.widget.Button[@text='Login']",
        fallback_ios="xpath://XCUIElementTypeButton[@name='Login']"
    )
    
    def tap_login(self):
        element = self.find_element(self.login_button)
        element.click()
```

---

## Native Tools

### 1. UIAutomator2 (Android Native)

**Direct UIAutomator API (no Appium):**

```java
// Java
UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());

// By resource ID
UiObject button = device.findObject(new UiSelector().resourceId("com.example:id/login"));

// By text
UiObject element = device.findObject(new UiSelector().text("Login"));

// By class
UiObject input = device.findObject(new UiSelector().className("android.widget.EditText"));

// Scroll
UiScrollable scrollable = new UiScrollable(new UiSelector().scrollable(true));
scrollable.scrollIntoView(new UiSelector().text("Item 50"));
```

---

### 2. XCUITest (iOS Native)

**Direct XCUITest API (no Appium):**

```swift
// Swift
let app = XCUIApplication()

// By accessibility identifier
let button = app.buttons["loginButton"]

// By label
let label = app.staticTexts["Welcome"]

// By type
let firstButton = app.buttons.element(boundBy: 0)

// Predicate
let button = app.buttons.matching(NSPredicate(format: "label CONTAINS 'Login'")).element

// Tap
button.tap()

// Type
let textField = app.textFields["emailInput"]
textField.tap()
textField.typeText("user@example.com")

// Swipe
app.swipeUp()

// Scroll
let table = app.tables.element
table.swipeUp()
```

---

## Framework-Specific

### Jetpack Compose

**Test Tags (Best Practice):**

```kotlin
// Compose
Button(
    onClick = { /* ... */ },
    modifier = Modifier.testTag("login_button")
) {
    Text("Login")
}
```

**Appium Selector:**

```python
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")
# Or
element = driver.find_element(AppiumBy.ID, "login_button")
```

**Semantics:**

```kotlin
Button(
    onClick = { /* ... */ },
    modifier = Modifier.semantics {
        contentDescription = "Login Button"
        testTag = "login_button"
    }
) {
    Text("Login")
}
```

---

### Flutter

**Keys:**

```dart
// Flutter
ElevatedButton(
  key: Key('login_button'),
  onPressed: () {},
  child: Text('Login'),
)
```

**Appium Selector (with Flutter Driver):**

```python
# Via accessibility
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")
```

**Flutter Driver (Alternative to Appium):**

```dart
// Dart integration test
await driver.tap(find.byValueKey('login_button'));
```

---

### React Native

**TestID:**

```javascript
// React Native
<Button
  testID="login_button"
  title="Login"
  onPress={handleLogin}
/>
```

**Appium Selector:**

```python
# Android
element = driver.find_element(AppiumBy.ID, "login_button")

# iOS
element = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "login_button")
```

---

## WebView/Hybrid

### Switching Context

**Appium 2 & 3:**

```python
# Get all contexts
contexts = driver.contexts
print(contexts)  # ['NATIVE_APP', 'WEBVIEW_com.example']

# Switch to WebView
driver.switch_to.context('WEBVIEW_com.example')

# Now use web selectors
element = driver.find_element(By.ID, "username")
element = driver.find_element(By.CSS_SELECTOR, "button.submit")
element = driver.find_element(By.XPATH, "//button[@type='submit']")

# Switch back to native
driver.switch_to.context('NATIVE_APP')
```

### WebView Selectors

**Standard Web Selectors (Selenium):**

```python
from selenium.webdriver.common.by import By

# ID
element = driver.find_element(By.ID, "username")

# Class name
element = driver.find_element(By.CLASS_NAME, "btn-primary")

# CSS Selector
element = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
element = driver.find_element(By.CSS_SELECTOR, "button.submit")
element = driver.find_element(By.CSS_SELECTOR, "#login-form > button")

# XPath
element = driver.find_element(By.XPATH, "//input[@id='username']")
element = driver.find_element(By.XPATH, "//button[@type='submit']")

# Link text
element = driver.find_element(By.LINK_TEXT, "Forgot Password?")
element = driver.find_element(By.PARTIAL_LINK_TEXT, "Forgot")

# Tag name
buttons = driver.find_elements(By.TAG_NAME, "button")

# Name
element = driver.find_element(By.NAME, "username")
```

---

## Best Practices

### Selector Priority (Android)

1. **Resource ID** (if available, most stable)

   ```python
   (AppiumBy.ID, "com.example:id/login_button")
   ```

2. **Test Tag / Accessibility ID** (Compose/modern apps)

   ```python
   (AppiumBy.ACCESSIBILITY_ID, "login_button")
   ```

3. **UIAutomator** (powerful, Android-specific)

   ```python
   (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Login")')
   ```

4. **XPath** (last resort, fragile)

   ```python
   (AppiumBy.XPATH, "//android.widget.Button[@text='Login']")
   ```

### Selector Priority (iOS)

1. **Accessibility Identifier** (best practice)

   ```python
   (AppiumBy.ACCESSIBILITY_ID, "loginButton")
   ```

2. **iOS Predicate** (powerful, iOS-specific)

   ```python
   (AppiumBy.IOS_PREDICATE, 'label == "Login"')
   ```

3. **iOS Class Chain** (efficient)

   ```python
   (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeButton[`label == "Login"`]')
   ```

4. **XPath** (last resort, fragile)

   ```python
   (AppiumBy.XPATH, "//XCUIElementTypeButton[@name='Login']")
   ```

### Stability Scoring

Our framework scores selectors based on stability:

| Strategy | Stability Score | Notes |
|----------|----------------|-------|
| Resource ID | 100 | Most stable |
| Accessibility ID | 95 | Very stable |
| Test Tag | 95 | Very stable (Compose/Flutter) |
| Class + unique attribute | 70 | Moderate |
| UIAutomator (complex) | 60 | Context-dependent |
| XPath (short, with ID) | 50 | Fragile |
| XPath (complex, text-based) | 20 | Very fragile |
| Text-only | 10 | Extremely fragile |

---

## Element Attributes Reference

### Android (UIAutomator2)

```python
element.get_attribute('resource-id')       # Resource ID
element.get_attribute('text')             # Visible text
element.get_attribute('content-desc')     # Content description
element.get_attribute('class')            # Element class
element.get_attribute('package')          # Package name
element.get_attribute('checkable')        # Is checkable
element.get_attribute('checked')          # Is checked
element.get_attribute('clickable')        # Is clickable
element.get_attribute('enabled')          # Is enabled
element.get_attribute('focusable')        # Is focusable
element.get_attribute('focused')          # Is focused
element.get_attribute('long-clickable')   # Supports long click
element.get_attribute('password')         # Is password field
element.get_attribute('scrollable')       # Is scrollable
element.get_attribute('selected')         # Is selected
element.get_attribute('bounds')           # Element bounds
element.get_attribute('displayed')        # Is displayed
```

### iOS (XCUITest)

```python
element.get_attribute('name')             # Accessibility label/text
element.get_attribute('label')            # Accessibility label
element.get_attribute('value')            # Current value
element.get_attribute('type')             # Element type
element.get_attribute('enabled')          # Is enabled
element.get_attribute('visible')          # Is visible
element.get_attribute('selected')         # Is selected
element.get_attribute('rect')             # Element rectangle
```

---

## Summary Table

### Quick Reference

| Selector Type | Android | iOS | Stability | Appium 2 | Appium 3 |
|---------------|---------|-----|-----------|----------|----------|
| ID |  |  |  |  |  |
| Accessibility ID |  |  |  |  |  |
| Class Name |  |  |  |  |  |
| XPath |  |  |  |  |  |
| UIAutomator |  |  |  |  |  |
| iOS Predicate |  |  |  |  |  |
| iOS Class Chain |  |  |  |  |  |
| Image |  |  |  |  |  |

Legend:

- Fully supported
- Limited support
- Not supported
- Stability rating (1-5 stars)

---

## Generated Page Object Example

Our framework generates Page Objects that handle all these complexities:

```python
from appium.webdriver.common.appiumby import AppiumBy
from framework.page_object_base import BasePage

class LoginScreen(BasePage):
    """Auto-generated Page Object for Login Screen"""
    
    # Selectors with fallbacks
    email_input = {
        'primary': (AppiumBy.ID, 'com.example:id/email_input'),
        'fallback': (AppiumBy.XPATH, '//android.widget.EditText[@content-desc="Email"]'),
        'ios_primary': (AppiumBy.ACCESSIBILITY_ID, 'emailInput'),
        'ios_fallback': (AppiumBy.XPATH, '//XCUIElementTypeTextField[@name="Email"]'),
        'stability': 'HIGH'
    }
    
    password_input = {
        'primary': (AppiumBy.ID, 'com.example:id/password_input'),
        'fallback': (AppiumBy.XPATH, '//android.widget.EditText[@password="true"]'),
        'ios_primary': (AppiumBy.ACCESSIBILITY_ID, 'passwordInput'),
        'ios_fallback': (AppiumBy.XPATH, '//XCUIElementTypeSecureTextField'),
        'stability': 'HIGH'
    }
    
    login_button = {
        'primary': (AppiumBy.ID, 'com.example:id/login_button'),
        'fallback': (AppiumBy.XPATH, '//android.widget.Button[@text="Login"]'),
        'ios_primary': (AppiumBy.ACCESSIBILITY_ID, 'loginButton'),
        'ios_fallback': (AppiumBy.IOS_PREDICATE, 'label == "Login"'),
        'stability': 'MEDIUM'
    }
    
    def enter_email(self, email: str):
        """Enter email address"""
        self.find_element(self.email_input).send_keys(email)
    
    def enter_password(self, password: str):
        """Enter password"""
        self.find_element(self.password_input).send_keys(password)
    
    def tap_login(self):
        """Tap login button"""
        self.find_element(self.login_button).click()
    
    def login(self, email: str, password: str):
        """Complete login flow"""
        self.enter_email(email)
        self.enter_password(password)
        self.tap_login()
```

---

**This document covers ALL selector strategies across all tools and frameworks!**

For framework-specific implementation, see the generated Page Objects in `generated/pages/`.
