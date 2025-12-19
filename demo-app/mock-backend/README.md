# 🔧 Mock Backend API

Simple FastAPI server for FinDemo app testing.

## 🚀 Quick Start

```bash
# From project root, activate venv
cd /{your_location}/mobile_test_recorder
source .venv/bin/activate

# Run server
cd demo-app/mock-backend
python main.py
```

Server will start on `http://localhost:8000`

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Endpoints

### Auth
- `POST /api/auth/login` - Login (accepts any credentials)
- `POST /api/auth/register` - Register user

### User
- `GET /api/user/profile` - Get user profile
- `GET /api/user/balance` - Get balance

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/topup` - Top-up account
- `POST /api/send` - Send money

### KYC
- `POST /api/kyc/verify` - Verify KYC document
- `GET /api/kyc/status` - Get KYC status

## 📝 Example Requests

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Get Balance
```bash
curl http://localhost:8000/api/user/balance?user_id=user123
```

### Top-up
```bash
curl -X POST http://localhost:8000/api/topup \
  -H "Content-Type: application/json" \
  -d '{"amount":100.00,"card_last4":"1234"}'
```

## 🎯 Features

- ✅ CORS enabled for mobile apps
- ✅ Mock data for testing
- ✅ All endpoints return success responses
- ✅ No authentication required
- ✅ Automatic API documentation

## 🔄 Connect from Android

Update your Android app to point to:
- Emulator: `http://10.0.2.2:8000`
- Real device: `http://YOUR_IP:8000`

## ⚙️ Configuration

Edit `main.py` to:
- Change port (default: 8000)
- Modify mock data
- Add custom endpoints

---

**Status:** ✅ Ready for development

