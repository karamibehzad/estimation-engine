"""
موتور محاسبه مصالح
Material Estimation Calculator Engine
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .constants import (
    WORK_TYPE_COEFFICIENTS,
    CEMENT_BAG_WEIGHT_KG,
    MATERIAL_NAMES_FA,
)


@dataclass
class MaterialItem:
    """یک آیتم مصالح"""
    name_en: str
    name_fa: str
    quantity: float
    unit: str
    unit_fa: str
    notes: str = ""


@dataclass
class EstimationResult:
    """نتیجه برآورد"""
    work_type: str
    work_type_fa: str
    area: float
    area_unit: str
    materials: List[MaterialItem] = field(default_factory=list)
    transport_plan: Optional[Any] = None
    confidence: float = 0.0
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class TilingCalculator:
    """محاسبه‌گر کاشی‌کاری"""

    WORK_TYPE_FA = "کاشی‌کاری"

    @classmethod
    def calculate(
        cls,
        area_m2: float,
        location: str = "wall",
        is_wet_area: bool = False,
        bed_thickness_cm: float = 3.0,
        tile_size_cm: Optional[tuple] = None,
    ) -> EstimationResult:
        """
        محاسبه مصالح کاشی‌کاری

        Args:
            area_m2: مساحت به متر مربع
            location: "wall" یا "floor"
            is_wet_area: آیا منطقه مرطوب است (حمام، استخر)
            bed_thickness_cm: ضخامت بستر به سانتی‌متر
            tile_size_cm: سایز کاشی (طول، عرض) به سانتی‌متر
        """
        result = EstimationResult(
            work_type="tiling",
            work_type_fa=cls.WORK_TYPE_FA,
            area=area_m2,
            area_unit="m²",
            confidence=0.85,
        )

        # انتخاب ضرایب مناسب
        if location == "wall":
            if is_wet_area:
                coeffs = WORK_TYPE_COEFFICIENTS["tiling"]["wall_wet_area"]
                result.notes.append("منطقه مرطوب: افزودنی ضد آب لحاظ شده است")
            else:
                coeffs = WORK_TYPE_COEFFICIENTS["tiling"]["wall_standard"]
        else:  # floor
            if bed_thickness_cm > 5:
                coeffs = WORK_TYPE_COEFFICIENTS["tiling"]["floor_thick_bed"]
                result.notes.append(f"بستر ضخیم ({bed_thickness_cm} سانت): ضرایب افزایش یافته")
            else:
                coeffs = WORK_TYPE_COEFFICIENTS["tiling"]["floor_standard"]

        waste_factor = coeffs["waste_factor"]

        # سیمان
        cement_kg = area_m2 * coeffs["cement_kg_per_m2"] * waste_factor
        cement_bags = int(cement_kg / CEMENT_BAG_WEIGHT_KG) + (1 if cement_kg % CEMENT_BAG_WEIGHT_KG > 0 else 0)
        result.materials.append(MaterialItem(
            name_en="cement",
            name_fa=MATERIAL_NAMES_FA["cement"],
            quantity=cement_bags,
            unit="bags",
            unit_fa=f"کیسه {CEMENT_BAG_WEIGHT_KG} کیلویی",
            notes=f"≈ {cement_kg:.1f} کیلوگرم"
        ))

        # ماسه
        sand_m3 = area_m2 * coeffs["sand_m3_per_m2"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="sand",
            name_fa=MATERIAL_NAMES_FA["sand"],
            quantity=round(sand_m3, 2),
            unit="m³",
            unit_fa="متر مکعب",
        ))

        # آب
        water_l = area_m2 * coeffs["water_l_per_m2"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="water",
            name_fa=MATERIAL_NAMES_FA["water"],
            quantity=round(water_l, 0),
            unit="L",
            unit_fa="لیتر",
        ))

        # چسب کاشی (اختیاری)
        if "tile_adhesive_kg_per_m2" in coeffs:
            adhesive_kg = area_m2 * coeffs["tile_adhesive_kg_per_m2"] * waste_factor
            result.materials.append(MaterialItem(
                name_en="tile_adhesive",
                name_fa=MATERIAL_NAMES_FA["tile_adhesive"],
                quantity=round(adhesive_kg, 1),
                unit="kg",
                unit_fa="کیلوگرم",
                notes="اختیاری - پیشنهاد می‌شود برای کیفیت بهتر"
            ))

        # افزودنی ضد آب
        if "waterproof_additive_l_per_m2" in coeffs:
            additive_l = area_m2 * coeffs["waterproof_additive_l_per_m2"] * waste_factor
            result.materials.append(MaterialItem(
                name_en="waterproof_additive",
                name_fa=MATERIAL_NAMES_FA["waterproof_additive"],
                quantity=round(additive_l, 1),
                unit="L",
                unit_fa="لیتر",
            ))

        # تعداد کاشی (اگر سایز داده شده)
        if tile_size_cm:
            tile_area_m2 = (tile_size_cm[0] / 100) * (tile_size_cm[1] / 100)
            tile_count = int(area_m2 / tile_area_m2 * waste_factor) + 1
            result.materials.append(MaterialItem(
                name_en="tiles",
                name_fa="کاشی",
                quantity=tile_count,
                unit="pieces",
                unit_fa="عدد",
                notes=f"سایز {tile_size_cm[0]}×{tile_size_cm[1]} سانت"
            ))

        return result


class PlasteringCalculator:
    """محاسبه‌گر گچ‌کاری"""

    WORK_TYPE_FA = "گچ‌کاری"

    @classmethod
    def calculate(
        cls,
        area_m2: float,
        surface_type: str = "interior_wall",  # interior_wall, exterior_wall, ceiling
        thickness_mm: float = 15.0,
    ) -> EstimationResult:
        """محاسبه مصالح گچ‌کاری"""

        result = EstimationResult(
            work_type="plastering",
            work_type_fa=cls.WORK_TYPE_FA,
            area=area_m2,
            area_unit="m²",
            confidence=0.80,
        )

        # انتخاب ضرایب
        if surface_type == "interior_wall":
            coeffs = WORK_TYPE_COEFFICIENTS["plastering"]["wall_interior"]
        elif surface_type == "exterior_wall":
            coeffs = WORK_TYPE_COEFFICIENTS["plastering"]["wall_exterior"]
        else:  # ceiling
            coeffs = WORK_TYPE_COEFFICIENTS["plastering"]["ceiling"]

        waste_factor = coeffs["waste_factor"]

        # ضخامت بر ضریب تأثیر می‌گذارد
        thickness_factor = thickness_mm / 15.0  # استاندارد ۱۵ میل

        if surface_type == "exterior_wall":
            # سیمان و ماسه
            cement_kg = area_m2 * coeffs["cement_kg_per_m2"] * waste_factor * thickness_factor
            cement_bags = int(cement_kg / CEMENT_BAG_WEIGHT_KG) + 1
            result.materials.append(MaterialItem(
                name_en="cement",
                name_fa=MATERIAL_NAMES_FA["cement"],
                quantity=cement_bags,
                unit="bags",
                unit_fa=f"کیسه {CEMENT_BAG_WEIGHT_KG} کیلویی",
                notes=f"≈ {cement_kg:.1f} کیلوگرم"
            ))

            sand_m3 = area_m2 * coeffs["sand_m3_per_m2"] * waste_factor * thickness_factor
            result.materials.append(MaterialItem(
                name_en="sand",
                name_fa=MATERIAL_NAMES_FA["sand"],
                quantity=round(sand_m3, 2),
                unit="m³",
                unit_fa="متر مکعب",
            ))
        else:
            # گچ
            gypsum_kg = area_m2 * coeffs["gypsum_kg_per_m2"] * waste_factor * thickness_factor
            result.materials.append(MaterialItem(
                name_en="gypsum",
                name_fa=MATERIAL_NAMES_FA["gypsum"],
                quantity=round(gypsum_kg, 1),
                unit="kg",
                unit_fa="کیلوگرم",
            ))

        # آب
        water_l = area_m2 * coeffs["water_l_per_m2"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="water",
            name_fa=MATERIAL_NAMES_FA["water"],
            quantity=round(water_l, 0),
            unit="L",
            unit_fa="لیتر",
        ))

        return result


class RebarCalculator:
    """محاسبه‌گر آرماتوربندی"""

    WORK_TYPE_FA = "آرماتوربندی"

    @classmethod
    def calculate(
        cls,
        quantity: float,
        quantity_unit: str = "m2",  # m2 یا m3
        element_type: str = "slab",  # slab, beam, column
        rebar_density: str = "medium",  # light, medium, heavy
    ) -> EstimationResult:
        """محاسبه مصالح آرماتوربندی"""

        result = EstimationResult(
            work_type="rebar",
            work_type_fa=cls.WORK_TYPE_FA,
            area=quantity,
            area_unit=quantity_unit,
            confidence=0.75,
        )

        # انتخاب ضرایب
        if element_type == "slab":
            if rebar_density == "light":
                coeffs = WORK_TYPE_COEFFICIENTS["rebar"]["slab_light"]
            else:
                coeffs = WORK_TYPE_COEFFICIENTS["rebar"]["slab_medium"]
            rebar_kg = quantity * coeffs["rebar_kg_per_m2"]
            wire_kg = quantity * coeffs["wire_kg_per_m2"]
            spacer_count = int(quantity * coeffs["spacer_per_m2"])
        else:
            key = "beam" if element_type == "beam" else "column"
            coeffs = WORK_TYPE_COEFFICIENTS["rebar"][key]
            rebar_kg = quantity * coeffs["rebar_kg_per_m3"]
            wire_kg = quantity * coeffs["wire_kg_per_m3"]
            spacer_count = int(quantity * 10)  # تخمینی

        waste_factor = coeffs["waste_factor"]

        # آرماتور
        result.materials.append(MaterialItem(
            name_en="rebar",
            name_fa=MATERIAL_NAMES_FA["rebar"],
            quantity=round(rebar_kg * waste_factor, 1),
            unit="kg",
            unit_fa="کیلوگرم",
            notes=f"≈ {(rebar_kg * waste_factor / 1000):.2f} تن"
        ))

        # سیم بست
        result.materials.append(MaterialItem(
            name_en="wire",
            name_fa=MATERIAL_NAMES_FA["wire"],
            quantity=round(wire_kg * waste_factor, 1),
            unit="kg",
            unit_fa="کیلوگرم",
        ))

        # اسپیسر
        result.materials.append(MaterialItem(
            name_en="spacer",
            name_fa=MATERIAL_NAMES_FA["spacer"],
            quantity=spacer_count,
            unit="pieces",
            unit_fa="عدد",
        ))

        return result


class ConcreteCalculator:
    """محاسبه‌گر بتن‌ریزی"""

    WORK_TYPE_FA = "بتن‌ریزی"

    @classmethod
    def calculate(
        cls,
        volume_m3: float,
        element_type: str = "slab",  # slab, foundation, column
        concrete_grade: str = "C25",
    ) -> EstimationResult:
        """محاسبه مصالح بتن‌ریزی"""

        result = EstimationResult(
            work_type="concrete",
            work_type_fa=cls.WORK_TYPE_FA,
            area=volume_m3,
            area_unit="m³",
            confidence=0.82,
        )

        # انتخاب ضرایب
        coeffs = WORK_TYPE_COEFFICIENTS["concrete"].get(
            element_type, 
            WORK_TYPE_COEFFICIENTS["concrete"]["slab"]
        )
        waste_factor = coeffs["waste_factor"]

        # سیمان
        cement_kg = volume_m3 * coeffs["cement_kg_per_m3"] * waste_factor
        cement_bags = int(cement_kg / CEMENT_BAG_WEIGHT_KG) + 1
        result.materials.append(MaterialItem(
            name_en="cement",
            name_fa=MATERIAL_NAMES_FA["cement"],
            quantity=cement_bags,
            unit="bags",
            unit_fa=f"کیسه {CEMENT_BAG_WEIGHT_KG} کیلویی",
            notes=f"≈ {cement_kg:.1f} کیلوگرم"
        ))

        # ماسه
        sand_m3 = volume_m3 * coeffs["sand_m3_per_m3"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="sand",
            name_fa=MATERIAL_NAMES_FA["sand"],
            quantity=round(sand_m3, 2),
            unit="m³",
            unit_fa="متر مکعب",
        ))

        # شن
        gravel_m3 = volume_m3 * coeffs["gravel_m3_per_m3"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="gravel",
            name_fa=MATERIAL_NAMES_FA["gravel"],
            quantity=round(gravel_m3, 2),
            unit="m³",
            unit_fa="متر مکعب",
        ))

        # آب
        water_l = volume_m3 * coeffs["water_l_per_m3"] * waste_factor
        result.materials.append(MaterialItem(
            name_en="water",
            name_fa=MATERIAL_NAMES_FA["water"],
            quantity=round(water_l, 0),
            unit="L",
            unit_fa="لیتر",
        ))

        result.notes.append(f"درجه بتن: {concrete_grade}")
        result.notes.append(f"حجم کل بتن با ضایعات: {volume_m3 * waste_factor:.2f} متر مکعب")

        return result


# ============================================
# Factory
# ============================================
CALCULATOR_REGISTRY = {
    "tiling": TilingCalculator,
    "plastering": PlasteringCalculator,
    "rebar": RebarCalculator,
    "concrete": ConcreteCalculator,
}


def get_calculator(work_type: str):
    """دریافت محاسبه‌گر مناسب بر اساس نوع کار"""
    calculator_class = CALCULATOR_REGISTRY.get(work_type.lower())
    if not calculator_class:
        raise ValueError(f"نوع کار نامعتبر: {work_type}. گزینه‌های مجاز: {list(CALCULATOR_REGISTRY.keys())}")
    return calculator_class
