from src.syllable_processor import get_full_text_data, hyphenate_word_with_syllables, process_text, split_hyphenated_word_into_list


def test_text1():
    text = "Мама мыла раму."
    expected = {
        1: {"levelName": "Слоги", "words": ["ма", "ма", "мы", "ла", "ра", "му"]},
        2: {"levelName": "Слова по слогам", "words": ["ма-ма", "мы-ла", "ра-му"]},
        3: {"levelName": "Полный текст", "words": ["Мама", "мыла", "раму", "Мама мыла раму."]},
    }
    assert process_text(text) == expected


def test_text2():
    text = "Саша ест кашу."
    expected = {
        1: {"levelName": "Слоги", "words": ["са", "ша", "ест", "ка", "шу"]},
        2: {"levelName": "Слова по слогам", "words": ["са-ша", "ест", "ка-шу"]},
        3: {"levelName": "Полный текст", "words": ["Саша", "ест", "кашу", "Саша ест кашу."]},
    }
    assert process_text(text) == expected


def test_text3():
    text = "На реке рыбаки."
    expected = {
        1: {"levelName": "Слоги", "words": ["на", "ре", "ке", "ры", "ба", "ки"]},
        2: {"levelName": "Слова по слогам", "words": ["на", "ре-ке", "ры-ба-ки"]},
        3: {"levelName": "Полный текст", "words": ["На", "реке", "рыбаки", "На реке рыбаки."]},
    }
    assert process_text(text) == expected


def test_text4():
    text = """Мама готовит суп.
        Папа читает книгу.
        Кошка пьёт молоко.
        Дети играют в парке.
        Мы любим лето."""
    expected = {
        1: {
            "levelName": "Слоги",
            "words": [
                "ма",
                "ма",
                "го",
                "то",
                "вит",
                "суп",
                "па",
                "па",
                "чи",
                "та",
                "ет",
                "кни",
                "гу",
                "кош",
                "ка",
                "пьёт",
                "мо",
                "ло",
                "ко",
                "де",
                "ти",
                "иг",
                "ра",
                "ют",
                "в",
                "пар",
                "ке",
                "мы",
                "лю",
                "бим",
                "ле",
                "то",
            ],
        },
        2: {
            "levelName": "Слова по слогам",
            "words": [
                "ма-ма",
                "го-то-вит",
                "суп",
                "па-па",
                "чи-та-ет",
                "кни-гу",
                "кош-ка",
                "пьёт",
                "мо-ло-ко",
                "де-ти",
                "иг-ра-ют",
                "в",
                "пар-ке",
                "мы",
                "лю-бим",
                "ле-то",
            ],
        },
        3: {
            "levelName": "Полный текст",
            "words": [
                "Мама",
                "готовит",
                "суп",
                "Папа",
                "читает",
                "книгу",
                "Кошка",
                "пьёт",
                "молоко",
                "Дети",
                "играют",
                "в",
                "парке",
                "Мы",
                "любим",
                "лето",
                "Мама готовит суп. Папа читает книгу. Кошка пьёт молоко. Дети играют в парке. Мы любим лето.",
            ],
        },
    }
    assert process_text(text) == expected


def test_text5():
    text = """На улице дети играют.
        Даниил играет в мяч.
        Наоми едет на велосипеде.
        Олег играет машинками.
        Все веселятся и смеются."""
    expected = {
        1: {
            "levelName": "Слоги",
            "words": [
                "на",
                "у",
                "ли",
                "це",
                "де",
                "ти",
                "иг",
                "ра",
                "ют",
                "да",
                "ни",
                "ил",
                "иг",
                "ра",
                "ет",
                "в",
                "мяч",
                "на",
                "о",
                "ми",
                "е",
                "дет",
                "на",
                "ве",
                "ло",
                "си",
                "пе",
                "де",
                "о",
                "лег",
                "иг",
                "ра",
                "ет",
                "ма",
                "шин",
                "ка",
                "ми",
                "все",
                "ве",
                "се",
                "лят",
                "ся",
                "и",
                "сме",
                "ют",
                "ся",
            ],
        },
        2: {
            "levelName": "Слова по слогам",
            "words": [
                "на",
                "у-ли-це",
                "де-ти",
                "иг-ра-ют",
                "да-ни-ил",
                "иг-ра-ет",
                "в",
                "мяч",
                "на-о-ми",
                "е-дет",
                "на",
                "ве-ло-си-пе-де",
                "о-лег",
                "иг-ра-ет",
                "ма-шин-ка-ми",
                "все",
                "ве-се-лят-ся",
                "и",
                "сме-ют-ся",
            ],
        },
        3: {
            "levelName": "Полный текст",
            "words": [
                "На",
                "улице",
                "дети",
                "играют",
                "Даниил",
                "играет",
                "в",
                "мяч",
                "Наоми",
                "едет",
                "на",
                "велосипеде",
                "Олег",
                "играет",
                "машинками",
                "Все",
                "веселятся",
                "и",
                "смеются",
                "На улице дети играют. Даниил играет в мяч. Наоми едет на велосипеде. Олег играет машинками. Все веселятся и смеются.",
            ],
        },
    }
    assert process_text(text) == expected


