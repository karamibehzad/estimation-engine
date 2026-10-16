"""
فرمت‌کننده خروجی به فارسی
Output Formatters for Persian Display
"""

from typing import List
from estimation_engine.core import EstimationResult, MaterialItem, TransportPlan


class PersianFormatter:
    """فرمت‌کننده خروجی فارسی"""

    @classmethod
    def format_estimation(cls, result: EstimationResult) -> str:
        """فرمت کردن نتیجه برآورد به متن فارسی زیبا"""
        lines = []

        # هدر
        lines.append(f"🔧 **{result.work_type_fa}**")
        lines.append(f"📏 مساحت/حجم: {result.area} {result.area_unit}")
        lines.append("")

        # مصالح
        lines.append("📦 **مصالح پیشنهادی:**")
        for i, mat in enumerate(result.materials, 1):
            qty = cls._format_number(mat.quantity)
            line = f"  {i}. {mat.name_fa}: **{qty}** {mat.unit_fa}"
            if mat.notes:
                line += f" ({mat.notes})"
            lines.append(line)

        lines.append("")

        # پلن حمل
        if result.transport_plan:
            lines.append(cls._format_transport(result.transport_plan))

        # نکات
        if result.notes:
            lines.append("💡 **نکات:**")
            for note in result.notes:
                lines.append(f"  • {note}")

        # هشدارها
        if result.warnings:
            lines.append("⚠️ **هشدارها:**")
            for warning in result.warnings:
                lines.append(f"  • {warning}")

        # اطمینان
        lines.append("")
        lines.append(f"_میزان اطمینان: {int(result.confidence * 100)}%_")

        return "\n".join(lines)

    @classmethod
    def _format_transport(cls, plan: TransportPlan) -> str:
        """فرمت کردن پلن حمل و نقل"""
        lines = []
        lines.append("🚛 **حمل و نقل:**")

        qty = cls._format_number(plan.total_quantity)
        weight = cls._format_number(plan.estimated_weight_kg)
        lines.append(f"  {plan.material_name_fa}: {qty} {plan.unit_fa} (≈ {weight} کیلوگرم)")
        lines.append("")

        # گزینه پیشنهادی
        rec = plan.recommended_option
        lines.append(f"  ✅ **پیشنهاد:** {rec.vehicle_name_fa}")
        if rec.trip_count == 1:
            lines.append(f"  📍 حمل در **یک مرحله**")
        else:
            lines.append(f"  📍 حمل در **{rec.trip_count} مرحله**")
        if rec.notes:
            lines.append(f"  📝 {rec.notes}")

        # همه گزینه‌ها
        if len(plan.all_options) > 1:
            lines.append("")
            lines.append("  📊 **سایر گزینه‌ها:**")
            for opt in plan.all_options[1:3]:  # فقط ۲ گزینه بعدی
                lines.append(f"    • {opt.vehicle_name_fa}: {opt.trip_count} مرحله")

        return "\n".join(lines)

    @classmethod
    def _format_number(cls, num: float) -> str:
        """فرمت عدد فارسی"""
        if num == int(num):
            return f"{int(num):,}"
        return f"{num:,.2f}"

    @classmethod
    def format_welcome(cls) -> str:
        """پیام خوش‌آمد"""
        return """👋 **سلام! به ربات برآورد مصالح خوش آمدید.**

من می‌توانم مصالح مورد نیاز برای کارهای ساختمانی را برآورد کنم.

**کارهای پشتیبانی‌شده:**
• 🧱 کاشی‌کاری (دیوار/کف)
• 🏗️ گچ‌کاری
• 🔩 آرماتوربندی
• 🏭 بتن‌ریزی

**نمونه پیام:**
`۱۰۰ متر کاشی کاری کف حمام ضخامت ۳ سانت`

فقط متن خود را بفرستید!"""

    @classmethod
    def format_help(cls) -> str:
        """پیام راهنما"""
        return """📖 **راهمای استفاده:**

**۱. کاشی‌کاری:**
`۱۲۰ متر کاشی دیوار حمام`
`۵۰ متر کاشی کف آشپزخانه ۶۰ در ۶۰`

**۲. گچ‌کاری:**
`۲۰۰ متر گچ دیوار داخلی`
`۱۵۰ متر گچ سقف`

**۳. آرماتوربندی:**
`۱۰۰ متر آرماتور سقف`
`۵ متر مکعب آرماتور ستون`

**۴. بتن‌ریزی:**
`۲۰ متر مکعب بتن سقف`
`۱۰ متر مکعب بتن فونداسیون`

**نکات:**
• می‌توانید ضخامت بستر را هم بنویسید (مثلاً: ضخامت ۵ سانت)
• منطقه مرطوب (حمام، استخر) به صورت خودکار تشخیص داده می‌شود
• حمل و نقل بهینه هم محاسبه می‌شود"""

    @classmethod
    def format_error(cls, message: str) -> str:
        """فرمت خطا"""
        return f"❌ **خطا:**\n{message}\n\nبرای راهنمایی /help را بفرستید."

    @classmethod
    def format_not_understood(cls) -> str:
        """پیام عدم درک متن"""
        return """🤔 متوجه نشدم. لطفاً با فرمت واضح‌تر بنویسید.

**مثال:**
`۱۰۰ متر کاشی کاری کف حمام`

برای راهنمایی: /help"""
