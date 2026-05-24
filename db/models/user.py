import uuid
import enum
import re   

from sqlalchemy import String, Enum as SQLEnum, CheckConstraint, UUID, ForeignKey, Integer
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from db.models.subject import Subject


from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from db.base import Base





# 1. Định nghĩa Enum (Menu chọn món)
class UserRole(enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class User(Base):
    __tablename__ = 'users'

    # --- CÁC CỘT DỮ LIỆU ---
    id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
# default= uuid.uuid4 only automatically when we have that db_session.commit 
    
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


   
    # Sử dụng SQLEnum để Postgres hiểu
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), 
        default=UserRole.STUDENT, 
        nullable=False
    )
    # Admin and Student will leave this blank (NULL). 
    # Teachers MUST have this filled out.
    subject_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('subjects.id', ondelete='SET NULL'), nullable=True)

    classrooms = relationship('Classroom', back_populates='teacher', cascade="save-update, merge")
    # We use Optional because Students and Admins will not have a subject
    subject: Mapped[Optional["Subject"]] = relationship('Subject', back_populates='teachers')




    __table_args__ = (
            # NOTE CHO TƯƠNG LAI: 
            # SQLite không hỗ trợ Regex (toán tử ~). 
            # Khi deploy lên hệ thống thật dùng PostgreSQL, hãy bỏ comment 2 dòng dưới đây.
            # CheckConstraint(r"username ~ '^[a-zA-Z0-9_]+$'", name='username_format_check'),
            # CheckConstraint(r"email ~* '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'", name='email_format_check'),
            
            # Check đơn giản để SQLite không nổ lỗi:
            CheckConstraint("length(username) >= 4", name='username_min_length'),
            CheckConstraint(
            "(role = 'teacher' AND subject_id IS NOT NULL) OR (role != 'teacher' AND subject_id IS NULL)",
            name="enforce_teacher_subject_rule"
        ),
    
        )
    @validates('username')
    def validate_username(self,key,input_value:str):
        # Trường hợp éo le 1: Username chỉ có số
        if not input_value.strip():
            raise ValueError("Tên người dùng không được để trống")
        if input_value.isdigit(): 
            raise ValueError("Tên người dùng không được chỉ chứa số")
        # TH2: Độ dài tối thiểu 
        if len(input_value.strip()) < 4:
            raise ValueError("Tên người dùng phải có ít nhất 4 ký tự")
        # Trường hợp éo le 3: Ký tự đặc biệt (chỉ cho phép chữ, số và dấu gạch dưới)
        if not re.match(r"^\w+$",input_value):
            raise ValueError("Tên người dùng chỉ được chứa chữ, số và dấu gạch dưới")
        return input_value
    @validates('role')
    def validate_role(self, key, input_value):
        # 1. Nếu nó đã là Enum chuẩn rồi, thì trả về luôn (Dành cho code backend/test)
        if isinstance(input_value, UserRole):
            return input_value
            
        # 2. Nếu nó là chuỗi, thì thử ép kiểu sang Enum (Dành cho API nhận JSON)
        if isinstance(input_value, str):
            try:
                return UserRole(input_value.lower())
            except ValueError:
                raise ValueError(f'Vai trò không hợp lệ: {input_value}. Phải là admin, teacher hoặc student')
                
        # 3. Nếu người dùng truyền vào số hoặc list, chặn lại ngay lập tức
        raise ValueError(f'Vai trò phải là UserRole hoặc chuỗi, không phải {type(input_value)}')
    @validates('email')
    def validate_email(self,key,input_value):
        print(f"DEBUG: Đang kiểm tra email: {input_value}")
        # Regex này sẽ chặn: .. , .@ , @. , dấu chấm ở đầu/cuối username
        email_regex = r"^(?!\.)(?!.*\.{2})[a-zA-Z0-9._%+-]+(?<!\.)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex,input_value):
            raise ValueError("Định dạng email không hợp lệ")
        
        if len(input_value) > 255:
            raise ValueError("Địa chỉ email không được vượt quá 255 ký tự")
        return input_value 
    
    @validates('subject_id')
    def validate_subject_id(self, key, input_value):
        if self.role == UserRole.TEACHER:
            if input_value is None:
                raise ValueError("Giáo viên phải có subject_id")
            if not isinstance(input_value, int):
                raise ValueError("subject_id phải là một số nguyên hợp lệ")
        else:
            if input_value is not None:
                raise ValueError("Chỉ giáo viên mới được phép có subject_id")
        return input_value
    
# ... các import khác


 

    

