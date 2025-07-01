# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from enum import Enum
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

engine = create_engine("sqlite:///reports.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Enums
# report_category e nums
class ReportCategory(str, Enum):
    OPERATION = "Operation"
    FINANCE = "Finance"
    RISK = "Risk"
    HR = "HR"
    IT = "IT"

class ReportType(str, Enum):
    TRIAL_BALANCE = "Trial Balance OB_TB001"
    INCOME_STATEMENT = "Income Statement NBE_FIN006"
    BALANCE_SHEET = "Balance Sheet – Institutional	NBE_FIN004"
    BREAKDOWN_OF_INCOME_ACCOUNTS = "Breakdown of Income Accounts BRE_INC001"
    BREAKDOWN_OF__EXPENSES = "Breakdown of Expenses	BRE_EXP001"
    MONTHLY_AVERAGE_RESERVE_REPORT = "Monthly Average Reserve Report NP024"
    LIQUIDITY_REQUIREMENT_REPORT = "Liquidity Requirement Report	NBE_FIN003"
    PROFIT_AND_LOSS_STATEMENT = "Profit and Loss Statement NBE_FIN010"
    BALANCE_SHEET_NBE = "Balance Sheet – NBE NBE_FIN005"
    NON_PERFORMING_LOANS_AND_ADVANCES_AND_PROVISIONS = "Non-Performing Loans and Advances & Provisions	NBE_FIN008"
    LOAN_CLASSIFICATION_AND_PROVISIONING = "Loan Classification and Provisioning NBE_FIN007"
    FIXED_ASSET = "Fixed Asset / PPE OB_FIN003"
    CAPITAL_ADEQUACY_REPORT = "Capital Adequacy Report – On-Balance Sheet NBE_FIN011"
    CAPITAL_ADEQUACY_REPORT_QRTR = "Capital Adequacy Report (Quarterly) – Capital Components NBE_FIN013"
    MATURITY_OF_ASSETS_AND_LIABILITIES = "Maturity of Assets & Liabilities	NBE_FIN014"

    LOAN_AND_ADVANCE_DISBURSEMENT_COLLECTION_AND_OUTSTANDING = "Loan and Advance Disbursement, Collection and Outstanding NBE_LN001"
    LOAN_TO_RELATED_PARTIES = "Loan to Related Parties NBE_LN002"
    BORROWERS_EXCEED_10_PERCENT = "Borrowers Exceed 10 Percent NBE_LN003"
    PERSONAL_INFORMATION_INDIVIDUAL = "Personal Information Individual NBE_PIF001"
    INSURANCE_ACTIVITY_REPORT = "Insurance Activity Report OB_INSU01"
    ARRAERS_BY_AGE_INDIVIDUAL = "Arrears by Age Individual OB_ARR01"
    ARREARS_BENEFICIARY = "Arrears Beneficiary OB_ARR02"


# Parent-Child Mapping
CATEGORY_REPORT_MAPPING = {
    ReportCategory.FINANCE: [
        ReportType.TRIAL_BALANCE,
        ReportType.INCOME_STATEMENT,
        ReportType.BALANCE_SHEET,
        ReportType.BREAKDOWN_OF_INCOME_ACCOUNTS,  
        ReportType.BREAKDOWN_OF__EXPENSES,
        ReportType.MONTHLY_AVERAGE_RESERVE_REPORT,
        ReportType.LIQUIDITY_REQUIREMENT_REPORT,
        ReportType.PROFIT_AND_LOSS_STATEMENT,
        ReportType.BALANCE_SHEET_NBE,
        ReportType.NON_PERFORMING_LOANS_AND_ADVANCES_AND_PROVISIONS,
        ReportType.LOAN_CLASSIFICATION_AND_PROVISIONING,
        ReportType.FIXED_ASSET,
        ReportType.CAPITAL_ADEQUACY_REPORT,
        ReportType.CAPITAL_ADEQUACY_REPORT,
        ReportType.CAPITAL_ADEQUACY_REPORT_QRTR,
        ReportType.MATURITY_OF_ASSETS_AND_LIABILITIES  

    ],
    ReportCategory.OPERATION:
        [ReportType.LOAN_AND_ADVANCE_DISBURSEMENT_COLLECTION_AND_OUTSTANDING,
         ReportType.LOAN_TO_RELATED_PARTIES,
         ReportType.BORROWERS_EXCEED_10_PERCENT,
         ReportType.PERSONAL_INFORMATION_INDIVIDUAL,
         ReportType.INSURANCE_ACTIVITY_REPORT,
         ReportType.ARRAERS_BY_AGE_INDIVIDUAL,
         ReportType.ARREARS_BENEFICIARY
        
         ]
   
}
class CheckerStatus(str, Enum):
    PENDING = "Pending"
    CHECKED = "Checked"
    REJECTED = "Rejected"

class ReviewerStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class Role(str, Enum):
    DISTRICT_USER = "district_user"
    DISTRICT_MANAGER = "district_manager"
    MAIN_OFFICE = "main_office"

class District(str, Enum):
    DISTRICT1 = "District1"
    DISTRICT2 = "District2"
    DISTRICT3 = "Arbaminch"
    DISTRICT4 = "Sodo"
    DISTRICT5 = "Hossana"
    DISTRICT6 = "Karate"
    DISTRICT7 = "Bonga"
    DISTRICT8 = "Jemu"
    DISTRICT9 = "Dilla"
    DISTRICT10 = "Masha"
    DISTRICT11 = "Bonga"
    District12 = "Tarcha"
    DISTRICT13 = "Mizan"
    DISTRICT14 = "Hawassa Sidama"
    DISTRICT15 = "Worabe"
    DISTRICT16 = "Sawla"
    DISTRICT17 = "Welkite"
    District18 = "Jinka"
    DISTRICT19 = "Hawassa Ketema"
    DISTRICT20 = "Durame"
    DISTRIct21 = "Halaba"

# Database Models
class ReportData(Base):
    __tablename__ = "report_data"
    id = Column(Integer, primary_key=True)
    report_type = Column(String)
    report_code = Column(String, unique=True)
    category = Column(String)
    district = Column(String)
    data_json = Column(Text)
    file_content = Column(Text)
    report_metadata = relationship("ReportMetadata", back_populates="data", uselist=False)

class ReportMetadata(Base):
    __tablename__ = "report_metadata"
    id = Column(Integer, primary_key=True)
    report_data_id = Column(Integer, ForeignKey("report_data.id"), nullable=False)
    report_type = Column(String)
    report_code = Column(String)
    title = Column(String)
    description = Column(String)
    prepared_by = Column(String)
    created_date = Column(Date)
    checker_status = Column(String, default="Pending")
    reviewer_status = Column(String, default="Pending")
    checker_comment = Column(String, nullable=True)
    reviewer_comment = Column(String, nullable=True)
    data = relationship("ReportData", back_populates="report_metadata")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    email_address = Column(String, nullable=False)
    role = Column(String, nullable=False)
    district = Column(String, nullable=True)

Base.metadata.create_all(engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    position: str
    email_address: EmailStr
    role: Role
    district: Optional[District] = None

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    position: str
    email_address: str
    role: str
    district: Optional[str] = None
    class Config:
        orm_mode = True

class ReportUpload(BaseModel):
    report_type: ReportType
    report_code: str
    title: str
    description: str
    category: ReportCategory

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class StatusUpdate(BaseModel):
    checker_status: Optional[CheckerStatus] = None
    reviewer_status: Optional[ReviewerStatus] = None
    comment: Optional[str] = None

REPORT_TEMPLATES = {
    "balance_sheet": ["District", "Date", "Assets", "Liabilities", "Equity"],
    "income_statement": ["District", "Date", "Revenue", "Expenses", "Net_Income"],
    "cash_flow": ["District", "Date", "Cash_In", "Cash_Out", "Net_Cash"]
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user(username, db)
        if user is None:
            raise credentials_exception
        return {"username": user.username, "role": user.role, "district": user.district}
    except JWTError:
        raise credentials_exception


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user(current_user["username"], db)
    return user

# Expose enums via endpoint
@app.get("/enums/")
async def get_enums():
    return {
        "categories": [category.value for category in ReportCategory],
        "report_types": [report_type.value for report_type in ReportType],
        "category_report_mapping": {
            category.value: [rt.value for rt in report_type]
            for category, report_type in CATEGORY_REPORT_MAPPING.items()
        }
    }

@app.post("/upload/")
async def upload_file(
    report: ReportUpload = Depends(),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["district_user", "main_office"]:
        raise HTTPException(status_code=403, detail="Only district users or main office can upload reports")
    
    district = current_user["district"] if current_user["role"] == "district_user" else None
    df = pd.read_excel(file.file)
    expected_columns = REPORT_TEMPLATES[report.report_type.value]
    if not all(col in df.columns for col in expected_columns):
        raise HTTPException(status_code=400, detail=f"Invalid {report.report_type.value} template")
    if district and not all(df["District"] == district):
        raise HTTPException(status_code=403, detail="You can only upload data for your own district")

    if db.query(ReportData).filter(ReportData.report_code == report.report_code).first():
        raise HTTPException(status_code=400, detail="Report code already exists")

    file_content = file.file.read()
    report_data = ReportData(
        report_type=report.report_type.value,
        report_code=report.report_code,
        category=report.category.value,
        district=df["District"].iloc[0],
        data_json=df.to_json(orient="records"),
        file_content=file_content.hex()
    )
    db.add(report_data)
    db.flush()  # Ensure report_data.id is generated
    
    metadata = ReportMetadata(
        report_data_id=report_data.id,
        report_type=report.report_type.value,
        report_code=report.report_code,
        title=report.title,
        description=report.description,
        prepared_by=current_user["username"],
        created_date=datetime.now(),
        checker_status=CheckerStatus.PENDING.value,
        reviewer_status=ReviewerStatus.PENDING.value
    )
    db.add(metadata)
    db.commit()
    return {"message": f"Report '{report.report_code}' uploaded successfully"}

@app.put("/reports/{report_code}")
async def update_report(
    report_code: str,
    report_update: ReportUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metadata = db.query(ReportMetadata).filter(ReportMetadata.report_code == report_code).first()
    if not metadata:
        raise HTTPException(status_code=404, detail="Report not found")
    if metadata.prepared_by != current_user["username"] or current_user["role"] != "district_user":
        raise HTTPException(status_code=403, detail="You can only edit your own reports")
    
    if report_update.title:
        metadata.title = report_update.title
    if report_update.description:
        metadata.description = report_update.description
    db.commit()
    return {"message": f"Report '{report_code}' updated successfully"}

@app.delete("/reports/{report_code}")
async def delete_report(
    report_code: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metadata = db.query(ReportMetadata).filter(ReportMetadata.report_code == report_code).first()
    if not metadata:
        raise HTTPException(status_code=404, detail="Report not found")
    if metadata.prepared_by != current_user["username"] or current_user["role"] != "district_user":
        raise HTTPException(status_code=403, detail="You can only delete your own reports")
    
    report_data = db.query(ReportData).filter(ReportData.report_code == report_code).first()
    db.delete(report_data)
    db.delete(metadata)
    db.commit()
    return {"message": f"Report '{report_code}' deleted successfully"}

@app.post("/reports/{report_code}/status")
async def update_status(
    report_code: str,
    status_update: StatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    metadata = db.query(ReportMetadata).filter(ReportMetadata.report_code == report_code).first()
    if not metadata:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if status_update.checker_status:
        if current_user["role"] != "district_manager":
            raise HTTPException(status_code=403, detail="Only district managers can update checker status")
        prepared_by_user = get_user(metadata.prepared_by, db)
        if prepared_by_user.district != current_user["district"]:
            raise HTTPException(status_code=403, detail="You can only update reports from your district")
        metadata.checker_status = status_update.checker_status.value
        metadata.checker_comment = status_update.comment if status_update.checker_status == CheckerStatus.REJECTED else None
    
    if status_update.reviewer_status:
        if current_user["role"] != "main_office":
            raise HTTPException(status_code=403, detail="Only main office can update reviewer status")
        metadata.reviewer_status = status_update.reviewer_status.value
        metadata.reviewer_comment = status_update.comment if status_update.reviewer_status == ReviewerStatus.REJECTED else None
    
    db.commit()
    return {"message": f"Status for report '{report_code}' updated"}

@app.get("/reports/")
async def list_reports(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ReportMetadata).join(ReportData, ReportMetadata.report_data_id == ReportData.id)
    if current_user["role"] in ["district_user", "district_manager"]:
        reports = query.filter(ReportData.district == current_user["district"]).all()
    else:  # main_office
        reports = query.all()
    return [{"report_code": r.report_code, "title": r.title, "description": r.description, "prepared_by": r.prepared_by,
             "created_date": r.created_date, "checker_status": r.checker_status, "reviewer_status": r.reviewer_status,
             "checker_comment": r.checker_comment, "reviewer_comment": r.reviewer_comment} for r in reports]

@app.get("/reports/merged/")
async def merged_reports(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "main_office":
        raise HTTPException(status_code=403, detail="Only main office can view merged reports")
    
    data = db.query(ReportData).join(ReportMetadata).filter(ReportMetadata.reviewer_status == ReviewerStatus.APPROVED.value).all()
    merged = {}
    for d in data:
        report_type = d.report_type
        if report_type not in merged:
            merged[report_type] = []
        df = pd.read_json(d.data_json, orient="records")
        merged[report_type].append(df)
    
    result = {rtype: pd.concat(dfs, ignore_index=True).to_dict(orient="records") for rtype, dfs in merged.items()}
    return result

@app.get("/reports/{report_code}/download")
async def download_report(report_code: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    report = db.query(ReportData).filter(ReportData.report_code == report_code).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user["role"] in ["district_user", "district_manager"] and report.district != current_user["district"]:
        raise HTTPException(status_code=403, detail="You can only download reports from your district")
    
    file_content = bytes.fromhex(report.file_content)
    return {"file_content": file_content.hex(), "filename": f"{report_code}.xlsx"}

@app.get("/users/", response_model=List[UserResponse])
async def list_users(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "main_office":
        raise HTTPException(status_code=403, detail="Only main office can list users")
    users = db.query(User).all()
    return users

@app.post("/users/", response_model=UserResponse)
async def add_user(user: UserCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "main_office":
        raise HTTPException(status_code=403, detail="Only main office can add users")
    
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        position=user.position,
        email_address=user.email_address,
        role=user.role.value,
        district=user.district.value if user.district else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def bootstrap_users(db: Session):
    if not db.query(User).first():
        initial_users = [
            {"username": "district1_user", "password": "district1_pass", "full_name": "John Doe", "position": "Analyst", "email_address": "john.doe@example.com", "role": "district_user", "district": "District1"},
            {"username": "district1_manager", "password": "manager1_pass", "full_name": "Jane Smith", "position": "Manager", "email_address": "jane.smith@example.com", "role": "district_manager", "district": "District1"},
            {"username": "district2_user", "password": "district2_pass", "full_name": "Alice Brown", "position": "Analyst", "email_address": "alice.brown@example.com", "role": "district_user", "district": "District2"},
            {"username": "district2_manager", "password": "manager2_pass", "full_name": "Bob Johnson", "position": "Manager", "email_address": "bob.johnson@example.com", "role": "district_manager", "district": "District2"},
            {"username": "mainoffice_user", "password": "mainoffice_pass", "full_name": "Admin User", "position": "Administrator", "email_address": "admin@example.com", "role": "main_office", "district": None},
        ]
        for user in initial_users:
            db_user = User(
                username=user["username"],
                hashed_password=pwd_context.hash(user["password"]),
                full_name=user["full_name"],
                position=user["position"],
                email_address=user["email_address"],
                role=user["role"],
                district=user["district"]
            )
            db.add(db_user)
        db.commit()

with SessionLocal() as db:
    bootstrap_users(db)

# Run with: uvicorn main:app --reload