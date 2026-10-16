"""
موتور یادگیری از داده‌های واقعی کارگاه
Learning Engine - Adjusts coefficients based on actual usage

این ماژول در فاز ۲ فعال می‌شود وقتی داده‌های واقعی
از پلتفرم گزارش‌گیری دریافت می‌شود
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ActualUsage:
    """مصرف واقعی ثبت‌شده از کارگاه"""
    project_id: str
    work_type: str
    estimated_materials: Dict[str, float]  # نام مصالح -> مقدار برآوردشده
    actual_materials: Dict[str, float]     # نام مصالح -> مقدار واقعی مصرف‌شده
    date: datetime
    notes: str = ""


@dataclass
class AdjustmentFactor:
    """ضریب اصلاح برای یک مصالح خاص"""
    material_name: str
    work_type: str
    original_factor: float
    adjusted_factor: float
    confidence: float  # 0-1
    sample_count: int  # تعداد نمونه‌های یادگیری
    last_updated: datetime


class LearningEngine:
    """موتور یادگیری و بهود ضرایب"""

    def __init__(self):
        self.adjustments: Dict[str, AdjustmentFactor] = {}
        self.usage_history: List[ActualUsage] = []

    def record_actual_usage(self, usage: ActualUsage):
        """ثبت مصرف واقعی از کارگاه"""
        self.usage_history.append(usage)
        self._update_adjustments(usage)

    def _update_adjustments(self, usage: ActualUsage):
        """به‌روزرسانی ضرایب بر اساس داه جدید"""
        for material, estimated_qty in usage.estimated_materials.items():
            if material in usage.actual_materials:
                actual_qty = usage.actual_materials[material]

                if estimated_qty > 0:
                    # نسبت واقعی به برآورد
                    ratio = actual_qty / estimated_qty

                    key = f"{usage.work_type}:{material}"

                    if key in self.adjustments:
                        # میانگین متحرک
                        adj = self.adjustments[key]
                        n = adj.sample_count
                        new_factor = (adj.adjusted_factor * n + ratio) / (n + 1)
                        adj.adjusted_factor = round(new_factor, 3)
                        adj.sample_count = n + 1
                        adj.last_updated = datetime.now()
                        # confidence با تعداد نمونه بیشتر می‌شود
                        adj.confidence = min(0.95, 0.5 + (n * 0.05))
                    else:
                        self.adjustments[key] = AdjustmentFactor(
                            material_name=material,
                            work_type=usage.work_type,
                            original_factor=1.0,
                            adjusted_factor=round(ratio, 3),
                            confidence=0.5,
                            sample_count=1,
                            last_updated=datetime.now(),
                        )

    def get_adjustment(
        self,
        work_type: str,
        material_name: str,
    ) -> Optional[AdjustmentFactor]:
        """دریافت ضریب اصلاح برای یک مصالح"""
        key = f"{work_type}:{material_name}"
        return self.adjustments.get(key)

    def apply_adjustment(
        self,
        work_type: str,
        material_name: str,
        base_quantity: float,
    ) -> float:
        """اعمال ضریب اصلاح به مقدار پایه"""
        adjustment = self.get_adjustment(work_type, material_name)
        if adjustment and adjustment.confidence > 0.6:
            return base_quantity * adjustment.adjusted_factor
        return base_quantity

    def get_learning_summary(self) -> Dict:
        """خلاصه وضعیت یادگیری"""
        return {
            "total_records": len(self.usage_history),
            "adjusted_materials": len(self.adjustments),
            "high_confidence_adjustments": sum(
                1 for a in self.adjustments.values() if a.confidence > 0.8
            ),
            "adjustments": {
                key: {
                    "factor": adj.adjusted_factor,
                    "confidence": adj.confidence,
                    "samples": adj.sample_count,
                }
                for key, adj in self.adjustments.items()
            },
        }
