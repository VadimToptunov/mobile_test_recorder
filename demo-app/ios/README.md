# 📱 iOS Demo App (Future Implementation)

iOS version of FinDemo application with Regula KYC integration.

---

## 📋 Planned Features

### Core Functionality:
- ✅ Onboarding (swipeable pages)
- ✅ Authentication (Login/Register)
- ✅ KYC with Regula Document Reader SDK
- ✅ Home screen with balance
- ✅ Top-up with WebView
- ✅ Send money flow
- ✅ Transaction history

### Tech Stack:
- **SwiftUI** - Modern declarative UI
- **Combine** - Reactive programming
- **NavigationStack** - iOS 16+ navigation
- **URLSession/Alamofire** - Networking
- **CoreData** - Local storage
- **AVFoundation** - Camera/QR scanner
- **LocalAuthentication** - Biometrics

### Regula SDK Integration:
```swift
// Podfile
pod 'DocumentReader', '~> 7.6'

// Or SPM
dependencies: [
    .package(
        url: "https://github.com/regulaforensics/DocumentReader-iOS",
        from: "7.6.0"
    )
]
```

---

## 🚀 Implementation Plan

### Phase 1: Project Setup
- [ ] Create Xcode project
- [ ] Setup SwiftUI navigation
- [ ] Add Regula SDK dependency
- [ ] Configure build variants (Observe/Test/Prod)

### Phase 2: Core Screens
- [ ] Onboarding view
- [ ] Login/Register views
- [ ] KYC view with Regula
- [ ] Home view

### Phase 3: Observe SDK
- [ ] iOS Observe SDK module
- [ ] UI event tracking
- [ ] Navigation observer
- [ ] Network interceptor

---

## 📝 KYC Screen (Planned)

```swift
struct KYCView: View {
    @StateObject var viewModel = KYCViewModel()
    
    var body: some View {
        VStack {
            Text("Identity Verification")
                .font(.largeTitle)
            
            Button("Scan Document") {
                viewModel.startScanning()
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("scan_document_button")
        }
    }
}

class KYCViewModel: ObservableObject {
    @Published var scanResult: DocumentResult?
    
    func startScanning() {
        // Initialize Regula Document Reader
        let reader = DocReader.shared
        
        reader.showScanner(self) { action, result, error in
            if action == .complete {
                self.scanResult = result
            }
        }
    }
}
```

---

## 🔧 Build Configuration

### Info.plist Requirements:
```xml
<!-- Camera permission -->
<key>NSCameraUsageDescription</key>
<string>Camera access is required for document scanning</string>

<!-- Location (if needed for KYC) -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>Location is needed for verification</string>
```

### Build Schemes:
- **Observe** - With Observe SDK
- **Test** - Clean for automation
- **Production** - Release build

---

## 📊 Current Status

**Status:** 🔴 Not Started  
**Priority:** High  
**Estimated Time:** 6-8 weeks

Will be implemented in **Phase 3** of the project roadmap.

---

## 💡 Notes

- Parity with Android app required
- Regula SDK works the same way on iOS
- SwiftUI navigation similar to Compose
- Test IDs via accessibilityIdentifier
- Observe SDK architecture mirrors Android

---

**For now, focus is on Android implementation.**  
iOS will follow same patterns and architecture.

