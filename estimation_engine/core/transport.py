"""
موتور محاسبه حمل و نقل
Transport Calculation Engine
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from .constants import TRANSPORT_CONFIG, MATERIAL_NAMES_FA


@dataclass
class TransportOption:
    """یک گزینه حمل و نقل"""
    vehicle_key: str
    vehicle_name_fa: str
    trip_count: int
    total_cost: float
    efficiency_score: float  # 0-1, بالاتر بهتر
    notes: str = ""


@dataclass
class TransportPlan:
    """پلن حمل و نقل بهینه"""
    material_name_fa: str
    total_quantity: float
    unit_fa: str
    estimated_weight_kg: float
    recommended_option: TransportOption
    all_options: List[TransportOption] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TransportCalculator:
    """محاسبه‌گر حمل و نقل مصالح"""

    @classmethod
    def calculate(
        cls,
        material_name_en: str,
        quantity: float,
        unit: str,
        material_density_kg_m3: Optional[float] = None,
    ) -> TransportPlan:
        """
        محاسبه بهترین گزینه حمل و نقل

        Args:
            material_name_en: نام انگلیسی مصالح
            quantity: مقدار
            unit: واحد (m³, kg, bags)
            material_density_kg_m3: چگالی (برای تبدیل حجم به وزن)
        """
        # تخمین وزن
        estimated_weight_kg = cls._estimate_weight(
            material_name_en, quantity, unit, material_density_kg_m3
        )

        material_name_fa = MATERIAL_NAMES_FA.get(material_name_en, material_name_en)

        # ارزیابی همه گزینه‌ها
        all_options = []
        for vehicle_key, vehicle in TRANSPORT_CONFIG["vehicles"].items():
            option = cls._evaluate_vehicle(
                vehicle_key=vehicle_key,
                vehicle=vehicle,
                total_weight_kg=estimated_weight_kg,
                total_volume_m3=cls._estimate_volume(material_name_en, quantity, unit),
            )
            all_options.append(option)

        # فیلتر گزینه‌های غیرممکن
        valid_options = [o for o in all_options if o.trip_count > 0]

        # انتخاب بهترین گزینه (بالاترین efficiency_score)
        if valid_options:
            recommended = max(valid_options, key=lambda x: x.efficiency_score)
        else:
            # اگر هیچ گزینه‌ای مناسب نبود، کامیون ۲۰ تن
            recommended = all_options[-1]

        # هشدارها
        warnings = []
        if estimated_weight_kg > 20000:
            warnings.append("وزن بسیار بالا - نیاز به چند مرحله حمل")

        return TransportPlan(
            material_name_fa=material_name_fa,
            total_quantity=quantity,
            unit_fa=unit,
            estimated_weight_kg=estimated_weight_kg,
            recommended_option=recommended,
            all_options=sorted(valid_options, key=lambda x: x.efficiency_score, reverse=True),
            warnings=warnings,
        )

    @classmethod
    def _estimate_weight(
        cls,
        material_name_en: str,
        quantity: float,
        unit: str,
        density: Optional[float] = None,
    ) -> float:
        """تخمین وزن مصالح به کیلوگرم"""
        if unit == "kg":
            return quantity
        elif unit == "bags":
            # فرض: کیسه سیمان ۵۰ کیلوگرم
            return quantity * 50
        elif unit == "m³":
            if density:
                return quantity * density
            # استفاده از چگالی پیش‌فرض
            default_density = TRANSPORT_CONFIG["material_density"].get(material_name_en, 1500)
            return quantity * default_density
        elif unit == "L":
            # آب: ۱ لیتر ≈ ۱ کیلوگرم
            if material_name_en == "water":
                return quantity
            return quantity * 1.0  # تخمین برای سایر مواد
        return quantity

    @classmethod
    def _estimate_volume(
        cls,
        material_name_en: str,
        quantity: float,
        unit: str,
    ) -> float:
        """تخمین حجم مصالح به متر مکعب"""
        if unit == "m³":
            return quantity
        elif unit == "bags":
            # حجم تقریبی کیسه سیمان: ۰.۰۳۵ m³
            return quantity * 0.035
        elif unit == "kg":
            density = TRANSPORT_CONFIG["material_density"].get(material_name_en, 1500)
            return quantity / density
        elif unit == "L":
            return quantity / 1000
        return 0.0

    @classmethod
    def _evaluate_vehicle(
        cls,
        vehicle_key: str,
        vehicle: Dict,
        total_weight_kg: float,
        total_volume_m3: float,
    ) -> TransportOption:
        """ارزیابی یک نوع وسیله حمل"""
        max_weight = vehicle["max_weight_kg"]
        max_volume = vehicle["max_volume_m3"]

        # محاسبه تعداد سرویس بر اساس وزن
        trips_by_weight = int(total_weight_kg / max_weight) + (
            1 if total_weight_kg % max_weight > 0 else 0
        )

        # محاسبه تعداد سرویس بر اساس حجم
        trips_by_volume = int(total_volume_m3 / max_volume) + (
            1 if total_volume_m3 % max_volume > 0 else 0
        )

        # تعداد سرویس = حداکثر وزن یا حجم
        trip_count = max(trips_by_weight, trips_by_volume)

        # هزینه کل
        total_cost = trip_count * vehicle["cost_per_trip_base"]

        # محاسبه efficiency score
        # هرچه تعداد سرویس کمتر و ظرفیت بهتر استفاده شود، بهتر است
        if trip_count > 0:
            avg_load_weight = total_weight_kg / trip_count
            avg_load_volume = total_volume_m3 / trip_count

            weight_utilization = avg_load_weight / max_weight if max_weight > 0 else 0
            volume_utilization = avg_load_volume / max_volume if max_volume > 0 else 0

            # efficiency = میانگین استفاده از ظرفیت / تعداد سرویس
            utilization = max(weight_utilization, volume_utilization)
            efficiency = utilization / max(trip_count, 1)
        else:
            efficiency = 0.0

        # یادداشت
        notes = ""
        if trip_count == 1:
            notes = "حمل در یک مرحله"
        elif trip_count <= 3:
            notes = f"حمل در {trip_count} مرحله"
        else:
            notes = f"حمل در {trip_count} مرحله - پیشنهاد می‌شود با وسیله بزرگ‌تر حمل شود"

        return TransportOption(
            vehicle_key=vehicle_key,
            vehicle_name_fa=vehicle["name_fa"],
            trip_count=trip_count,
            total_cost=total_cost,
            efficiency_score=round(efficiency, 3),
            notes=notes,
        )


class TransportPlanner:
    """برنامه‌ریزی حمل و نقل برای کل پروژه"""

    @classmethod
    def plan_all_materials(
        cls,
        materials: List[Dict],
    ) -> List[TransportPlan]:
        """برنامه‌ریزی حمل برای لیست مصالح"""
        plans = []
        for mat in materials:
            plan = TransportCalculator.calculate(
                material_name_en=mat["name_en"],
                quantity=mat["quantity"],
                unit=mat["unit"],
                material_density_kg_m3=mat.get("density"),
            )
            plans.append(plan)
        return plans
