"""
موتور بهینه‌سازی مصرف مصالح
Optimization Engine for Material Usage

این ماژول در آینده می‌تواند با یادگیری از داده‌های واقعی
ضرایب را بهینه کند
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class OptimizationSuggestion:
    """یک پیشنهاد بهینه‌سازی"""
    type: str  # "cost", "time", "quality", "waste"
    message_fa: str
    impact: str  # "high", "medium", "low"
    potential_savings: Optional[float] = None  # درصد صرفه‌جویی


class MaterialOptimizer:
    """بهینه‌ساز مصرف مصالح"""

    @classmethod
    def optimize_tiling(
        cls,
        area_m2: float,
        tile_size_cm: Optional[tuple] = None,
        bed_thickness_cm: float = 3.0,
    ) -> List[OptimizationSuggestion]:
        """پیشنهاد بهینه‌سازی برای کاشی‌کاری"""
        suggestions = []

        # بررسی ضخامت بستر
        if bed_thickness_cm > 5:
            suggestions.append(OptimizationSuggestion(
                type="cost",
                message_fa="ضخامت بستر بالا است. اگر امکان استفاده از چسب کاشی به جای ملات وجود دارد، مصرف ماسه و سیمان به طور قابل توجهی کاهش می‌یابد.",
                impact="high",
                potential_savings=30.0,
            ))

        # بررسی سایز کاشی
        if tile_size_cm:
            tile_area = (tile_size_cm[0] / 100) * (tile_size_cm[1] / 100)
            if tile_area > 0.36:  # کاشی بزرگ (۶۰×۶۰ و بزرگ‌تر)
                suggestions.append(OptimizationSuggestion(
                    type="quality",
                    message_fa="کاشی‌های بزرگ نیاز به چسب کاشی دارند. استفاده از ملات سنتی ممکن است باعث کاهش کیفیت شود.",
                    impact="high",
                ))

        # پیشنهاد کاهش ضایعات
        suggestions.append(OptimizationSuggestion(
            type="waste",
            message_fa="برای کاهش ضایعات، کاشی‌ها را قبل از شروع کار برش‌دهی کنید و از نقشه اجرایی استفاده نمایید.",
            impact="medium",
            potential_savings=5.0,
        ))

        return suggestions

    @classmethod
    def optimize_concrete(
        cls,
        volume_m3: float,
        concrete_grade: str = "C25",
    ) -> List[OptimizationSuggestion]:
        """پیشنهاد بهینه‌سازی برای بتن‌ریزی"""
        suggestions = []

        # بررسی حجم
        if volume_m3 > 50:
            suggestions.append(OptimizationSuggestion(
                type="cost",
                message_fa="حجم بتن بالا است. پیشنهاد می‌شود از بچینگ پلانت استفاده کنید. هزینه هر متر مکعب بتن آماده معمولاً کمتر از بتن دستی است.",
                impact="high",
                potential_savings=15.0,
            ))
        elif volume_m3 < 5:
            suggestions.append(OptimizationSuggestion(
                type="cost",
                message_fa="حجم بتن کم است. بتن آماده برای حجم‌های کم مقرون‌به‌صرفه نیست. بتن دستی توصیه می‌شود.",
                impact="medium",
            ))

        # بررسی رجه بتن
        if concrete_grade in ["C30", "C35", "C40"]:
            suggestions.append(OptimizationSuggestion(
                type="quality",
                message_fa="درجه بتن بالا نیاز به کنترل کیفیت دقیق دارد. حتماً از مهندسی ناظر مشورت بگیرید.",
                impact="medium",
            ))

        return suggestions

    @classmethod
    def optimize_transport(
        cls,
        total_weight_kg: float,
        material_name_fa: str,
    ) -> List[OptimizationSuggestion]:
        """پیشنهاد بهینه‌سازی حمل و نقل"""
        suggestions = []

        # بررسی وزن
        if total_weight_kg > 20000:
            suggestions.append(OptimizationSuggestion(
                type="cost",
                message_fa=f"وزن {material_name_fa} بسیار بالا است. پیشنهاد می‌شود سفارش را به چند مرحله تقسیم کنید تا از کف‌ریزی جلوگیری شود.",
                impact="high",
                potential_savings=10.0,
            ))

        # بررسی حمل ترکیبی
        if 1000 < total_weight_kg < 3000:
            suggestions.append(OptimizationSuggestion(
                type="cost",
                message_fa=f"برای {total_weight_kg/1000:.1f} تن {material_name_fa}، یک خاور کوچک (۲.۵ تن) کافی است. نیازی به کامیون نیست.",
                impact="medium",
                potential_savings=20.0,
            ))

        return suggestions


class CostEstimator:
    """تخمین‌زن هزینه"""

    # قیمت‌های تقریبی (تومان) - باید به‌روز شوند
    MATERIAL_PRICES = {
        "cement": 450000,        # هر کیسه ۵۰ کیلویی
        "sand": 800000,          # هر متر مکعب
        "gravel": 700000,        # هر متر مکعب
        "water": 0,             # آب معمولاً رایگان
        "gypsum": 350000,        # هر کیسه ۳۰ کیلویی
        "rebar": 45000,          # هر کیلوگرم
        "wire": 50000,           # هر کیلوگرم
        "tile_adhesive": 250000, # هر کیسه ۲۵ کیلویی
    }

    @classmethod
    def estimate_material_cost(
        cls,
        material_name_en: str,
        quantity: float,
        unit: str,
    ) -> float:
        """تخمین هزینه یک مصالح"""
        unit_price = cls.MATERIAL_PRICES.get(material_name_en, 0)

        # تبدیل واحد
        if unit == "bags":
            return quantity * unit_price
        elif unit == "m³":
            return quantity * unit_price
        elif unit == "kg":
            # تبدیل به کیلوگرم
            if material_name_en in ["rebar", "wire"]:
                return quantity * unit_price

        return 0.0
