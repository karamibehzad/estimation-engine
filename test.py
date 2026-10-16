from estimation_engine.core.calculators import TilingCalculator
from estimation_engine.utils.formatters import PersianFormatter

r = TilingCalculator.calculate(100, 'wall', True, 3.0, (30, 60))
print(PersianFormatter.format_estimation(r))
