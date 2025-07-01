from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Text

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/hrs"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class ReportData(Base):
    __tablename__ = "report_data"
    id = Column(Integer, primary_key=True)
    report_type = Column(String)
    district = Column(String)
    data_json = Column(Text)

class ReportMetadata(Base):
    __tablename__ = "report_metadata"
    id = Column(Integer, primary_key=True)
    report_type = Column(String)
    filename = Column(String)
    description = Column(String)
    department = Column(String)
    prepared_by = Column(String)
    created_date = Column(Date)
    status = Column(String)
    rejection_comments = Column(String, nullable=True)

Base.metadata.create_all(engine)
print("Tables created successfully!")