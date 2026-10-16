"""
ضرایب استاندارد مصرف مصالح برای عملیات ساختمانی
Standard Material Consumption Coefficients

منبع: مبانی برآورد و کنترل پروژه - استانداردهای ایران
"""

from typing import Dict, Any


# ============================================
# ضرایب کاشی‌کاری (Tiling)
# ============================================
TILING_COEFFICIENTS = {
    "wall_standard": {
        "cement_kg_per_m2": 7.0,        # سیمان (کیلوگرم بر متر مربع)
        "sand_m3_per_m2": 0.025,        # ماسه (متر مکعب بر متر مربع)
        "water_l_per_m2": 6.0,          # آب (لیتر بر متر مربع)
        "tile_adhesive_kg_per_m2": 4.0, # چسب کاشی (اختیاری)
        "waste_factor": 1.08,            # ضریب ضایعات
    },
    "wall_wet_area": {
        "cement_kg_per_m2": 9.0,
        "sand_m3_per_m2": 0.030,
        "water_l_per_m2": 7.0,
        "tile_adhesive_kg_per_m2": 5.0,
        "waterproof_additive_l_per_m2": 0.5,
        "waste_factor": 1.10,
    },
    "floor_standard": {
        "cement_kg_per_m2": 8.0,
        "sand_m3_per_m2": 0.035,
        "water_l_per_m2": 7.0,
        "tile_adhesive_kg_per_m2": 4.5,
        "waste_factor": 1.08,
    },
    "floor_thick_bed": {  # بستر ضخیم (بیش از ۵ سانت)
        "cement_kg_per_m2": 12.0,
        "sand_m3_per_m2": 0.050,
        "water_l_per_m2": 10.0,
        "tile_adhesive_kg_per_m2": 3.0,
        "waste_factor": 1.10,
    },
}


# ============================================
# ضرایب گچ‌کاری (Plastering)
# ============================================
PLASTERING_COEFFICIENTS = {
    "wall_interior": {
        "gypsum_kg_per_m2": 8.0,
        "water_l_per_m2": 5.0,
        "mesh_m_per_m2": 0.15,
        "waste_factor": 1.05,
    },
    "wall_exterior": {
        "cement_kg_per_m2": 10.0,
        "sand_m3_per_m2": 0.025,
        "water_l_per_m2": 6.0,
        "waste_factor": 1.08,
    },
    "ceiling": {
        "gypsum_kg_per_m2": 9.0,
        "water_l_per_m2": 5.5,
        "waste_factor": 1.07,
    },
}


# ============================================
# ضرایب آرماتوربندی (Rebar)
# ============================================
REBAR_COEFFICIENTS = {
    "slab_light": {
        "rebar_kg_per_m2": 8.0,
        "wire_kg_per_m2": 0.2,
        "spacer_per_m2": 2.0,
        "waste_factor": 1.05,
    },
    "slab_medium": {
        "rebar_kg_per_m2": 12.0,
        "wire_kg_per_m2": 0.3,
        "spacer_per_m2": 2.5,
        "waste_factor": 1.05,
    },
    "beam": {
        "rebar_kg_per_m3": 120.0,
        "wire_kg_per_m3": 3.0,
        "waste_factor": 1.06,
    },
    "column": {
        "rebar_kg_per_m3": 150.0,
        "wire_kg_per_m3": 4.0,
        "waste_factor": 1.06,
    },
}


# ============================================
# ضرایب بتن‌ریزی (Concrete)
# ============================================
CONCRETE_COEFFICIENTS = {
    "slab": {
        "cement_kg_per_m3": 350.0,
        "sand_m3_per_m3": 0.45,
        "gravel_m3_per_m3": 0.75,
        "water_l_per_m3": 180.0,
        "waste_factor": 1.05,
    },
    "foundation": {
        "cement_kg_per_m3": 300.0,
        "sand_m3_per_m3": 0.50,
        "gravel_m3_per_m3": 0.80,
        "water_l_per_m3": 170.0,
        "waste_factor": 1.05,
    },
    "column": {
        "cement_kg_per_m3": 380.0,
        "sand_m3_per_m3": 0.42,
        "gravel_m3_per_m3": 0.72,
        "water_l_per_m3": 190.0,
        "waste_factor": 1.06,
    },
}


# ============================================
# نگاشت نو کار به ضرایب
# ============================================
WORK_TYPE_COEFFICIENTS: Dict[str, Dict[str, Any]] = {
    "tiling": TILING_COEFFICIENTS,
    "plastering": PLASTERING_COEFFICIENTS,
    "rebar": REBAR_COEFFICIENTS,
    "concrete": CONCRETE_COEFFICIENTS,
}


# ============================================
# تنظیمات حمل و نقل
# ============================================
TRANSPORT_CONFIG = {
    "vehicles": {
        "pickup": {
            "name_fa": "وانت",
            "max_weight_kg": 1000,
            "max_volume_m3": 3.0,
            "cost_per_trip_base": 500000,  # تومان
        },
        "small_truck": {
            "name_fa": "خاور کوچک (نیسان‌بار)",
            "max_weight_kg": 2500,
            "max_volume_m3": 8.0,
            "cost_per_trip_base": 800000,
        },
        "medium_truck": {
            "name_fa": "کامیون ۶ تن",
            "max_weight_kg": 6000,
            "max_volume_m3": 18.0,
            "cost_per_trip_base": 1500000,
        },
        "heavy_truck_10t": {
            "name_fa": "کامیون ۱۰ تن",
            "max_weight_kg": 10000,
            "max_volume_m3": 25.0,
            "cost_per_trip_base": 2200000,
        },
        "heavy_truck_20t": {
            "name_fa": "کامیون ۲۰ تن",
            "max_weight_kg": 20000,
            "max_volume_m3": 40.0,
            "cost_per_trip_base": 3500000,
        },
    },
    "material_density": {
        "sand": 1600,       # kg/m³
        "cement": 1400,     # kg/m³ (کیسه)
        "gravel": 1700,     # kg/m³
        "gypsum": 900,      # kg/m³
        "rebar": 7850,      # kg/m³
    },
}


# ============================================
# وزن هر کیسه سیمان
# ============================================
CEMENT_BAG_WEIGHT_KG = 50


# ============================================
# نام‌های فارسی مصالح
# ============================================
MATERIAL_NAMES_FA = {
    "cement": "سیمان",
    "sand": "ماسه",
    "gravel": "شن",
    "water": "آب",
    "gypsum": "گچ",
    "rebar": "آرماتور",
    "wire": "سیم‌بست",
    "spacer": "اسپیسر",
    "tile_adhesive": "چسب کاشی",
    "waterproof_additive": "افزودنی ضد آب",
    "mesh": "تور مرغی",
}
