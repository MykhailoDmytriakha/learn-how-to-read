import string

RUSSIAN_VOWELS = "аеёиоуыэюя"
SINGLE_SYLLABLE_WORDS = {"ест", "все", "в", "мяч", "суп"}


def is_vowel(ch: str) -> bool:
    return ch.lower() in RUSSIAN_VOWELS


def strip_trailing_punct(word: str) -> str:
    punct_chars = set(string.punctuation + "«»„“…")
    return word.rstrip("".join(punct_chars))


def unify_text_in_one_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return " ".join(lines)


def split_syllables_hybrid(word: str) -> list[str]:
    """
    Делит слово на слоги, соблюдая принципы:
      1) Если нет/1 гласная или слово в SPECIAL -> 1 слог.
      2) Иначе между парой гласных:
         - если ровно 1 согласная => она целиком в onset следующего слога
         - если >1 согласных => все, кроме последней, к предыдущему слогу,
           последняя => onset следующего слога
      3) Дополнительно: если последняя согласная = 'ь'/'ъ' (знак),
         мы считаем её частью предыдущего слога.
         Пример: "семья" => "семь" + "я"
    """
    w = word.lower()

    # (1) особые случаи
    if w in SINGLE_SYLLABLE_WORDS or not any(is_vowel(c) for c in w) or sum(is_vowel(c) for c in w) == 1:
        return [w]

    # Иначе несколько гласных
    syllables = []
    vowel_positions = [i for i, ch in enumerate(w) if is_vowel(ch)]

    # 1-й слог (до и включая первую гласную)
    first_vowel = vowel_positions[0]
    syllables.append(w[: first_vowel + 1])

    for i in range(len(vowel_positions) - 1):
        curr_v = vowel_positions[i]
        next_v = vowel_positions[i + 1]
        c_part = w[curr_v + 1 : next_v]  # согласные между гласными

        if len(c_part) == 0:
            # Нет согласных, просто новая гласная => новый слог
            syllables.append(w[next_v : next_v + 1])
        elif len(c_part) == 1:
            # Ровно 1 согласная => целиком в onset следующего слога
            # Но проверим, вдруг это 'ь'/'ъ' — тогда оставим в предыдущем?
            # Однако по условию test6 "семья" -> "семь"+"я",
            # здесь 2 согласных "м"(2),"ь"(3). Потому len(c_part)=2 => другой случай.
            new_syll = c_part + w[next_v : next_v + 1]
            syllables.append(new_syll)
        else:
            # >1 согласных
            # Все, кроме последней, к предыдущему слогу,
            # последняя => onset следующего
            c_part_prev = c_part[:-1]
            c_part_next = c_part[-1]

            # Если последний символ = 'ь'/'ъ',
            # то отдаём его тоже к предыдущему слогу (пример: "семья")
            if c_part_next in ("ь", "ъ"):
                # Значит все согласные идут в предыдущий слог
                syllables[-1] += c_part
                # А следующий слог будет только гласная
                syllables.append(w[next_v : next_v + 1])
            else:
                # Стандартный случай
                syllables[-1] += c_part_prev
                new_syll = c_part_next + w[next_v : next_v + 1]
                syllables.append(new_syll)

    # Хвост после последней гласной
    last_v = vowel_positions[-1]
    tail = w[last_v + 1 :]
    if tail:
        # Если хвост начинается на 'ь'/'ъ',
        # приклеим его к предыдущему слогу
        if tail[0] in ("ь", "ъ"):
            syllables[-1] += tail
        else:
            # иначе стандартно добавляем согласные к последнему слогу
            syllables[-1] += tail

    return syllables


def get_full_text_data(text: str) -> dict:
    level_name = "Полный текст"
    raw_tokens = text.split()
    level3_words = []
    for token in raw_tokens:
        w3 = strip_trailing_punct(token)
        if w3:
            level3_words.append(w3)
    full_line = unify_text_in_one_line(text)
    level3_words.append(full_line)
    return {"levelName": level_name, "words": level3_words}


def hyphenate_word_with_syllables(word: str) -> str:
    cleaned_word = word.strip(string.punctuation + "«»„“…").lower()
    if not cleaned_word:
        return ""
    syllables = split_syllables_hybrid(cleaned_word)
    if len(syllables) > 1:
        return "-".join(syllables)
    else:
        return syllables[0]


def split_hyphenated_word_into_list(hyphenated_word: str) -> list[str]:
    return hyphenated_word.split("-")


def process_text(text: str) -> dict:
    level_name_1 = "Слоги"
    level_name_2 = "Слова по слогам"
    level_name_3 = "Полный текст"

    raw_tokens = text.split()
    all_syllables = []
    hyphenated_words = []
    level3_words = []

    for token in raw_tokens:
        # Уровень 3: убираем только завершающую пунктуацию
        w3 = strip_trailing_punct(token)
        if w3:
            level3_words.append(w3)

        # Для слогов: убираем внешнюю пунктуацию, к lower
        w_clean = token.strip(string.punctuation + "«»„“…").lower()
        if not w_clean:
            continue

        # Делим на слоги
        sylls = split_syllables_hybrid(w_clean)

        # Уровень 1
        all_syllables.extend(sylls)

        # Уровень 2
        if len(sylls) > 1:
            hyphenated_words.append("-".join(sylls))
        else:
            hyphenated_words.append(sylls[0])

    # Добавляем полное предложение (одной строкой)
    full_line = unify_text_in_one_line(text)
    level3_words.append(full_line)

    return {
        1: {"levelName": level_name_1, "words": all_syllables},
        2: {"levelName": level_name_2, "words": hyphenated_words},
        3: {"levelName": level_name_3, "words": level3_words},
    }
