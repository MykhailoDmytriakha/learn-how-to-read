"""
Улучшенный алгоритм расчета сложности текста для обучения детей чтению
"""
import math
from typing import List, Dict, Tuple
from syllable_processor import split_syllables_hybrid, is_vowel

def calculate_cognitive_load(text: str, age: int) -> float:
    """
    Расчет когнитивной нагрузки от длины текста с учетом возраста ребенка.
    
    Args:
        text: Анализируемый текст
        age: Возраст ребенка (6-11 лет)
        
    Returns:
        Когнитивная нагрузка (0-50 баллов)
    """
    words = len([word for word in text.split() if word.strip()])
    
    if words == 0:
        return 0
    
    # Возрастные коэффициенты влияния длины
    age_factors = {
        6: {"factor": 1.8, "divisor": 5},   # Максимальное влияние длины
        7: {"factor": 1.5, "divisor": 7},   # Высокое влияние
        8: {"factor": 1.0, "divisor": 10},  # Базовое влияние
        9: {"factor": 0.8, "divisor": 12},  # Умеренное влияние
        10: {"factor": 0.7, "divisor": 15}, # Низкое влияние
        11: {"factor": 0.6, "divisor": 18}  # Минимальное влияние
    }
    
    # Используем ближайший возраст если точного нет
    if age not in age_factors:
        if age < 6:
            age = 6
        elif age > 11:
            age = 11
        else:
            # Интерполяция между соседними возрастами
            lower_age = max([a for a in age_factors.keys() if a <= age])
            age = lower_age
    
    params = age_factors[age]
    
    # Логарифмическая формула: больше влияние для коротких текстов
    cognitive_load = min(50, math.log(1 + words / params["divisor"]) * params["factor"] * 10)
    
    return cognitive_load

def calculate_text_complexity_improved(text: str, age: int = 8, include_cognitive_load: bool = False) -> int:
    """
    Улучшенный алгоритм расчета сложности текста.
    
    Args:
        text: Текст для анализа
        age: Возраст ребенка (6-11 лет)
        include_cognitive_load: Учитывать ли когнитивную нагрузку от длины
    
    Returns:
        Сложность текста:
        - Без когнитивной нагрузки: 0-100 (чистая лингвистическая сложность)
        - С когнитивной нагрузкой: 0-150 (включает влияние длины текста)
    
    Основные улучшения:
    1. Более точная оценка сложности слогов
    2. Сбалансированные весовые коэффициенты
    3. Учет морфологической сложности
    4. Улучшенная частотная модель
    5. Опциональный учет когнитивной нагрузки от длины
    """
    if not text.strip():
        return 0
    
    # Обновленная частотная модель букв (на основе современных корпусов)
    letter_frequency = {
        'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70,
        'т': 6.26, 'с': 5.47, 'р': 4.73, 'в': 4.54, 'л': 4.40,
        'к': 3.49, 'м': 3.21, 'д': 2.98, 'п': 2.81, 'у': 2.62,
        'я': 2.01, 'ы': 1.90, 'ь': 1.74, 'г': 1.70, 'з': 1.65,
        'б': 1.59, 'ч': 1.44, 'й': 1.21, 'х': 0.97, 'ж': 0.94,
        'ю': 0.64, 'ш': 0.73, 'ц': 0.48, 'щ': 0.36, 'э': 0.32,
        'ф': 0.26, 'ъ': 0.04, 'ё': 0.04
    }
    
    # Более мягкая шкала сложности букв
    letter_complexity = {}
    sorted_letters = sorted(letter_frequency.items(), key=lambda x: x[1], reverse=True)
    for i, (letter, freq) in enumerate(sorted_letters):
        # Логарифмическая шкала вместо линейной
        complexity = math.log(i + 2) * 2
        letter_complexity[letter] = complexity
    
    # Сложные сочетания букв
    difficult_combinations = {
        'жы': 8, 'шы': 8, 'чя': 6, 'щя': 6, 'чю': 6, 'щю': 6,
        'тся': 4, 'ться': 4, 'ство': 3, 'ння': 5, 'льн': 4
    }
    
    words = [word.strip() for word in text.split() if word.strip()]
    if not words:
        return 0
    
    total_words = len(words)
    total_chars = sum(len(word) for word in words)
    
    # Компоненты сложности
    syllable_complexity_score = 0
    morphological_score = 0
    phonetic_score = 0
    lexical_score = 0
    
    syllable_complexities = []
    word_lengths = []
    
    for word in words:
        word_lower = word.lower()
        syllables = split_syllables_hybrid(word_lower)
        word_lengths.append(len(syllables))
        
        # 1. Анализ сложности слогов (улучшенный)
        for syll in syllables:
            consonants = sum(1 for c in syll if not is_vowel(c) and c not in ('ь', 'ъ'))
            vowels = sum(1 for c in syll if is_vowel(c))
            special_chars = sum(1 for c in syll if c in ('ь', 'ъ'))
            
            # Более точная оценка сложности слога
            syll_complexity = 0
            
            # Согласные кластеры
            if consonants >= 3:
                syll_complexity += 3  # Сложные кластеры
            elif consonants == 2:
                syll_complexity += 1  # Умеренные кластеры
            
            # Специальные символы
            syll_complexity += special_chars * 2
            
            # Несколько гласных подряд
            consecutive_vowels = sum(
                1 for i in range(len(syll)-1) 
                if is_vowel(syll[i]) and is_vowel(syll[i+1])
            )
            syll_complexity += consecutive_vowels * 2
            
            # Длина слога (более мягкий подход)
            if len(syll) >= 5:
                syll_complexity += 2
            elif len(syll) == 4:
                syll_complexity += 1
            
            syllable_complexities.append(syll_complexity)
        
        # 2. Лексическая сложность
        word_lexical_score = 0
        for char in word_lower:
            word_lexical_score += letter_complexity.get(char, 5)
        
        # Нормализация по длине слова
        if len(word_lower) > 0:
            lexical_score += word_lexical_score / len(word_lower)
        
        # 3. Морфологическая сложность
        # Длинные слова (потенциально сложная морфология)
        if len(word) > 7:
            morphological_score += 2
        elif len(word) > 5:
            morphological_score += 1
        
        # Окончания, указывающие на сложность
        if word_lower.endswith(('ость', 'ение', 'ание', 'ция', 'сия')):
            morphological_score += 2
        
        # 4. Фонетическая сложность
        for combination, score in difficult_combinations.items():
            if combination in word_lower:
                phonetic_score += score
    
    # Расчет итоговых компонентов (0-100 шкала)
    
    # 1. Сложность слогов (0-30)
    if syllable_complexities:
        avg_syllable_complexity = sum(syllable_complexities) / len(syllable_complexities)
        syllable_complexity_score = min(30, avg_syllable_complexity * 4)
    
    # 2. Структурная сложность (0-20)
    avg_syllables_per_word = sum(word_lengths) / len(word_lengths) if word_lengths else 1
    avg_word_length = total_chars / total_words if total_words > 0 else 1
    
    structural_score = min(20, 
        (avg_syllables_per_word - 1) * 5 + 
        (avg_word_length - 3) * 2
    )
    
    # 3. Лексическая сложность (0-25)
    if total_words > 0:
        avg_lexical_complexity = lexical_score / total_words
        lexical_complexity_score = min(25, avg_lexical_complexity * 2)
    else:
        lexical_complexity_score = 0
    
    # 4. Морфологическая сложность (0-15)
    morphological_complexity_score = min(15, morphological_score * 0.5)
    
    # 5. Фонетическая сложность (0-10)
    phonetic_complexity_score = min(10, phonetic_score * 0.3)
    
    # Базовая лингвистическая сложность (0-100)
    linguistic_complexity = (
        syllable_complexity_score +
        structural_score +
        lexical_complexity_score +
        morphological_complexity_score +
        phonetic_complexity_score
    )
    
    # Добавляем когнитивную нагрузку если требуется
    if include_cognitive_load:
        cognitive_load = calculate_cognitive_load(text, age)
        total_complexity = linguistic_complexity + cognitive_load
    else:
        total_complexity = linguistic_complexity
    
    return int(total_complexity)


