import math
from collections import Counter
from typing import List
from src.syllable_processor import split_syllables_hybrid, is_vowel

def calculate_text_complexity(text: str) -> int:
    words = [word.strip() for word in text.split() if word.strip()]
    total_words = len(words)
    total_chars = sum(len(word) for word in words)

    syllable_complexities = []
    word_lengths: List[int] = []
    rare_chars: Counter[str] = Counter()
    total_consecutive_vowels = 0

    for word in words:
        word_lower = word.lower()
        syllables = split_syllables_hybrid(word_lower)
        word_lengths.append(len(syllables))

        for syll in syllables:
            # Базовые параметры
            consonants = sum(1 for c in syll if not is_vowel(c) and c not in ('ь', 'ъ'))
            special_chars = sum(1 for c in syll if c in ('ь', 'ъ'))
            consecutive_vowels = sum(
                1 for i in range(len(syll)-1) 
                if is_vowel(syll[i]) and is_vowel(syll[i+1])
            )
            
            # Новый параметр: длина слога по вашей схеме
            syll_len = len(syll)
            length_score = max(0, (syll_len - 2) * 5) if syll_len >= 3 else 0

            syll_complexity = (
                min(3, consonants) 
                + special_chars 
                + consecutive_vowels 
                + length_score  # <-- Добавлено здесь
            )
            syllable_complexities.append(syll_complexity)

        rare_chars.update(c for c in word_lower if c in {'ё', 'э', 'ъ', 'ф', 'ц', 'щ', 'ш', 'ч'})

    # 1. Сложность слогов (0-50 points)
    avg_syll_complexity = (
        sum(syllable_complexities) / len(syllable_complexities) 
        if syllable_complexities else 0
    )
    syll_score = min(50, avg_syll_complexity * 3)  # Множитель снижен для баланса

    # 2. Длина текста (0-20 points)
    length_score = int(min(
        20, 
        math.log(total_words + total_chars/20 + 1) * 3  # Медленный рост
    ))

    # 3. Структура слов (0-15 points)
    avg_syllables_per_word = (
        sum(word_lengths) / len(word_lengths) 
        if word_lengths else 0
    )
    word_structure_score = min(15, avg_syllables_per_word * 3)

    # 4. Редкие символы (0-15 points)
    rare_score = min(
        15, 
        (sum(rare_chars.values()) / total_chars * 100) 
        if total_chars else 0
    )

    total_score = (
        syll_score 
        + length_score 
        + word_structure_score 
        + rare_score
    )

    return min(100, max(1, int(total_score)))