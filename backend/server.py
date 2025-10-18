from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
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
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
# Use Emergent's default database name or from env
db_name = os.environ.get('DB_NAME', 'test')  # Emergent uses 'test' as default
db = client[db_name]

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
    APPROVED = "onaylandi"
    IN_PROGRESS = "isleniyor"
    COMPLETED = "tamamlandi"
    CANCELLED = "iptal"
    REJECTED = "reddedildi"

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
    is_approved: bool = False  # Admin onayı için
    requested_role: Optional[UserRole] = None  # Kullanıcının talep ettiği rol
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole  # Kullanıcının talep ettiği rol
    phone: Optional[str] = None

class UserApproval(BaseModel):
    user_id: str
    approved: bool
    role: Optional[UserRole] = None  # Admin onay verirken rolü belirleyecek

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
    images: List[str] = []  # File URLs from upload endpoint

class RepairRequestUpdate(BaseModel):
    status: Optional[RepairStatus] = None
    assigned_technician_id: Optional[str] = None
    cost_estimate: Optional[float] = None
    final_cost: Optional[float] = None
    payment_status: Optional[PaymentStatus] = None

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Optional[str] = None  # "new_repair", "new_customer", "repair_status_update", "repair_cancelled"
    title: str
    message: str
    related_id: Optional[str] = None  # ID of the related customer or repair
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False
    # Enhanced fields for frontend linking
    repair_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    device_info: Optional[str] = None
    new_status: Optional[str] = None


class StockCategory(str, Enum):
    SPARE_PART = "yedek_parca"
    CHEMICAL = "kimyasal"
    MATERIAL = "malzeme"
    TOOL = "alet"

class StockItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: StockCategory
    quantity: float
    unit: str  # adet, kg, litre, metre
    min_quantity: float  # Minimum stok seviyesi
    supplier: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StockItemCreate(BaseModel):
    name: str
    category: StockCategory
    quantity: float
    unit: str
    min_quantity: float
    supplier: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class StockUpdate(BaseModel):
    quantity: float
    operation: str  # "add" or "subtract"
    note: Optional[str] = None



# SMS Configuration
SMS_API_KEY = os.environ.get('SMS_API_KEY', '')
SMS_API_URL = os.environ.get('SMS_API_URL', 'https://api.netgsm.com.tr/sms/send/get')  # Default Netgsm
SMS_SENDER = os.environ.get('SMS_SENDER', 'REFSAN')

