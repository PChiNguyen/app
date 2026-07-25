import json
from uuid import UUID
from typing import Dict, Any, Optional
from redis import Redis

from repositories.grading_repo import GradingRepository

class GPACachingService:
    def __init__(self, grading_repo: GradingRepository, redis_client: Redis):
        self.repo = grading_repo
        self.redis = redis_client
        self.CACHE_TTL = 3600  # Dữ liệu cache tồn tại trong 1 giờ (3600s)

    def get_student_semester_gpa(
        self, 
        classroom_id: UUID, 
        student_id: UUID, 
        semester: int
    ) -> Optional[Dict[str, Any]]:
        # Tạo key phân biệt riêng cho từng học sinh và học kỳ
        cache_key = f"gpa:classroom:{classroom_id}:student:{student_id}:semester:{semester}"

        # 1. THỬ ĐỌC DỮ LIỆU TỪ REDIS
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                # ⚡ THÔNG BÁO CACHE HIT
                print(f"⚡ [REDIS CACHE HIT] Đã lấy điểm GPA cho Học sinh {student_id} trực tiếp từ RAM!")
                return json.loads(cached_data)
        except Exception as e:
            print(f"⚠️ [REDIS WARNING]: Không kết nối được Redis, chuyển sang truy vấn DB: {e}")

        # 2. CACHE MISS -> GỌI REPOSITORY ĐỂ TÍNH GPA TỪ POSTGRESQL
        print(f"🐢 [REDIS CACHE MISS] Đang tính toán GPA cho Học sinh {student_id} từ PostgreSQL...")
        result = self.repo.get_student_semester_gpa(classroom_id, student_id, semester)

        # Nếu không tìm thấy học sinh hoặc chưa có điểm
        if result is None:
            return None

        # 3. CHUYỂN ĐỔI DATACLASS THÀNH DICT ĐỂ CHUYỂN THÀNH JSON
        serialized_data = {
            "student_id": str(result.student_id),
            "student_name": result.student_name,
            "semester_gpa": float(result.semester_gpa) if result.semester_gpa is not None else None
        }

        # 4. LƯU KẾT QUẢ VÀO REDIS CHO LẦN TRUY CẬP SAU
        try:
            self.redis.setex(cache_key, self.CACHE_TTL, json.dumps(serialized_data))
        except Exception as e:
            print(f"⚠️ [REDIS WARNING]: Lỗi khi lưu vào Redis: {e}")

        return serialized_data