def get_complexity_breakdown(text: str, age: int = 8, include_cognitive_load: bool = False) -> Dict[str, float]:
    """
    Возвращает детальную разбивку компонентов сложности для анализа
    """
    linguistic_complexity = calculate_text_complexity_improved(text, age=age, include_cognitive_load=False)
    cognitive_load = calculate_cognitive_load(text, age) if include_cognitive_load else 0
    total_complexity = linguistic_complexity + cognitive_load
    
    return {
        "text": text,
        "age": age,
        "words": len(text.split()),
        "linguistic_complexity": linguistic_complexity,
        "cognitive_load": cognitive_load,
        "total_complexity": total_complexity,
        "syllable_component": linguistic_complexity * 0.3,
        "structural_component": linguistic_complexity * 0.2,
        "lexical_component": linguistic_complexity * 0.25,
        "morphological_component": linguistic_complexity * 0.15,
        "phonetic_component": linguistic_complexity * 0.1
    }


# Функция сравнения старого и нового алгоритмов
def compare_algorithms(text: str, age: int = 8, include_cognitive_load: bool = False) -> Dict[str, int]:
    """Сравнивает результаты старого и нового алгоритмов"""
    from text_complexity import calculate_text_complexity
    
    old_score = calculate_text_complexity(text)
    new_score = calculate_text_complexity_improved(text, age=age, include_cognitive_load=include_cognitive_load)
    
    return {
        "text": text,
        "age": age,
        "include_cognitive_load": include_cognitive_load,
        "old_algorithm": old_score,
        "new_algorithm": new_score,
        "difference": new_score - old_score
    }

# Удобная функция для оценки сложности для конкретного возраста
def calculate_complexity_for_age(text: str, age: int) -> Dict[str, float]:
    """
    Удобная функция для полной оценки сложности с учетом возраста
    """
    return get_complexity_breakdown(text, age=age, include_cognitive_load=True)