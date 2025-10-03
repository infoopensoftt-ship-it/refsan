from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, timezone
import jwt
import hashlib
import base64
import shutil
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Teknik Servis API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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

class Priority(str, Enum):
    LOW = "dusuk"
    MEDIUM = "orta"
    HIGH = "yuksek"
    URGENT = "acil"

class PaymentStatus(str, Enum):
    PENDING = "beklemede"
    PAID = "odendi"
    PARTIAL = "kismi"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    address: Optional[str] = None
    created_by_technician: Optional[str] = None  # Müşteriyi ekleyen teknisyen ID'si
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: str
    address: Optional[str] = None

class RepairRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    device_type: str
    brand: str
    model: str
    description: str
    priority: Priority
    status: RepairStatus
    assigned_technician_id: Optional[str] = None
    assigned_technician_name: Optional[str] = None
    images: List[str] = []
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

class RepairRequestCreate(BaseModel):
    customer_id: str
    device_type: str
    brand: str
    model: str
    description: str
    priority: Priority = Priority.MEDIUM
    cost_estimate: Optional[float] = None

class RepairRequestUpdate(BaseModel):
    status: Optional[RepairStatus] = None
    assigned_technician_id: Optional[str] = None
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    payment_status: Optional[PaymentStatus] = None

# Utility functions
def verify_password(plain_password, hashed_password):
    """Verify a password against its hash using SHA-256 + salt"""
    return get_password_hash(plain_password) == hashed_password

def get_password_hash(password):
    """Hash a password using SHA-256 + salt"""
    salt = SECRET_KEY.encode('utf-8')
    return base64.b64encode(
        hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    ).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

