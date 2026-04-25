
from db.session import engine
# PHẢI CÓ DÒNG NÀY ĐỂ PYTHON "NẠP" LỖI VÀO BỘ NHỚ

from sqlalchemy import create_engine 
from db.base import Base 
import time 
from core.config import settings 
def test_connection():
    try: 
        engine= create_engine(settings.SQLALCHEMY_DATABASE_URL)
        print('Đang kết nối và tạo bảng........')
        Base.metadata.create_all(bind=engine)
        print('Thành công, các bảng đã được tạo!')
    except Exception as e:
        print(f'Thất bại!!. Lỗi rồi ku, lỗi;{e}')
if __name__== '__main__':
    test_connection() 