def test_text6():
    text = """Сегодня хорошая погода.
Я люблю кушать мороженое.
Мама любит папу.
Папа любит маму.
Мы дружная семья."""

    expected = {
        1: {
            "levelName": "Слоги",
            "words": [
                "се",
                "год",
                "ня",  # Сегодня
                "хо",
                "ро",
                "ша",
                "я",  # хорошая
                "по",
                "го",
                "да",  # погода
                "я",  # Я
                "люб",
                "лю",  # люблю
                "ку",
                "шать",  # кушать
                "мо",
                "ро",
                "же",
                "но",
                "е",  # мороженое
                "ма",
                "ма",  # Мама
                "лю",
                "бит",  # любит
                "па",
                "пу",  # папу
                "па",
                "па",  # Папа
                "лю",
                "бит",
                "ма",
                "му",  # маму
                "мы",  # Мы
                "друж",
                "на",
                "я",  # дружная
                "семь",
                "я",  # семья
            ],
        },
        2: {
            "levelName": "Слова по слогам",
            "words": [
                "се-год-ня",  # Сегодня
                "хо-ро-ша-я",  # хорошая
                "по-го-да",  # погода
                "я",  # Я
                "люб-лю",  # люблю
                "ку-шать",  # кушать
                "мо-ро-же-но-е",  # мороженое
                "ма-ма",  # Мама
                "лю-бит",  # любит
                "па-пу",  # папу
                "па-па",  # Папа
                "лю-бит",  # любит
                "ма-му",  # маму
                "мы",  # Мы
                "друж-на-я",  # дружная
                "семь-я",  # семья
            ],
        },
        3: {
            "levelName": "Полный текст",
            "words": [
                "Сегодня",
                "хорошая",
                "погода",
                "Я",
                "люблю",
                "кушать",
                "мороженое",
                "Мама",
                "любит",
                "папу",
                "Папа",
                "любит",
                "маму",
                "Мы",
                "дружная",
                "семья",
                "Сегодня хорошая погода. Я люблю кушать мороженое. Мама любит папу. Папа любит маму. Мы дружная семья.",
            ],
        },
    }
    assert process_text(text) == expected


def test_get_full_text_data():
    text = "Привет, мир!"
    expected_output = {"levelName": "Полный текст", "words": ["Привет", "мир", "Привет, мир!"]}
    assert get_full_text_data(text) == expected_output


def test_hyphenate_word_with_syllables():
    word = "семья"
    expected_output = "семь-я"
    assert hyphenate_word_with_syllables(word) == expected_output

    word = "кот"
    expected_output = "кот"
    assert hyphenate_word_with_syllables(word) == expected_output

    word = ""
    expected_output = ""
    assert hyphenate_word_with_syllables(word) == expected_output

    word = "папа"
    expected_output = "па-па"
    assert hyphenate_word_with_syllables(word) == expected_output

    word = "веселятся"
    expected_output = "ве-се-лят-ся"
    assert hyphenate_word_with_syllables(word) == expected_output

    word = "смеются"
    expected_output = "сме-ют-ся"
    assert hyphenate_word_with_syllables(word) == expected_output


def test_split_hyphenated_word_into_list():
    hyphenated_word = "семь-я"
    expected_output = ["семь", "я"]
    assert split_hyphenated_word_into_list(hyphenated_word) == expected_output

    hyphenated_word = "кот"
    expected_output = ["кот"]
    assert split_hyphenated_word_into_list(hyphenated_word) == expected_output

    hyphenated_word = ""
    expected_output = [""]
    assert split_hyphenated_word_into_list(hyphenated_word) == expected_output