def require_role(required_roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Authentication routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user_dict = user_data.dict(exclude={"password"})
    user_obj = User(**user_dict)
    
    # Prepare for MongoDB
    user_mongo_dict = user_obj.dict()
    user_mongo_dict["created_at"] = user_mongo_dict["created_at"].isoformat()
    user_mongo_dict["password"] = hashed_password
    
    await db.users.insert_one(user_mongo_dict)
    return user_obj

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Parse user data
    user_data = user.copy()
    if isinstance(user_data.get("created_at"), str):
        user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
    
    user_obj = User(**{k: v for k, v in user_data.items() if k != "password"})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_obj
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Customer routes
@api_router.post("/customers", response_model=Customer)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    customer_dict = customer_data.dict()
    # Teknisyen ise kendi ID'sini ekle
    if current_user.role == UserRole.TECHNICIAN:
        customer_dict["created_by_technician"] = current_user.id
    
    customer_obj = Customer(**customer_dict)
    customer_mongo_dict = customer_obj.dict()
    customer_mongo_dict["created_at"] = customer_mongo_dict["created_at"].isoformat()
    
    await db.customers.insert_one(customer_mongo_dict)
    return customer_obj

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    # Teknisyen sadece kendi müşterilerini görebilir
    query = {}
    if current_user.role == UserRole.TECHNICIAN:
        query["created_by_technician"] = current_user.id
    
    customers = await db.customers.find(query).to_list(1000)
    result = []
    for customer in customers:
        if isinstance(customer.get("created_at"), str):
            customer["created_at"] = datetime.fromisoformat(customer["created_at"])
        result.append(Customer(**customer))
    return result

# Repair Request routes
@api_router.post("/repairs", response_model=RepairRequest)
async def create_repair_request(
    repair_data: RepairRequestCreate,
    current_user: User = Depends(get_current_user)
):
    # Get customer info
    customer = await db.customers.find_one({"id": repair_data.customer_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    repair_dict = repair_data.dict()
    repair_dict["customer_name"] = customer["full_name"]
    repair_dict["status"] = RepairStatus.PENDING
    repair_dict["created_by"] = current_user.id
    
    repair_obj = RepairRequest(**repair_dict)
    
    # Prepare for MongoDB
    repair_mongo_dict = repair_obj.dict()
    repair_mongo_dict["created_at"] = repair_mongo_dict["created_at"].isoformat()
    repair_mongo_dict["updated_at"] = repair_mongo_dict["updated_at"].isoformat()
    if repair_mongo_dict["completed_at"]:
        repair_mongo_dict["completed_at"] = repair_mongo_dict["completed_at"].isoformat()
    
    await db.repairs.insert_one(repair_mongo_dict)
    return repair_obj

@api_router.get("/repairs", response_model=List[RepairRequest])
async def get_repair_requests(current_user: User = Depends(get_current_user)):
    query = {}
    
    # Role-based filtering
    if current_user.role == UserRole.TECHNICIAN:
        query["assigned_technician_id"] = current_user.id
    elif current_user.role == UserRole.CUSTOMER:
        query["created_by"] = current_user.id
    # Admin can see all
    
    repairs = await db.repairs.find(query).to_list(1000)
    result = []
    for repair in repairs:
        if isinstance(repair.get("created_at"), str):
            repair["created_at"] = datetime.fromisoformat(repair["created_at"])
        if isinstance(repair.get("updated_at"), str):
            repair["updated_at"] = datetime.fromisoformat(repair["updated_at"])
        if repair.get("completed_at") and isinstance(repair["completed_at"], str):
            repair["completed_at"] = datetime.fromisoformat(repair["completed_at"])
        result.append(RepairRequest(**repair))
    return result

@api_router.get("/repairs/{repair_id}", response_model=RepairRequest)
async def get_repair_request(repair_id: str, current_user: User = Depends(get_current_user)):
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    # Check permissions
    if (current_user.role == UserRole.TECHNICIAN and repair.get("assigned_technician_id") != current_user.id) or \
       (current_user.role == UserRole.CUSTOMER and repair.get("created_by") != current_user.id):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Parse dates
    if isinstance(repair.get("created_at"), str):
        repair["created_at"] = datetime.fromisoformat(repair["created_at"])
    if isinstance(repair.get("updated_at"), str):
        repair["updated_at"] = datetime.fromisoformat(repair["updated_at"])
    if repair.get("completed_at") and isinstance(repair["completed_at"], str):
        repair["completed_at"] = datetime.fromisoformat(repair["completed_at"])
    
    return RepairRequest(**repair)

@api_router.put("/repairs/{repair_id}", response_model=RepairRequest)
async def update_repair_request(
    repair_id: str,
    repair_update: RepairRequestUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in repair_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Handle technician assignment
    if "assigned_technician_id" in update_data and update_data["assigned_technician_id"]:
        technician = await db.users.find_one({"id": update_data["assigned_technician_id"], "role": UserRole.TECHNICIAN})
        if technician:
            update_data["assigned_technician_name"] = technician["full_name"]
    
    # Handle completion
    if update_data.get("status") == RepairStatus.COMPLETED:
        update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.repairs.update_one({"id": repair_id}, {"$set": update_data})
    
    # Get updated repair
    updated_repair = await db.repairs.find_one({"id": repair_id})
    
    # Parse dates
    if isinstance(updated_repair.get("created_at"), str):
        updated_repair["created_at"] = datetime.fromisoformat(updated_repair["created_at"])
    if isinstance(updated_repair.get("updated_at"), str):
        updated_repair["updated_at"] = datetime.fromisoformat(updated_repair["updated_at"])
    if updated_repair.get("completed_at") and isinstance(updated_repair["completed_at"], str):
        updated_repair["completed_at"] = datetime.fromisoformat(updated_repair["completed_at"])
    
    return RepairRequest(**updated_repair)

# Users management (Admin only)
@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    users = await db.users.find({}, {"password": 0}).to_list(1000)
    result = []
    for user in users:
        if isinstance(user.get("created_at"), str):
            user["created_at"] = datetime.fromisoformat(user["created_at"])
        result.append(User(**user))
    return result

# Stats endpoint
@api_router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        total_repairs = await db.repairs.count_documents({})
        pending_repairs = await db.repairs.count_documents({"status": RepairStatus.PENDING})
        completed_repairs = await db.repairs.count_documents({"status": RepairStatus.COMPLETED})
        total_customers = await db.customers.count_documents({})
        total_technicians = await db.users.count_documents({"role": UserRole.TECHNICIAN})
        
        return {
            "total_repairs": total_repairs,
            "pending_repairs": pending_repairs,
            "completed_repairs": completed_repairs,
            "total_customers": total_customers,
            "total_technicians": total_technicians
        }
    elif current_user.role == UserRole.TECHNICIAN:
        my_repairs = await db.repairs.count_documents({"assigned_technician_id": current_user.id})
        my_pending = await db.repairs.count_documents({
            "assigned_technician_id": current_user.id,
            "status": RepairStatus.PENDING
        })
        my_completed = await db.repairs.count_documents({
            "assigned_technician_id": current_user.id,
            "status": RepairStatus.COMPLETED
        })
        
        return {
            "my_repairs": my_repairs,
            "my_pending": my_pending,
            "my_completed": my_completed
        }
    else:  # Customer
        my_repairs = await db.repairs.count_documents({"created_by": current_user.id})
        my_pending = await db.repairs.count_documents({
            "created_by": current_user.id,
            "status": RepairStatus.PENDING
        })
        
        return {
            "my_repairs": my_repairs,
            "my_pending": my_pending
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()