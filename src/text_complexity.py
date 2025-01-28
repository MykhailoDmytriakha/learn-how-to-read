import math
from typing import List
from syllable_processor import split_syllables_hybrid, is_vowel

def calculate_text_complexity(text: str) -> int:
    # Define the order of letters and their corresponding difficulty scores
    letter_order = "ауомсхршылнктипзйгвдбжеьяюёчэцфщъ"
    letter_frequency = {
        'а': 8.01, 'о': 7.28, 'е': 5.47, 'и': 5.45, 
        'н': 4.32, 'т': 4.19, 'с': 4.00, 'р': 3.60,
        'в': 3.20, 'л': 3.10, 'к': 2.90, 'м': 2.80,
        'д': 2.50, 'п': 2.30, 'у': 2.10, 'я': 1.90,
        'ы': 1.80, 'ь': 1.70, 'г': 1.60, 'з': 1.50,
        'б': 1.40, 'ч': 1.30, 'й': 1.20, 'х': 1.10,
        'ж': 1.00, 'ю': 0.90, 'ш': 0.80, 'ц': 0.70,
        'щ': 0.60, 'э': 0.50, 'ф': 0.40, 'ъ': 0.30,
        'ё': 0.20
    }
    letter_to_score = {
        char: (idx * 3) * (1 - letter_frequency.get(char, 0) / 10) 
        for idx, char in enumerate(letter_order)
    }
    
    words = [word.strip() for word in text.split() if word.strip()]
    total_words = len(words)
    total_chars = sum(len(word) for word in words)

    syllable_complexities = []
    word_lengths: List[int] = []
    total_letter_score = 0  # Accumulator for letter order scores
    total_consecutive_vowels = 0
    difficult_combinations = ['чк', 'чн', 'щн', 'жы', 'шы', 'чя', 'щя']
    combination_bonus = 5  # Бонус за каждое сложное сочетание

    for word in words:
        word_lower = word.lower()
        syllables = split_syllables_hybrid(word_lower)
        word_lengths.append(len(syllables))

        # Calculate letter order score for each character in the word
        for c in word_lower:
            total_letter_score += int(letter_to_score.get(c, 0))

        # Syllable complexity processing
        for syll in syllables:
            consonants = sum(1 for c in syll if not is_vowel(c) and c not in ('ь', 'ъ'))
            special_chars = sum(1 for c in syll if c in ('ь', 'ъ'))
            consecutive_vowels = sum(
                1 for i in range(len(syll)-1) 
                if is_vowel(syll[i]) and is_vowel(syll[i+1])
            )
            syll_len = len(syll)
            length_score = max(0, (syll_len - 2) * 5) if syll_len >= 3 else 0

            syll_complexity = (
                min(3, consonants) 
                + special_chars 
                + consecutive_vowels 
                + length_score
            )
            syllable_complexities.append(syll_complexity)

        # Проверяем каждое сложное сочетание
        for comb in difficult_combinations:
            if comb in word_lower:
                total_letter_score += combination_bonus

        # Увеличиваем сложность для слов с мягким/твердым знаком
        if 'ь' in word_lower or 'ъ' in word_lower:
            total_letter_score += 5

    # 1. Syllable complexity score (0-50)
    avg_syll_complexity = (
        sum(syllable_complexities) / len(syllable_complexities) 
        if syllable_complexities else 0
    )
    syll_score = min(50, avg_syll_complexity * 3)

    # 2. Text length score (0-20)
    length_score = int(min(
        20, 
        math.log(total_words + total_chars/20 + 1) * 3  # Медленный рост
    ))

    # 3. Word structure score (0-15)
    avg_syllables_per_word = (
        sum(word_lengths) / len(word_lengths) 
        if word_lengths else 0
    )
    word_structure_score = min(15, avg_syllables_per_word * 3)

    # 4. Letter order score (0-15)
    if total_chars == 0:
        letter_order_score = 0
    else:
        average_letter = total_letter_score / total_chars
        letter_order_score = int(average_letter * (40 / (32*3)))
    letter_order_score = min(15, letter_order_score)

    total_score = (
        syll_score 
        + length_score 
        + word_structure_score 
        + letter_order_score
    )

    return int(total_score)