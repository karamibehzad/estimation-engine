"""
هندلر پیام‌های تلگرام
Telegram Bot Message Handlers
"""

from telegram import Update
from telegram.ext import ContextTypes

from estimation_engine.ai.extractor import RuleBasedExtractor
from estimation_engine.core.calculators import (
    get_calculator, TilingCalculator, PlasteringCalculator,
    RebarCalculator, ConcreteCalculator
)
from estimation_engine.core.transport import TransportCalculator
from estimation_engine.core.optimizer import MaterialOptimizer
from estimation_engine.utils.formatters import PersianFormatter
from estimation_engine.utils.validators import InputValidator


# استخراج‌کننده پارامترها
extractor = RuleBasedExtractor()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    await update.message.reply_text(
        PersianFormatter.format_welcome(),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    await update.message.reply_text(
        PersianFormatter.format_help(),
        parse_mode="Markdown"
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام متنی کاربر"""
    text = update.message.text

    # ۱. استخراج پارامترها از متن
    params = extractor.extract(text)

    # ۲. بررسی confidence
    if params.confidence < 0.5 or not params.work_type:
        await update.message.reply_text(
            PersianFormatter.format_not_understood(),
            parse_mode="Markdown"
        )
        return

    try:
        # ۳. اجرای محاسبه بر اساس نوع کار
        result = await _calculate_estimation(params)

        if not result:
            await update.message.reply_text(
                PersianFormatter.format_error("نوع کار یا پارامترهای کافی شناسایی نشد."),
                parse_mode="Markdown"
            )
            return

        # ۴. محاسبه حمل و نقل برای مصالح اصلی
        result = await _add_transport_plan(result)

        # ۵. دریافت پیشنهادهای بهینه‌سازی
        suggestions = await _get_optimization_suggestions(params, result)

        # ۶. فرمت کردن خروجی
        response = PersianFormatter.format_estimation(result)

        # ۷. اضافه کردن پیشنهادها
        if suggestions:
            response += "\n\n📋 **پیشنهادهای بهینه‌سازی:**\n"
            for i, sug in enumerate(suggestions, 1):
                impact_emoji = "🔴" if sug.impact == "high" else "🟡" if sug.impact == "medium" else "🟢"
                response += f"{impact_emoji} {sug.message_fa}\n"

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            PersianFormatter.format_error(f"خطا در محاسبه: {str(e)}"),
            parse_mode="Markdown"
        )


async def _calculate_estimation(params):
    """اجرای محاسبه بر اساس پارامترهای استخراج‌شده"""

    if params.work_type == "tiling":
        # اعتبارسنجی
        if not params.area:
            return None
        valid, error = InputValidator.validate_area(params.area)
        if not valid:
            return None

        return TilingCalculator.calculate(
            area_m2=params.area,
            location=params.location or "wall",
            is_wet_area=params.is_wet_area,
            bed_thickness_cm=params.bed_thickness_cm or 3.0,
            tile_size_cm=params.tile_size_cm,
        )

    elif params.work_type == "plastering":
        if not params.area:
            return None
        valid, error = InputValidator.validate_area(params.area)
        if not valid:
            return None

        return PlasteringCalculator.calculate(
            area_m2=params.area,
            surface_type=params.surface_type or "interior_wall",
        )

    elif params.work_type == "rebar":
        quantity = params.area or params.volume_m3
        if not quantity:
            return None

        unit = "m2" if params.area else "m3"
        return RebarCalculator.calculate(
            quantity=quantity,
            quantity_unit=unit,
            element_type=params.element_type or "slab",
        )

    elif params.work_type == "concrete":
        if not params.volume_m3:
            # اگر حجم نبود ولی مساحت بود، تخمین بزن
            if params.area:
                # تخمین: ۰.۲ متر ضخامت پیش‌فرض
                params.volume_m3 = params.area * 0.2
            else:
                return None

        valid, error = InputValidator.validate_volume(params.volume_m3)
        if not valid:
            return None

        return ConcreteCalculator.calculate(
            volume_m3=params.volume_m3,
            element_type=params.element_type or "slab",
        )

    return None


async def _add_transport_plan(result):
    """اضافه کردن پلن حمل و نقل به نتیجه"""
    from estimation_engine.core.constants import TRANSPORT_CONFIG

    # برای مصالح اصلی (ماسه، سیمان، شن) حمل محاسبه کن
    for mat in result.materials:
        if mat.name_en in ["sand", "gravel", "cement"]:
            density = TRANSPORT_CONFIG["material_density"].get(mat.name_en)
            plan = TransportCalculator.calculate(
                material_name_en=mat.name_en,
                quantity=mat.quantity,
                unit=mat.unit,
                material_density_kg_m3=density,
            )
            # فقط برای اولین مصالح اصلی پلن حمل را ذخیره کن
            if not result.transport_plan:
                result.transport_plan = plan
            break

    return result


async def _get_optimization_suggestions(params, result):
    """دریافت پیشنهادهای بهینه‌سازی"""
    suggestions = []

    if params.work_type == "tiling":
        suggestions = MaterialOptimizer.optimize_tiling(
            area_m2=params.area or 0,
            tile_size_cm=params.tile_size_cm,
            bed_thickness_cm=params.bed_thickness_cm or 3.0,
        )
    elif params.work_type == "concrete":
        suggestions = MaterialOptimizer.optimize_concrete(
            volume_m3=params.volume_m3 or 0,
        )

    return suggestions


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش پیام صوتی (برای آینده)"""
    await update.message.reply_text(
        "🎤 پیام صوتی دریافت شد.\n"
        "⚠️ تبدیل صدا به من هنوز فعال نیست.\n"
        "لطفاً متن خود را تایپ کنید.",
        parse_mode="Markdown"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    print(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.",
            parse_mode="Markdown"
        )
