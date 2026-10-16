"""
استخراج پارامترها از متن محاوره‌ای فارسی
AI-Powered Parameter Extractor

این ماژول می‌تواند از LLM (مثل OpenAI) استفاده کند
یا با روش Rule-Based ساده کار کند
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ExtractedParams:
    """پارامترهای استخراج‌شده از متن"""
    work_type: Optional[str] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    location: Optional[str] = None
    is_wet_area: bool = False
    bed_thickness_cm: Optional[float] = None
    tile_size_cm: Optional[tuple] = None
    surface_type: Optional[str] = None
    volume_m3: Optional[float] = None
    element_type: Optional[str] = None
    rebar_density: Optional[str] = None
    concrete_grade: Optional[str] = None
    confidence: float = 0.0
    raw_text: str = ""


class RuleBasedExtractor:
    """استخراج‌کننده مبتنی بر قوانین (بدون نیاز به AI)"""

    # نگاشت کلمات کلیدی
    WORK_TYPE_KEYWORDS = {
        "tiling": ["کاشی", "سرامیک", "کاشیکاری", "سرامیک‌کاری", "کف", "دیوار"],
        "plastering": ["گچ", "گچ‌کاری", "گچکاری", "نازک‌کاری", "گچبری"],
        "rebar": ["آرماتور", "میلگرد", "اسکلت", "آهن", "فولاد"],
        "concrete": ["بتن", "بتن‌ریزی", "بتنریزی", "فونداسیون", "سقف"],
    }

    LOCATION_KEYWORDS = {
        "wall": ["دیوار", "wall"],
        "floor": ["کف", "سرویس", "آشپزخانه", "salon", "اتاق"],
    }

    WET_AREA_KEYWORDS = ["حمام", "دستشویی", "استخر", "سرویس بهداشتی", "توالت", "bathroom"]

    SURFACE_KEYWORDS = {
        "interior_wall": ["دیوار داخلی", "اتاق", "داخل"],
        "exterior_wall": ["دیوار خارجی", "نما"],
        "ceiling": ["سقف", "کف اتاق"],
    }

    ELEMENT_KEYWORDS = {
        "slab": ["سقف", "دال"],
        "foundation": ["فونداسیون", "پی"],
        "column": ["ستون"],
        "beam": ["تیر"],
    }

    @classmethod
    def extract(cls, text: str) -> ExtractedParams:
        """استخراج پارامترها از متن فارسی"""
        params = ExtractedParams(raw_text=text)

        # ۱. تشخیص نوع کار
        params.work_type = cls._detect_work_type(text)

        # ۲. استخراج مساحت/حجم
        params.area, params.area_unit = cls._extract_quantity(text)
        params.volume_m3 = cls._extract_volume(text)

        # ۳. تشخیص موقعیت
        params.location = cls._detect_location(text)
        params.is_wet_area = cls._detect_wet_area(text)

        # ۴. استخراج ضخامت بستر
        params.bed_thickness_cm = cls._extract_thickness(text)

        # ۵. استخراج سایز کاشی
        params.tile_size_cm = cls._extract_tile_size(text)

        # ۶. تشخیص نوع سطح
        params.surface_type = cls._detect_surface_type(text)

        # ۷. تشخیص نوع المان
        params.element_type = cls._detect_element_type(text)

        # ۸. محاسبه confidence
        params.confidence = cls._calculate_confidence(params)

        return params

    @classmethod
    def _detect_work_type(cls, text: str) -> Optional[str]:
        """تشخیص نوع کار"""
        text_lower = text.lower()
        scores = {}

        for work_type, keywords in cls.WORK_TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[work_type] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    @classmethod
    def _extract_quantity(cls, text: str) -> tuple:
        """استخراج مساحت/مقدار از متن"""
        # الگوهای رایج فارسی
        patterns = [
            # "۱۰۰ متر"، "۱۲۰ متر مربع"، "۱۰۰ m2"
            r"(\d+(?:\.\d+)?)\s*(?:متر مرع|مترمربع|متر|m2|m²|m\^2)",
            # "۱۰۰۰ کیلو"، "۲ تن"
            r"(\d+(?:\.\d+)?)\s*(?:کیلوگرم|کیلو|kg)",
            # "۵۰۰ عدد"
            r"(\d+(?:\.\d+)?)\s*(?:عدد|تعداد)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if "متر" in text[match.start():match.end()] or "m" in text[match.start():match.end()].lower():
                    return value, "m2"
                elif "کیلو" in text[match.start():match.end()]:
                    return value, "kg"
                return value, "unit"

        return None, None

    @classmethod
    def _extract_volume(cls, text: str) -> Optional[float]:
        """استخراج حجم از متن"""
        # "۱۰ متر مکعب"، "۵ m3"
        pattern = r"(\d+(?:\.\d+)?)\s*(?:متر مکعب|مترمکعب|m3|m³)"
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
        return None

    @classmethod
    def _detect_location(cls, text: str) -> Optional[str]:
        """تشخیص موقعیت (دیوار/کف)"""
        text_lower = text.lower()
        if any(kw in text_lower for kw in cls.LOCATION_KEYWORDS["floor"]):
            return "floor"
        elif any(kw in text_lower for kw in cls.LOCATION_KEYWORDS["wall"]):
            return "wall"
        return None

    @classmethod
    def _detect_wet_area(cls, text: str) -> bool:
        """تشخیص منطقه مرطوب"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in cls.WET_AREA_KEYWORDS)

    @classmethod
    def _extract_thickness(cls, text: str) -> Optional[float]:
        """استخراج ضخامت بستر"""
        # "ضخامت ۳ سانت"، "۳ سانتی‌متر"، "۳۰ میل"
        patterns = [
            r"ضخامت\s*(\d+(?:\.\d+)?)\s*(?:سانت|سانتی‌متر|cm)",
            r"(\d+(?:\.\d+)?)\s*(?:سانت|سانتی‌متر|cm)",
            r"(\d+(?:\.\d+)?)\s*(?:میل|میلی‌متر|mm)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if "میل" in text[match.start():match.end()]:
                    return value / 10.0  # تبدیل میل به سانت
                return value
        return None

    @classmethod
    def _extract_tile_size(cls, text: str) -> Optional[tuple]:
        """استخراج سایز کاشی"""
        # "۶۰ در ۶۰"، "۶۰×۶۰"، "60x60"
        patterns = [
            r"(\d+)\s*(?:در|×|x|X)\s*(\d+)\s*(?:سانت)?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                w, h = int(match.group(1)), int(match.group(2))
                # اگر میل بود تبدیل کن
                if w < 10:  # احتمالاً متر است
                    w *= 100
                    h *= 100
                return (w, h)
        return None

    @classmethod
    def _detect_surface_type(cls, text: str) -> Optional[str]:
        """تشخیص نوع سطح برای گچ‌کاری"""
        text_lower = text.lower()
        for surface_type, keywords in cls.SURFACE_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return surface_type
        return None

    @classmethod
    def _detect_element_type(cls, text: str) -> Optional[str]:
        """تشخیص نوع المان سازه‌ای"""
        text_lower = text.lower()
        for element_type, keywords in cls.ELEMENT_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return element_type
        return None

    @classmethod
    def _calculate_confidence(cls, params: ExtractedParams) -> float:
        """محاسبه میزان اطمینان از استخراج"""
        score = 0.0
        checks = [
            params.work_type is not None,
            params.area is not None or params.volume_m3 is not None,
            params.location is not None or params.surface_type is not None or params.element_type is not None,
        ]
        score = sum(checks) / len(checks)
        return round(score, 2)


class AIExtractor:
    """استخراج‌کننده مبتنی بر AI (برای آینده)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.rule_based = RuleBasedExtractor()

    def extract(self, text: str) -> ExtractedParams:
        """استخراج با AI یا Rule-Based"""
        if not self.api_key:
            # اگر API key نداریم، Rule-Based استفاده کن
            return self.rule_based.extract(text)

        # TODO: در آینده می‌توان از OpenAI API استفاده کرد
        # برای حالا Rule-Based کافی است
        return self.rule_based.extract(text)