async def send_sms(phone: str, message: str):
    """Send SMS to customer - supports both real API and mock mode"""
    try:
        if not SMS_API_KEY or SMS_API_KEY == 'MOCK':
            # Mock mode - just log the SMS
            logger.info(f"📱 [MOCK SMS] To: {phone}, Message: {message}")
            return {"success": True, "message": "SMS sent (mock mode)", "mock": True}
        
        # Real SMS API call (Netgsm format)
        import requests
        
        # Clean phone number (remove spaces, dashes, etc.)
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('90'):
            clean_phone = '90' + clean_phone
        
        # Netgsm API parameters
        params = {
            'usercode': os.environ.get('SMS_USERNAME', ''),
            'password': SMS_API_KEY,
            'gsmno': clean_phone,
            'message': message,
            'msgheader': SMS_SENDER
        }
        
        response = requests.get(SMS_API_URL, params=params, timeout=10)
        
        if response.status_code == 200 and response.text.startswith('00'):
            logger.info(f"✅ SMS sent to {phone}")
            return {"success": True, "message": "SMS sent successfully"}
        else:
            logger.error(f"❌ SMS failed: {response.text}")
            return {"success": False, "message": f"SMS failed: {response.text}"}
            
    except Exception as e:
        logger.error(f"SMS error: {str(e)}")
        return {"success": False, "message": f"SMS error: {str(e)}"}

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt"""
    try:
        # Bcrypt requires bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        logging.error(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

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

async def create_notification(notification_type: str, title: str, message: str, related_id: str, extra_data: dict = None):
    """Helper function to create notifications"""
    notification = Notification(
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id
    )
    
    notification_dict = notification.dict()
    notification_dict["created_at"] = notification_dict["created_at"].isoformat()
    
    # Add extra data if provided
    if extra_data:
        notification_dict.update(extra_data)
    
    await db.notifications.insert_one(notification_dict)
    return notification

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
    
    # Create user with pending approval
    user_dict = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "role": user_data.role,  # Varsayılan rol, admin değiştirebilir
        "requested_role": user_data.role,  # Kullanıcının talep ettiği rol
        "is_active": True,
        "is_approved": False,  # Admin onayı bekliyor
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Admin bildirimi oluştur
    admins = await db.users.find({"role": "admin", "is_approved": True}).to_list(100)
    role_display = {
        "admin": "Admin",
        "teknisyen": "Teknisyen",
        "musteri": "Müşteri"
    }
    for admin in admins:
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": admin["id"],
            "type": "new_user_registration",
            "title": "Yeni Kullanıcı Kaydı",
            "message": f"{user_data.full_name} ({user_data.email}) sisteme kayıt oldu. Rol talebi: {role_display.get(user_data.role, user_data.role)}",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": {"new_user_id": user_dict["id"]}
        }
        await db.notifications.insert_one(notification)
    
    # Return user without password
    user_dict_response = {k: v for k, v in user_dict.items() if k != "hashed_password"}
    if isinstance(user_dict_response.get("created_at"), str):
        user_dict_response["created_at"] = datetime.fromisoformat(user_dict_response["created_at"])
    
    return User(**user_dict_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
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
    
    # Onay kontrolü - Admin onayı bekleyen kullanıcılar giriş yapamaz
    if not user.get("is_approved", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending admin approval"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Parse user data
    user_data = user.copy()
    if isinstance(user_data.get("created_at"), str):
        user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
    
    user_obj = User(**{k: v for k, v in user_data.items() if k != "hashed_password"})
    
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
    
    # Create notification for new customer
    await create_notification(
        notification_type="new_customer",
        title="Yeni Müşteri Eklendi",
        message=f"{customer_obj.full_name} adlı yeni müşteri eklendi",
        related_id=customer_obj.id
    )
    
    return customer_obj

# File upload endpoint
@api_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.docx', '.doc', '.txt'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (10MB max)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large. Maximum size is 10MB"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path(ROOT_DIR) / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Return file info
        return {
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_size": len(content),
            "file_url": f"/uploads/{unique_filename}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@api_router.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    try:
        uploaded_files = []
        
        for file in files:
            # Validate file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.docx', '.doc', '.txt'}
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed for {file.filename}. Allowed types: {', '.join(allowed_extensions)}"
                )
            
            # Check file size (10MB max)
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size too large for {file.filename}. Maximum size is 10MB"
                )
            
            # Create uploads directory if it doesn't exist
            upload_dir = Path(ROOT_DIR) / "uploads"
            upload_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Add to uploaded files list
            uploaded_files.append({
                "filename": unique_filename,
                "original_filename": file.filename,
                "file_size": len(content),
                "file_url": f"/uploads/{unique_filename}"
            })
        
        return {"uploaded_files": uploaded_files}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

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


@api_router.get("/customers/me", response_model=Customer)
async def get_my_customer_record(
    current_user: User = Depends(get_current_user)
):
    """Get or create customer record for logged-in customer user"""
    # Find customer by email
    customer = await db.customers.find_one({"email": current_user.email})
    
    if not customer:
        # Auto-create customer record for customer users
        if current_user.role == UserRole.CUSTOMER:
            new_customer = Customer(
                full_name=current_user.full_name,
                email=current_user.email,
                phone=current_user.phone or "",
                address="",
                created_by_technician=None
            )
            customer_dict = new_customer.dict()
            customer_dict["created_at"] = customer_dict["created_at"].isoformat()
            await db.customers.insert_one(customer_dict)
            return new_customer
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer record not found"
            )
    
    if isinstance(customer.get("created_at"), str):
        customer["created_at"] = datetime.fromisoformat(customer["created_at"])
    return Customer(**customer)

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Teknisyen sadece kendi müşterilerini görebilir
    if current_user.role == UserRole.TECHNICIAN and customer.get("created_by_technician") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if isinstance(customer.get("created_at"), str):
        customer["created_at"] = datetime.fromisoformat(customer["created_at"])
    return Customer(**customer)

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_update: CustomerUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Teknisyen sadece kendi müşterilerini güncelleyebilir
    if current_user.role == UserRole.TECHNICIAN and customer.get("created_by_technician") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in customer_update.dict().items() if v is not None}
    
    if update_data:
        await db.customers.update_one({"id": customer_id}, {"$set": update_data})
    
    # Get updated customer
    updated_customer = await db.customers.find_one({"id": customer_id})
    if isinstance(updated_customer.get("created_at"), str):
        updated_customer["created_at"] = datetime.fromisoformat(updated_customer["created_at"])
    
    return Customer(**updated_customer)

@api_router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Teknisyen sadece kendi müşterilerini silebilir
    if current_user.role == UserRole.TECHNICIAN and customer.get("created_by_technician") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete all repairs for this customer first
    await db.repairs.delete_many({"customer_id": customer_id})
    
    # Delete the customer
    result = await db.customers.delete_one({"id": customer_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {"message": "Customer and all associated repairs deleted successfully"}

@api_router.get("/customers/{customer_id}/repairs", response_model=List[RepairRequest])
async def get_customer_repairs(
    customer_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    # First check if customer exists
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Teknisyen sadece kendi müşterilerini görebilir
    if current_user.role == UserRole.TECHNICIAN and customer.get("created_by_technician") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    repairs = await db.repairs.find({"customer_id": customer_id}).to_list(1000)
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

# Search functionality
@api_router.get("/search")
async def search_data(
    query: str,
    type: Optional[str] = None,  # "customers", "repairs", or None for both
    current_user: User = Depends(get_current_user)
):
    results = {"customers": [], "repairs": []}
    
    if not query or len(query.strip()) < 2:
        return results
    
    query = query.strip()
    
    # Search customers
    if type is None or type == "customers":
        customer_query = {
            "$or": [
                {"full_name": {"$regex": query, "$options": "i"}},
                {"phone": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}},
                {"address": {"$regex": query, "$options": "i"}}
            ]
        }
        
        # Apply role-based filtering
        if current_user.role == UserRole.TECHNICIAN:
            customer_query["created_by_technician"] = current_user.id
        elif current_user.role == UserRole.CUSTOMER:
            customer_query["email"] = current_user.email
        
        customers = await db.customers.find(customer_query).to_list(100)
        for customer in customers:
            if isinstance(customer.get("created_at"), str):
                customer["created_at"] = datetime.fromisoformat(customer["created_at"])
            results["customers"].append(Customer(**customer))
    
    # Search repairs
    if type is None or type == "repairs":
        repair_query = {
            "$or": [
                {"customer_name": {"$regex": query, "$options": "i"}},
                {"device_type": {"$regex": query, "$options": "i"}},
                {"brand": {"$regex": query, "$options": "i"}},
                {"model": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"status": {"$regex": query, "$options": "i"}},
                {"priority": {"$regex": query, "$options": "i"}}
            ]
        }
        
        # Apply role-based filtering (same as get_repair_requests)
        if current_user.role == UserRole.TECHNICIAN:
            customer_ids = []
            customers = await db.customers.find({"created_by_technician": current_user.id}).to_list(1000)
            customer_ids = [customer["id"] for customer in customers]
            
            repair_query = {
                "$and": [
                    repair_query,
                    {
                        "$or": [
                            {"assigned_technician_id": current_user.id},
                            {"customer_id": {"$in": customer_ids}},
                            {"created_by": current_user.id}
                        ]
                    }
                ]
            }
        elif current_user.role == UserRole.CUSTOMER:
            repair_query["created_by"] = current_user.id
        
        repairs = await db.repairs.find(repair_query).to_list(100)
        for repair in repairs:
            if isinstance(repair.get("created_at"), str):
                repair["created_at"] = datetime.fromisoformat(repair["created_at"])
            if isinstance(repair.get("updated_at"), str):
                repair["updated_at"] = datetime.fromisoformat(repair["updated_at"])
            if repair.get("completed_at") and isinstance(repair["completed_at"], str):
                repair["completed_at"] = datetime.fromisoformat(repair["completed_at"])
            results["repairs"].append(RepairRequest(**repair))
    
    return results

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
    
    # Teknisyen sadece kendi müşterileri için arıza açabilir
    # Müşteri kendi adına arıza açabilir
    if current_user.role == UserRole.TECHNICIAN:
        if customer.get("created_by_technician") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create repairs for your own customers"
            )
    elif current_user.role == UserRole.CUSTOMER:
        # Müşteri kendi adına arıza açıyor, customer kaydında email kontrolü
        if customer.get("email") != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create repairs for yourself"
            )
    
    repair_dict = repair_data.dict()
    repair_dict["customer_name"] = customer["full_name"]
    repair_dict["customer_phone"] = customer.get("phone", "")
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
    
    # Create notification for new repair
    await create_notification(
        notification_type="new_repair",
        title="Yeni Arıza Kaydı",
        message=f"{repair_obj.customer_name} için yeni arıza: {repair_obj.device_type} {repair_obj.brand}",
        related_id=repair_obj.id,
        extra_data={
            "repair_id": repair_obj.id,
            "customer_name": repair_obj.customer_name,
            "device_info": f"{repair_obj.device_type} {repair_obj.brand} {repair_obj.model}"
        }
    )
    
    return repair_obj

@api_router.get("/repairs", response_model=List[RepairRequest])
async def get_repair_requests(current_user: User = Depends(get_current_user)):
    query = {}
    
    # Role-based filtering
    if current_user.role == UserRole.TECHNICIAN:
        # Teknisyen hem atanan işleri hem kendi eklediği müşterilerin arızalarını görebilir
        customer_ids = []
        customers = await db.customers.find({"created_by_technician": current_user.id}).to_list(1000)
        customer_ids = [customer["id"] for customer in customers]
        
        query = {
            "$or": [
                {"assigned_technician_id": current_user.id},
                {"customer_id": {"$in": customer_ids}},
                {"created_by": current_user.id}
            ]
        }
    elif current_user.role == UserRole.CUSTOMER:
        query["created_by"] = current_user.id
    # Admin can see all
    
    repairs = await db.repairs.find(query).to_list(1000)
    result = []
    for repair in repairs:
        # Get customer info for phone
        if repair.get("customer_id"):
            customer = await db.customers.find_one({"id": repair["customer_id"]})
            if customer:
                repair["customer_phone"] = customer.get("phone", "")
        
        if isinstance(repair.get("created_at"), str):
            repair["created_at"] = datetime.fromisoformat(repair["created_at"])
        if isinstance(repair.get("updated_at"), str):
            repair["updated_at"] = datetime.fromisoformat(repair["updated_at"])
        if repair.get("completed_at") and isinstance(repair["completed_at"], str):
            repair["completed_at"] = datetime.fromisoformat(repair["completed_at"])
        result.append(RepairRequest(**repair))
    return result

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
    
    # Create notification for status update if status changed
    if "status" in update_data:
        await create_notification(
            notification_type="repair_status_update",
            title="Arıza Durumu Güncellendi",
            message=f"{repair['customer_name']} - {repair['device_type']}: {update_data['status']}",
            related_id=repair_id,
            extra_data={
                "repair_id": repair_id,
                "customer_name": repair['customer_name'],
                "device_info": f"{repair['device_type']} {repair['brand']} {repair['model']}",
                "new_status": update_data['status']
            }
        )
    
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

@api_router.get("/repairs/{repair_id}", response_model=RepairRequest)
async def get_repair_request(
    repair_id: str,
    current_user: User = Depends(get_current_user)
):
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    # Check permissions based on role
    if current_user.role == UserRole.TECHNICIAN:
        # Technician can view repairs they created or are assigned to
        customer_ids = []
        customers = await db.customers.find({"created_by_technician": current_user.id}).to_list(1000)
        customer_ids = [customer["id"] for customer in customers]
        
        if (repair.get("created_by") != current_user.id and 
            repair.get("assigned_technician_id") != current_user.id and
            repair.get("customer_id") not in customer_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.CUSTOMER:
        # Customer can only view their own repairs
        if repair.get("created_by") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    # Admin can view all repairs (no additional check needed)
    
    # Parse dates
    if isinstance(repair.get("created_at"), str):
        repair["created_at"] = datetime.fromisoformat(repair["created_at"])
    if isinstance(repair.get("updated_at"), str):
        repair["updated_at"] = datetime.fromisoformat(repair["updated_at"])
    if repair.get("completed_at") and isinstance(repair["completed_at"], str):
        repair["completed_at"] = datetime.fromisoformat(repair["completed_at"])
    
    return RepairRequest(**repair)

@api_router.delete("/repairs/{repair_id}")
async def delete_repair_request(
    repair_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    # Check permissions - admin can delete any repair, technician can only delete own repairs
    if current_user.role == UserRole.TECHNICIAN:
        if repair.get("created_by") != current_user.id and repair.get("assigned_technician_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    result = await db.repairs.delete_one({"id": repair_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    return {"message": "Repair request deleted successfully"}

@api_router.put("/repairs/{repair_id}/cancel")
async def cancel_repair_request(
    repair_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TECHNICIAN]))
):
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repair request not found"
        )
    
    # Check permissions - admin can cancel any repair, technician can only cancel own repairs
    if current_user.role == UserRole.TECHNICIAN:
        if repair.get("created_by") != current_user.id and repair.get("assigned_technician_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Update repair status to cancelled
    update_data = {
        "status": RepairStatus.CANCELLED,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.repairs.update_one({"id": repair_id}, {"$set": update_data})
    
    # Create notification for cancellation
    await create_notification(
        notification_type="repair_cancelled",
        title="Arıza İptal Edildi",
        message=f"{repair['customer_name']} - {repair['device_type']}: İptal edildi",
        related_id=repair_id,
        extra_data={
            "repair_id": repair_id,
            "customer_name": repair['customer_name'],
            "device_info": f"{repair['device_type']} {repair['brand']} {repair['model']}"
        }
    )
    
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



@api_router.put("/repairs/{repair_id}/status")
async def update_repair_status(
    repair_id: str,
    status: RepairStatus,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update repair status (Admin only) and send SMS notification"""
    # Find repair
    repair = await db.repairs.find_one({"id": repair_id})
    if not repair:
        raise HTTPException(status_code=404, detail="Repair not found")
    
    # Get customer info
    customer = await db.customers.find_one({"id": repair["customer_id"]})
    
    # Update status
    await db.repairs.update_one(
        {"id": repair_id},
        {"$set": {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Send SMS notification to customer
    if customer and customer.get("phone"):
        status_messages = {
            RepairStatus.APPROVED: "Arıza kaydınız onaylandı ve işleme alındı.",
            RepairStatus.IN_PROGRESS: "Arıza kaydınız işleniyor.",
            RepairStatus.COMPLETED: "Arıza kaydınız tamamlandı.",
            RepairStatus.CANCELLED: "Arıza kaydınız iptal edildi.",
            RepairStatus.REJECTED: "Arıza kaydınız reddedildi."
        }
        
        sms_message = f"Refsan Technical: {customer['full_name']}, {status_messages.get(status, 'Arıza durumu güncellendi.')} Arıza No: {repair_id[:8]}"
        
        # Send SMS
        sms_result = await send_sms(customer["phone"], sms_message)
        logger.info(f"SMS result for repair {repair_id}: {sms_result}")
    
    # Create notification for admin
    await db.notifications.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "repair_id": repair_id,
        "title": f"Arıza Durumu Güncellendi",
        "message": f"{customer['full_name'] if customer else 'Müşteri'} - Durum: {status}",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"success": True, "status": status, "sms_sent": customer and customer.get("phone") is not None}

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


@api_router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update user role (Admin only)"""
    # Find user
    existing_user = await db.users.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update role
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role}}
    )
    
    return {"success": True, "message": f"User role updated to {role}"}


@api_router.get("/users/pending", response_model=List[User])
async def get_pending_users(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    """Get all pending users waiting for approval"""
    users = await db.users.find({"is_approved": False}, {"hashed_password": 0}).to_list(1000)
    result = []
    for user in users:
        if isinstance(user.get("created_at"), str):
            user["created_at"] = datetime.fromisoformat(user["created_at"])
        result.append(User(**user))
    return result


@api_router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: str,
    approval_data: UserApproval,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Approve or reject user registration"""
    # Find user
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("is_approved", False):
        raise HTTPException(status_code=400, detail="User already approved/rejected")
    
    if approval_data.approved:
        # Onay ver
        update_data = {
            "is_approved": True,
            "role": approval_data.role if approval_data.role else user.get("requested_role", UserRole.CUSTOMER)
        }
        
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Kullanıcıya bildirim gönder
        role_display = {
            "admin": "Admin",
            "teknisyen": "Teknisyen", 
            "musteri": "Müşteri"
        }
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "account_approved",
            "title": "Hesap Onaylandı",
            "message": f"Hesabınız onaylandı! Rol: {role_display.get(update_data['role'], update_data['role'])}. Artık giriş yapabilirsiniz.",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)
        
        return {"success": True, "message": "User approved successfully", "role": update_data['role']}
    else:
        # Reddet - kullanıcıyı sil
        await db.users.delete_one({"id": user_id})
        
        return {"success": True, "message": "User registration rejected and removed"}


@api_router.get("/users/pending/count")
async def get_pending_users_count(current_user: User = Depends(require_role([UserRole.ADMIN]))):
    """Get count of pending users"""
    count = await db.users.count_documents({"is_approved": False})
    return {"count": count}


# Technician report endpoint
@api_router.get("/reports/technician/{technician_id}")
async def get_technician_report(
    technician_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    # Get technician info
    technician = await db.users.find_one({"id": technician_id, "role": UserRole.TECHNICIAN})
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found"
        )
    
    # Get technician's customers
    customers = await db.customers.find({"created_by_technician": technician_id}).to_list(1000)
    
    # Get technician's repairs
    repairs = await db.repairs.find({
        "$or": [
            {"assigned_technician_id": technician_id},
            {"created_by": technician_id}
        ]
    }).to_list(1000)
    
    # Calculate totals
    total_repairs = len(repairs)
    total_cost = sum(repair.get("final_cost", 0) for repair in repairs if repair.get("final_cost"))
    total_estimate = sum(repair.get("cost_estimate", 0) for repair in repairs if repair.get("cost_estimate"))
    
    # Group by dates
    repairs_by_date = {}
    for repair in repairs:
        if isinstance(repair.get("created_at"), str):
            date_str = repair["created_at"][:10]  # Get YYYY-MM-DD
        else:
            date_str = repair.get("created_at", datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        
        if date_str not in repairs_by_date:
            repairs_by_date[date_str] = []
        repairs_by_date[date_str].append(repair)
    
    return {
        "technician": {
            "id": technician["id"],
            "full_name": technician["full_name"],
            "email": technician["email"],
            "phone": technician.get("phone")
        },
        "summary": {
            "total_customers": len(customers),
            "total_repairs": total_repairs,
            "total_cost": total_cost,
            "total_estimate": total_estimate
        },
        "customers": customers,
        "repairs": repairs,
        "repairs_by_date": repairs_by_date
    }

# Stats endpoint
@api_router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        total_repairs = await db.repairs.count_documents({})
        pending_repairs = await db.repairs.count_documents({"status": RepairStatus.PENDING})
        completed_repairs = await db.repairs.count_documents({"status": RepairStatus.COMPLETED})
        total_customers = await db.customers.count_documents({})
        total_technicians = await db.users.count_documents({"role": UserRole.TECHNICIAN})
        
        # Calculate total payments (completed repairs with final_cost)
        total_paid_amount = 0.0
        total_unpaid_amount = 0.0
        paid_count = 0
        unpaid_count = 0
        
        repairs_cursor = db.repairs.find({})
        async for repair in repairs_cursor:
            if repair.get("final_cost") and repair.get("final_cost") > 0:
                if repair.get("payment_status") == "odendi":
                    total_paid_amount += repair["final_cost"]
                    paid_count += 1
                else:
                    total_unpaid_amount += repair["final_cost"]
                    unpaid_count += 1
        
        return {
            "total_repairs": total_repairs,
            "pending_repairs": pending_repairs,
            "completed_repairs": completed_repairs,
            "total_customers": total_customers,
            "total_technicians": total_technicians,
            "total_paid_amount": total_paid_amount,
            "total_unpaid_amount": total_unpaid_amount,
            "paid_repairs": paid_count,
            "unpaid_repairs": unpaid_count
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

# Notifications endpoint
@api_router.get("/notifications")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    query = {}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    result = []
    for notification in notifications:
        if isinstance(notification.get("created_at"), str):
            notification["created_at"] = datetime.fromisoformat(notification["created_at"])
        result.append(Notification(**notification))
    return result

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    result = await db.notifications.update_one(
        {"id": notification_id}, 
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}

@api_router.get("/notifications/unread-count")
async def get_unread_notifications_count(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    count = await db.notifications.count_documents({"read": False})
    return {"unread_count": count}

@api_router.delete("/notifications/clear-all")
async def clear_all_notifications(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    result = await db.notifications.delete_many({})
    return {"message": f"{result.deleted_count} notifications cleared"}

@api_router.delete("/admin/repairs/delete-all")
async def delete_all_repairs(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    result = await db.repairs.delete_many({})
    return {"message": f"{result.deleted_count} repair records deleted"}

@api_router.delete("/admin/customers/delete-all")
async def delete_all_customers(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    # First delete all repairs (cascade delete)
    repairs_result = await db.repairs.delete_many({})
    # Then delete all customers
    customers_result = await db.customers.delete_many({})
    return {
        "message": f"{customers_result.deleted_count} customers and {repairs_result.deleted_count} repair records deleted"
    }

@api_router.delete("/admin/system/reset")
async def reset_system(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    # Delete all data except admin users
    repairs_result = await db.repairs.delete_many({})
    customers_result = await db.customers.delete_many({})
    notifications_result = await db.notifications.delete_many({})
    # Keep admin users, delete others
    users_result = await db.users.delete_many({"role": {"$ne": "admin"}})
    
    return {
        "message": f"System reset complete: {repairs_result.deleted_count} repairs, {customers_result.deleted_count} customers, {notifications_result.deleted_count} notifications, {users_result.deleted_count} non-admin users deleted"
    }

@api_router.post("/admin/demo/create-data")
async def create_demo_data(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    # Refsan Türkiye demo data - ceramic machinery company
    demo_customers = [
        {
            "id": str(uuid.uuid4()),
            "full_name": "Ankara Seramik A.Ş.",
            "email": "info@ankaraseramik.com",
            "phone": "0312 456 7890",
            "address": "Ostim OSB, Ankara",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "İstanbul Çini Fabrikası",
            "email": "uretim@istanbulcini.com",
            "phone": "0216 345 6789",
            "address": "Kartal Sanayi Sitesi, İstanbul",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "Ege Karo Ltd. Şti.",
            "email": "siparis@egekaro.com",
            "phone": "0232 567 8901",
            "address": "Kemalpaşa OSB, İzmir",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "Bursa Porselen San.",
            "email": "fabrika@bursaporselen.com",
            "phone": "0224 678 9012",
            "address": "Nilüfer Sanayi Bölgesi, Bursa",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "full_name": "Kütahya Çini Atölyesi",
            "email": "atolye@kutahyacini.com",
            "phone": "0274 789 0123",
            "address": "Merkez, Kütahya",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    # Insert demo customers
    await db.customers.insert_many(demo_customers)
    
    # Create demo repair requests for ceramic machinery
    demo_repairs = [
        {
            "id": str(uuid.uuid4()),
            "customer_id": demo_customers[0]["id"],
            "customer_name": demo_customers[0]["full_name"],
            "device_type": "Seramik Fırını",
            "brand": "Refsan",
            "model": "RF-2500",
            "description": "Fırın sıcaklık kontrolü arızalı. 1200°C'ye çıkarken ani düşüş yaşanıyor. Termostat değişimi gerekebilir.",
            "status": RepairStatus.PENDING,
            "priority": Priority.HIGH,
            "cost_estimate": 15000.0,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": demo_customers[1]["id"],
            "customer_name": demo_customers[1]["full_name"],
            "device_type": "Çini Presi",
            "brand": "Refsan",
            "model": "RP-150",
            "description": "Hidrolik sistem basınç kaybı yaşıyor. Çini kalıpları tam olarak şekillendirilemiyor. Conta değişimi gerekli.",
            "status": RepairStatus.IN_PROGRESS,
            "priority": Priority.MEDIUM,
            "cost_estimate": 8500.0,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": demo_customers[2]["id"],
            "customer_name": demo_customers[2]["full_name"],
            "device_type": "Karo Kesim Makinesi",
            "brand": "Refsan",
            "model": "RK-300",
            "description": "Kesim diskinin titreşim yapması. Kesim kalitesi düşmüş. Motor yatakları kontrol edilmeli.",
            "status": RepairStatus.COMPLETED,
            "priority": Priority.MEDIUM,
            "cost_estimate": 5200.0,
            "final_cost": 4800.0,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": demo_customers[3]["id"],
            "customer_name": demo_customers[3]["full_name"],
            "device_type": "Porselen Kalıplama Makinesi",
            "brand": "Refsan",
            "model": "PK-500",
            "description": "Kalıplama işlemi sırasında hava kabarcığı oluşumu. Vakum sistemi kontrol edilmeli.",
            "status": RepairStatus.PENDING,
            "priority": Priority.LOW,
            "cost_estimate": 3200.0,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        },
        {
            "id": str(uuid.uuid4()),
            "customer_id": demo_customers[4]["id"],
            "customer_name": demo_customers[4]["full_name"],
            "device_type": "Çini Sırlama Makinesi",
            "brand": "Refsan",
            "model": "RS-800",
            "description": "Sır püskürtme memelerinde tıkanma. Homojen sırlama yapılamıyor. Temizlik ve ayar gerekli.",
            "status": RepairStatus.PENDING,
            "priority": Priority.URGENT,
            "cost_estimate": 2800.0,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "images": []
        }
    ]
    
    # Insert demo repair requests
    await db.repairs.insert_many(demo_repairs)
    
    return {
        "customers_created": len(demo_customers),
        "repairs_created": len(demo_repairs),
        "message": "Refsan Türkiye demo data created successfully"
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


# ==================== STOCK MANAGEMENT ====================

@api_router.get("/stock", response_model=List[StockItem])
async def get_stock_items(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Get all stock items (Admin only)"""
    stock_items = await db.stock.find().to_list(1000)
    result = []
    for item in stock_items:
        if isinstance(item.get("created_at"), str):
            item["created_at"] = datetime.fromisoformat(item["created_at"])
        if isinstance(item.get("updated_at"), str):
            item["updated_at"] = datetime.fromisoformat(item["updated_at"])
        result.append(StockItem(**item))
    return result

@api_router.post("/stock", response_model=StockItem)
async def create_stock_item(
    stock_data: StockItemCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Create new stock item (Admin only)"""
    stock_item = StockItem(**stock_data.dict())
    
    # Prepare for MongoDB
    stock_dict = stock_item.dict()
    stock_dict["created_at"] = stock_dict["created_at"].isoformat()
    stock_dict["updated_at"] = stock_dict["updated_at"].isoformat()
    
    await db.stock.insert_one(stock_dict)
    return stock_item

@api_router.put("/stock/{stock_id}", response_model=StockItem)
async def update_stock_item(
    stock_id: str,
    stock_data: StockItemCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update stock item (Admin only)"""
    existing_item = await db.stock.find_one({"id": stock_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Stock item not found")
    
    # Update fields
    update_dict = stock_data.dict()
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.stock.update_one({"id": stock_id}, {"$set": update_dict})
    
    # Fetch updated item
    updated_item = await db.stock.find_one({"id": stock_id})
    if isinstance(updated_item.get("created_at"), str):
        updated_item["created_at"] = datetime.fromisoformat(updated_item["created_at"])
    if isinstance(updated_item.get("updated_at"), str):
        updated_item["updated_at"] = datetime.fromisoformat(updated_item["updated_at"])
    
    return StockItem(**updated_item)

@api_router.post("/stock/{stock_id}/quantity")
async def update_stock_quantity(
    stock_id: str,
    stock_update: StockUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Update stock quantity (add or subtract) (Admin only)"""
    existing_item = await db.stock.find_one({"id": stock_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Stock item not found")
    
    current_quantity = existing_item["quantity"]
    
    if stock_update.operation == "add":
        new_quantity = current_quantity + stock_update.quantity
    elif stock_update.operation == "subtract":
        new_quantity = current_quantity - stock_update.quantity
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    
    await db.stock.update_one(
        {"id": stock_id},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "new_quantity": new_quantity}

@api_router.delete("/stock/{stock_id}")
async def delete_stock_item(
    stock_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete stock item (Admin only)"""
    result = await db.stock.delete_one({"id": stock_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Stock item not found")
    return {"success": True}

@api_router.get("/stock/low-stock")
async def get_low_stock_items(
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Get items below minimum stock level"""
    stock_items = await db.stock.find().to_list(1000)
    low_stock = [
        StockItem(**item) 
        for item in stock_items 
        if item["quantity"] <= item["min_quantity"]
    ]
    return low_stock

# Serve uploaded files
upload_dir = Path(ROOT_DIR) / "uploads"
upload_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Startup event to create first admin user
@app.on_event("startup")
async def create_first_admin():
    """Create first admin user on startup if no users exist"""
    try:
        # Check if any users exist
        user_count = await db.users.count_documents({})
        if user_count == 0:
            # Create default admin user
            admin_user = {
                "id": str(uuid.uuid4()),
                "email": "admin@demo.com",
                "full_name": "Admin User",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "phone": "05551234567",
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
            
            await db.users.insert_one(admin_user)
            logging.info("✅ First admin user created: admin@demo.com / admin123")
        else:
            logging.info(f"ℹ️ Database already has {user_count} users")
    except Exception as e:
        logging.error(f"❌ Error creating first admin user: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()