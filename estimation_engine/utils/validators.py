"""
اعتبارسنجی ورودی‌ها
Input Validators
"""

from typing import Tuple, Optional


class InputValidator:
    """اعتبارسنج ورودی"""

    @classmethod
    def validate_area(cls, area: float) -> Tuple[bool, Optional[str]]:
        """اعتبارسنجی مساحت"""
        if area <= 0:
            return False, "مساحت باید بزرگ‌تر از صفر باشد"
        if area > 100000:
            return False, "مساحت بسیار بزرگ است. لطفاً بررسی کنید"
        return True, None

    @classmethod
    def validate_volume(cls, volume: float) -> Tuple[bool, Optional[str]]:
        """اعتبارسنجی حجم"""
        if volume <= 0:
            return False, "حجم باید بزرگ‌تر از صفر باشد"
        if volume > 10000:
            return False, "حجم بسیار بزرگ است. لطفاً بررسی کنید"
        return True, None

    @classmethod
    def validate_thickness(cls, thickness: float) -> Tuple[bool, Optional[str]]:
        """اعتبارسنجی ضخامت"""
        if thickness <= 0:
            return False, "ضخامت باید بزرگ‌تر از صفر باشد"
        if thickness > 50:
            return False, "ضخامت بسیار زیاد است. آیا واحد را درست وارد کرده‌اید؟"
        return True, None
