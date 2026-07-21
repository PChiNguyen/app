from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from core.config import settings 
from sqlalchemy import event
from sqlalchemy.engine import Engine

# 1. CẤU HÌNH ENGINE ĐÃ ĐƯỢC TỐI ƯU CHO PRODUCTION
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=False,          
    pool_recycle=1800,   # Tự động làm mới kết nối sau 30 phút
    pool_pre_ping=True    # Kiểm tra Neon còn sống không trước khi gửi câu lệnh
) 

Sessionlocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

# Các khối lệnh chạy thử nghiệm kiểm tra phản hồi Terminal
try:
    with engine.connect() as conn:
        print("--- SESSION: Kết nối DB ngon lành! ---")
except Exception as e:
    print(f"--- SESSION: URL CÓ VẤN ĐỀ RỒI KU: {e} ---")

try:
    db = Sessionlocal()
    print("Tạo Session thành công!")
except Exception as e:
    print(f"LỖI ĐÂY NÈ KU: {e}")
    