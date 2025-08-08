from __future__ import annotations

# Support both package contexts:
# 1) When imported as `src.domain.complexity` (tests, package execution)
# 2) When imported as `domain.complexity` (running `streamlit run src/app.py`)
try:  # context: src.domain
    from ..text_complexity_children_optimized import (
        calculate_children_text_complexity_optimized,
        compare_algorithms_children_vs_original,
        get_children_complexity_breakdown,
    )
    from ..text_complexity_improved import calculate_text_complexity_improved
    from ..text_complexity_improved import get_complexity_breakdown as get_complexity_breakdown_improved
except Exception:  # context: domain
    from text_complexity_children_optimized import (  # type: ignore
        calculate_children_text_complexity_optimized,
        compare_algorithms_children_vs_original,
        get_children_complexity_breakdown,
    )
    from text_complexity_improved import calculate_text_complexity_improved  # type: ignore
    from text_complexity_improved import get_complexity_breakdown as get_complexity_breakdown_improved  # type: ignore[no-redef]


def get_age_thresholds_info(age: int) -> str:
    """Return formatted threshold information for the given age"""
    thresholds: dict[int, str] = {
        6: "✅ 0-20: Идеально | 👍 20-30: Хорошо | ⚠️ 30-40: Сложно | ❌ 40+: Очень сложно",
        7: "✅ 0-25: Идеально | 👍 25-35: Хорошо | ⚠️ 35-45: Сложно | ❌ 45+: Очень сложно",
        8: "✅ 0-25: Идеально | 👍 25-35: Хорошо | ⚠️ 35-45: Сложно | ❌ 45+: Очень сложно",
        9: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно",
        10: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно",
        11: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно",
    }
    return thresholds.get(age, thresholds[8])


def get_complexity_emoji(complexity: float | int, age: int) -> str:
    """Return emoji based on complexity score and age"""
    if age <= 6:
        if complexity <= 20:
            return "✅"
        elif complexity <= 30:
            return "👍"
        elif complexity <= 40:
            return "⚠️"
        else:
            return "❌"
    elif age <= 8:
        if complexity <= 25:
            return "✅"
        elif complexity <= 35:
            return "👍"
        elif complexity <= 45:
            return "⚠️"
        else:
            return "❌"
    else:  # 9+
        if complexity <= 30:
            return "✅"
        elif complexity <= 40:
            return "👍"
        elif complexity <= 50:
            return "⚠️"
        else:
            return "❌"


def calculate_text_complexity_universal(
    text: str,
    age: int = 8,
    include_cognitive_load: bool = True,
    use_children_algorithm: bool = True,
) -> int:
    """
    Универсальная функция для расчета сложности текста

    Args:
        text: Текст для анализа
        age: Возраст ребенка (6-11 лет)
        include_cognitive_load: Учитывать ли когнитивную нагрузку
        use_children_algorithm: Использовать ли детский алгоритм

    Returns:
        Сложность текста
    """
    if use_children_algorithm:
        return calculate_children_text_complexity_optimized(text, age=age, include_cognitive_load=include_cognitive_load)
    else:
        return calculate_text_complexity_improved(text, age=age, include_cognitive_load=include_cognitive_load)


def get_complexity_breakdown_universal(
    text: str,
    age: int = 8,
    include_cognitive_load: bool = True,
    use_children_algorithm: bool = True,
) -> dict:
    """Универсальная функция для получения детального анализа сложности"""
    if use_children_algorithm:
        return get_children_complexity_breakdown(text, age=age, include_cognitive_load=include_cognitive_load)
    else:
        return get_complexity_breakdown_improved(text, age=age, include_cognitive_load=include_cognitive_load)


__all__ = [
    "get_age_thresholds_info",
    "get_complexity_emoji",
    "calculate_text_complexity_universal",
    "get_complexity_breakdown_universal",
    "compare_algorithms_children_vs_original",
]
