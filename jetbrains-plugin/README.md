# Mobile Test Recorder - JetBrains Plugin

JetBrains IDE plugin for mobile test automation with interactive UI control and smart test generation.

## Features

- 📱 Device management (Android emulators, iOS simulators)
- 🔍 UI Tree inspector (Appium XML viewer)
- 📊 Device logs (logcat, simctl)
- 📸 Screenshot capture
- 🎯 Interactive UI control (tap, swipe, type)
- 🧠 Smart selector generation
- 🔄 Flow-based test generation
- 🌍 Multi-language support (Python, Java, Kotlin, JS/TS, Go, Ruby)
- 🔌 Multi-backend (Appium, Espresso, XCTest, Detox, Maestro)

## Requirements

- JetBrains IDE (IntelliJ IDEA, Android Studio, PyCharm, etc.) 2023.2+
- Java 17+
- Python 3.8+
- `mobile-test-recorder` CLI installed (`pip install mobile-observe-test`)

## Installation

### From Marketplace (Coming Soon)

1. Open Settings → Plugins
2. Search for "Mobile Test Recorder"
3. Click Install

### From Source

```bash
cd jetbrains-plugin
./gradlew buildPlugin
# Install from disk: build/distributions/mobile-test-recorder-*.zip
```

## Development

### Setup

```bash
./gradlew buildPlugin
```

### Run IDE with Plugin

```bash
./gradlew runIde
```

### Test

```bash
./gradlew test
```

## Architecture

```
JetBrains Plugin (Kotlin)
├── ToolWindow
│   ├── Devices Tab
│   ├── Inspector Tab
│   ├── Logs Tab
│   └── Actions Tab
├── JSON-RPC Client
└── Settings

     ↕ (JSON-RPC)

mobile-test-recorder CLI (Python + Rust)
├── Daemon
├── Device Management
├── UI Inspection
└── Code Generation
```

## Usage

1. Open any project in JetBrains IDE
2. Open "Mobile Test Recorder" tool window (View → Tool Windows)
3. Click "Start Daemon" to connect to CLI
4. Select device from list
5. Start testing!

## License

MIT License - see [LICENSE](../LICENSE)
