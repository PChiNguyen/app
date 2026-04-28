from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from core.config import settings 
from sqlalchemy import event
from sqlalchemy.engine import Engine

# This forces SQLite to actually check Foreign Keys!
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()



engine= create_engine(settings.SQLALCHEMY_DATABASE_URL,echo= False) #dev only 

Sessionlocal= sessionmaker(bind= engine,autoflush=False,autocommit= False)

def get_db():
    db= Sessionlocal()
    try:
        yield db
    finally:
        db.close()

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
 
    