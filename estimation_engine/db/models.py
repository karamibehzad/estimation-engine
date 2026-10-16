"""
مدل‌های دیتابیس
Database Models for Estimation Engine
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Text, JSON, Boolean, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class EstimationRecord(Base):
    """رکورد برآورد ذخیره‌شده"""
    __tablename__ = "estimations"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=True, index=True)
    work_type = Column(String(50), nullable=False)
    work_type_fa = Column(String(100), nullable=False)
    area = Column(Float, nullable=True)
    area_unit = Column(String(20), nullable=True)

    # مصاح به صورت JSON
    materials_json = Column(Text, nullable=False, default="[]")

    # پلن حمل و نقل
    transport_plan_json = Column(Text, nullable=True)

    # نتیجه
    confidence = Column(Float, default=0.0)
    warnings_json = Column(Text, nullable=True, default="[]")
    notes_json = Column(Text, nullable=True, default="[]")

    # متادیتا
    raw_input = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def set_materials(self, materials_list):
        """تبدیل لیست مصالح به JSON"""
        self.materials_json = json.dumps([
            {
                "name_en": m.name_en,
                "name_fa": m.name_fa,
                "quantity": m.quantity,
                "unit": m.unit,
                "unit_fa": m.unit_fa,
                "notes": m.notes,
            }
            for m in materials_list
        ], ensure_ascii=False)

    def get_materials(self):
        """دریافت لیست مصالح از JSON"""
        if not self.materials_json:
            return []
        return json.loads(self.materials_json)

    def set_transport_plan(self, plan):
        """تبدیل پلن حمل به JSON"""
        if plan:
            self.transport_plan_json = json.dumps({
                "material_name_fa": plan.material_name_fa,
                "total_quantity": plan.total_quantity,
                "unit_fa": plan.unit_fa,
                "estimated_weight_kg": plan.estimated_weight_kg,
                "recommended": {
                    "vehicle_name_fa": plan.recommended_option.vehicle_name_fa,
                    "trip_count": plan.recommended_option.trip_count,
                    "notes": plan.recommended_option.notes,
                }
            }, ensure_ascii=False)

    def set_warnings(self, warnings_list):
        self.warnings_json = json.dumps(warnings_list, ensure_ascii=False)

    def set_notes(self, notes_list):
        self.notes_json = json.dumps(notes_list, ensure_ascii=False)


class ActualUsageRecord(Base):
    """مصرف واقعی ثبت‌شده از کارگاه (برای فاز ۲)"""
    __tablename__ = "actual_usages"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(100), nullable=False, index=True)
    estimation_id = Column(Integer, ForeignKey("estimations.id"), nullable=True)
    work_type = Column(String(50), nullable=False)

    # مصالح برآوردشده و واقعی
    estimated_materials_json = Column(Text, nullable=False)
    actual_materials_json = Column(Text, nullable=False)

    # تفاوت
    variance_json = Column(Text, nullable=True)

    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, default=datetime.now)


class AdjustmentFactorRecord(Base):
    """ضرایب اصلاح‌شده (برای فاز ۲)"""
    __tablename__ = "adjustment_factors"

    id = Column(Integer, primary_key=True, index=True)
    work_type = Column(String(50), nullable=False)
    material_name = Column(String(50), nullable=False)
    original_factor = Column(Float, default=1.0)
    adjusted_factor = Column(Float, default=1.0)
    confidence = Column(Float, default=0.0)
    sample_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.now)

    __table_args__ = (
        # کلید یکتا برای work_type + material_name
        # SQLAlchemy unique constraint
    )
