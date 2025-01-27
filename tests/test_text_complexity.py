import pytest
import json
from src.text_complexity import calculate_text_complexity

def test_very_simple_text():
    text = "Мама мыла раму"
    expected_score = 20
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_medium_complexity():
    text = "Я привествую вас позле подъезда"
    expected_score = 29
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_high_complexity():
    text = "Сверхсложное многосложное слово с ё и щупальцами"
    expected_score = 35
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_medium_high_complexity():
    text = "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
    expected_score = 41
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_simple_text():
    text = "Кот спит на диване."
    expected_score = 23
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_medium_complexity_2():
    text = "Аэроплан летит высоко в небе."
    expected_score = 29
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_medium_high_complexity_2():
    text = "Философия и математика — основы науки."
    expected_score = 32
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_empty_text():
    text = ""
    expected_score = 1
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_simple_word_with_consonants():
    text = "привестсвую"
    expected_score = 25  # Adjust this score based on your scoring logic
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_another_simple_word_with_consonants():
    text = "собака"
    expected_score = 22  # Adjust this score based on your scoring logic
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"

def test_yet_another_simple_word_with_consonants():
    text = "книга"
    expected_score = 21  # Adjust this score based on your scoring logic
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"
    
def test_1():
    text = "семья"
    expected_score = 21  # Adjust this score based on your scoring logic
    score = calculate_text_complexity(text)
    assert abs(score - expected_score) <= 10, f"Ошибка: {text} (ожидалось {expected_score}, получено {score})"