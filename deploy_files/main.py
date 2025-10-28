from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import jwt
import uuid
import os
from pathlib import Path
from enum import Enum

# Initialize FastAPI
app = FastAPI(title="Refsan Türkiye Teknik Servis API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://demo:demo123@cluster0.mongodb.net/refsan_db?retryWrites=true&w=majority")
client = AsyncIOMotorClient(MONGO_URL)
db = client.refsan_db

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "refsan_secret_key_2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Root directory
ROOT_DIR = Path(__file__).parent

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICIAN = "teknisyen"
    CUSTOMER = "musteri"

class RepairStatus(str, Enum):
    PENDING = "beklemede"
    IN_PROGRESS = "isleniyor"
    COMPLETED = "tamamlandi"
    CANCELLED = "iptal"

class RepairPriority(str, Enum):
    LOW = "dusuk"
    MEDIUM = "orta"
    HIGH = "yuksek"
    URGENT = "acil"

class PaymentStatus(str, Enum):
    PENDING = "beklemede"
    PAID = "odendi"
    PARTIAL = "kismi"

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: UserRole
    phone: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    address: Optional[str] = None
    created_by_technician: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RepairRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    device_type: str
    brand: str
    model: Optional[str] = None
    description: str
    status: RepairStatus = RepairStatus.PENDING
    priority: RepairPriority = RepairPriority.MEDIUM
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    payment_status: Optional[PaymentStatus] = None
    assigned_technician_id: Optional[str] = None
    assigned_technician_name: Optional[str] = None
    images: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    if isinstance(user.get("created_at"), str):
        user["created_at"] = datetime.fromisoformat(user["created_at"])
    
    return User(**user)

# Router
api_router = APIRouter(prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Refsan Türkiye Teknik Servis API", "status": "running"}

# Auth endpoints
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "phone": user_data.phone,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    user_obj = User(**user_dict)
    access_token = create_access_token(data={"sub": user_obj.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_obj
    }

@api_router.post("/auth/login")
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    if isinstance(user.get("created_at"), str):
        user["created_at"] = datetime.fromisoformat(user["created_at"])
    
    user_obj = User(**user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_obj
    }

# Stats endpoint
@api_router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    total_repairs = await db.repairs.count_documents({})
    total_customers = await db.customers.count_documents({})
    pending_repairs = await db.repairs.count_documents({"status": "beklemede"})
    completed_repairs = await db.repairs.count_documents({"status": "tamamlandi"})
    
    return {
        "total_repairs": total_repairs,
        "total_customers": total_customers,
        "pending_repairs": pending_repairs,
        "completed_repairs": completed_repairs
    }

# Include router
app.include_router(api_router)

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)