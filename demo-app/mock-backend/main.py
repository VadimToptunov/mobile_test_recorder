"""
Mock Backend API for FinDemo App

Simple FastAPI server to simulate backend responses for demo purposes.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="FinDemo Mock API",
    description="Mock backend for Mobile Observe & Test Framework demo",
    version="0.1.0"
)

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Models ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user_id: Optional[str] = None
    message: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    balance: float
    currency: str = "USD"

class Transaction(BaseModel):
    id: str
    type: str  # topup, send, receive
    amount: float
    currency: str
    recipient: Optional[str] = None
    sender: Optional[str] = None
    note: Optional[str] = None
    timestamp: str
    status: str

class TopUpRequest(BaseModel):
    amount: float
    card_last4: str

class SendMoneyRequest(BaseModel):
    recipient_name: str
    recipient_id: str
    amount: float
    note: Optional[str] = None

class KYCVerificationRequest(BaseModel):
    document_type: str
    document_number: str
    full_name: str

# ==================== Mock Data ====================

mock_users = {
    "user123": {
        "user_id": "user123",
        "name": "John Doe",
        "email": "john@example.com",
        "balance": 1250.50,
        "currency": "USD"
    }
}

mock_transactions = [
    {
        "id": "tx001",
        "type": "receive",
        "amount": 100.00,
        "currency": "USD",
        "sender": "Alice Johnson",
        "timestamp": "2024-12-15T10:30:00Z",
        "status": "completed"
    },
    {
        "id": "tx002",
        "type": "send",
        "amount": 50.00,
        "currency": "USD",
        "recipient": "Bob Smith",
        "note": "Dinner split",
        "timestamp": "2024-12-14T18:45:00Z",
        "status": "completed"
    },
    {
        "id": "tx003",
        "type": "topup",
        "amount": 200.00,
        "currency": "USD",
        "timestamp": "2024-12-13T09:15:00Z",
        "status": "completed"
    }
]

# ==================== Routes ====================

@app.get("/")
def root():
    """API health check"""
    return {
        "service": "FinDemo Mock API",
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# ==================== Auth ====================

@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Mock login endpoint
    Accepts any email/password for demo purposes
    """
    if not request.email or not request.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Mock: accept any credentials
    return LoginResponse(
        success=True,
        token="mock_token_abc123",
        user_id="user123",
        message="Login successful"
    )

@app.post("/api/auth/register")
def register(request: LoginRequest):
    """Mock registration endpoint"""
    return {
        "success": True,
        "message": "Registration successful",
        "user_id": "user123"
    }

# ==================== User ====================

@app.get("/api/user/profile", response_model=UserProfile)
def get_profile(user_id: str = "user123"):
    """Get user profile"""
    if user_id not in mock_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    return mock_users[user_id]

@app.get("/api/user/balance")
def get_balance(user_id: str = "user123"):
    """Get user balance"""
    if user_id not in mock_users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = mock_users[user_id]
    return {
        "balance": user["balance"],
        "currency": user["currency"]
    }

# ==================== Transactions ====================

@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions(user_id: str = "user123", limit: int = 10):
    """Get user transactions"""
    # Return mock transactions
    return mock_transactions[:limit]

@app.post("/api/topup")
def topup(request: TopUpRequest, user_id: str = "user123"):
    """Process top-up"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    # Update mock balance
    if user_id in mock_users:
        mock_users[user_id]["balance"] += request.amount
    
    # Create transaction
    transaction = {
        "id": f"tx{len(mock_transactions) + 1:03d}",
        "type": "topup",
        "amount": request.amount,
        "currency": "USD",
        "timestamp": datetime.now().isoformat() + "Z",
        "status": "completed"
    }
    mock_transactions.insert(0, transaction)
    
    return {
        "success": True,
        "transaction_id": transaction["id"],
        "new_balance": mock_users[user_id]["balance"],
        "message": "Top-up successful"
    }

@app.post("/api/send")
def send_money(request: SendMoneyRequest, user_id: str = "user123"):
    """Send money to another user"""
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    # Check balance
    if user_id in mock_users:
        if mock_users[user_id]["balance"] < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Update balance
        mock_users[user_id]["balance"] -= request.amount
    
    # Create transaction
    transaction = {
        "id": f"tx{len(mock_transactions) + 1:03d}",
        "type": "send",
        "amount": request.amount,
        "currency": "USD",
        "recipient": request.recipient_name,
        "note": request.note,
        "timestamp": datetime.now().isoformat() + "Z",
        "status": "completed"
    }
    mock_transactions.insert(0, transaction)
    
    return {
        "success": True,
        "transaction_id": transaction["id"],
        "new_balance": mock_users[user_id]["balance"],
        "message": f"Sent ${request.amount} to {request.recipient_name}"
    }

# ==================== KYC ====================

@app.post("/api/kyc/verify")
def verify_kyc(request: KYCVerificationRequest, user_id: str = "user123"):
    """
    Verify KYC document
    Mock endpoint - always returns success
    """
    return {
        "success": True,
        "verification_id": "kyc_verify_001",
        "status": "verified",
        "message": "KYC verification successful"
    }

@app.get("/api/kyc/status")
def get_kyc_status(user_id: str = "user123"):
    """Get KYC verification status"""
    return {
        "user_id": user_id,
        "kyc_status": "verified",
        "verified_at": "2024-12-19T12:00:00Z"
    }

# ==================== Main ====================

if __name__ == "__main__":
    print("🚀 Starting FinDemo Mock Backend API...")
    print("📍 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🔧 ReDoc: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

