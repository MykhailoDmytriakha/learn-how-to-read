import json
import logging
from datetime import datetime

import streamlit as st

from domain.complexity import calculate_text_complexity_universal as _calc_universal
from domain.complexity import compare_algorithms_children_vs_original
from domain.complexity import get_age_thresholds_info as _age_thresholds
from domain.complexity import get_complexity_breakdown_universal as _get_breakdown_universal
from domain.complexity import get_complexity_emoji as _emoji
from services.files import load_config as _load_config
from services.files import load_phrases as _load_phrases
from services.files import save_config as _save_config
from services.files import save_phrases as _save_phrases
from services.session import init_session_state as _init_session_state
from syllable_processor import process_text

# Set page config for wide layout
st.set_page_config(layout="wide")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)

# Add this at the top of the file with other imports
PHRASES_FILE = "phrases.json"
CONFIG_FILE = "config.json"

LEVEL_NAMES = {1: "Слоги", 2: "Слова по слогам", 3: "Полный текст"}


def get_age_thresholds_info(age):
    return _age_thresholds(age)


def get_complexity_emoji(complexity, age):
    return _emoji(complexity, age)


def load_config():
    return _load_config()


def save_config(config):
    return _save_config(config)


def update_phrases_complexity():
    """Update complexity for all phrases (no sorting - preserve original order)"""
    if not st.session_state.phrases_data:
        return

    logger.info("Updating complexity for all phrases (preserving original file order)")

    # Recalculate complexity for all phrases
    for phrase in st.session_state.phrases_data:
        phrase["complexity"] = calculate_text_complexity_universal(
            phrase["text"],
            age=st.session_state.child_age,
            include_cognitive_load=st.session_state.use_cognitive_load,
            use_children_algorithm=st.session_state.get("use_children_algorithm", True),
        )

    # No sorting here - file order is preserved like a database
    # UI will sort for display purposes only

    logger.info("Complexity updated (file order preserved)")


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
    return _calc_universal(
        text,
        age=age,
        include_cognitive_load=include_cognitive_load,
        use_children_algorithm=use_children_algorithm,
    )


def get_complexity_breakdown_universal(
    text: str,
    age: int = 8,
    include_cognitive_load: bool = True,
    use_children_algorithm: bool = True,
) -> dict:
    """
    Универсальная функция для получения детального анализа сложности
    """
    return _get_breakdown_universal(
        text,
        age=age,
        include_cognitive_load=include_cognitive_load,
        use_children_algorithm=use_children_algorithm,
    )


BASE_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap');

:root {
    --brand: #5ed2a2;
    --brand-600: #46a37e;
    --bg: #f7fbff;
    --panel: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --border: #e5e7eb;
    --shadow: 0 6px 20px rgba(0,0,0,0.08);
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 10px;
    --space-xs: .375rem;
    --space-sm: .75rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
    font-family: 'Nunito', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, sans-serif !important;
    color: var(--text);
}

/* Buttons */
button[data-testid="stBaseButton-primary"] {
    background-color: var(--brand) !important;
    border-color: var(--brand) !important;
    color: white !important;
    transition: all 0.25s ease !important;
    font-size: 1.15rem !important;
    padding: .9rem 1.1rem !important;
    height: auto !important;
    min-height: 56px !important;
    border-radius: var(--radius-md) !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background-color: var(--brand-600) !important;
    border-color: var(--brand-600) !important;
}
button[data-testid="stBaseButton-secondary"] {
    font-size: 1.05rem !important;
    padding: .85rem 1rem !important;
    height: auto !important;
    min-height: 52px !important;
    border-radius: var(--radius-md) !important;
}
button > div { color: inherit !important; }
button:focus { box-shadow: 0 0 0 0.2rem rgba(94,210,162,.35) !important; outline: none !important; }

/* Cards */
.stContainer {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin-bottom: var(--space-md);
    transition: transform .18s ease, box-shadow .18s ease;
    background: var(--panel);
}
.stContainer:hover { transform: translateY(-2px); box-shadow: var(--shadow); }

/* Progress bar */
.stProgress > div > div > div > div { background-color: var(--brand) !important; }

/* Tabs */
[data-baseweb="tab-list"] {
    gap: .5rem !important;
    border-bottom: 1px solid var(--border);
    margin-bottom: .25rem;
}
button[role="tab"] {
    border-radius: 999px !important;
    padding: .5rem .9rem !important;
    color: var(--muted) !important;
    background: transparent !important;
}
button[role="tab"]:hover {
    background: rgba(94,210,162,.08) !important;
    color: var(--text) !important;
}
button[role="tab"][aria-selected="true"] {
    color: var(--text) !important;
    font-weight: 800 !important;
    background: rgba(94,210,162,.15) !important;
    box-shadow: inset 0 -3px 0 0 var(--brand) !important;
}
button[role="tab"]:focus { outline: none !important; box-shadow: none !important; }

/* Word display */
.word-display {
    font-size: 120px;
    text-align: center;
    margin: var(--space-xl) 0;
    padding: var(--space-xl);
    background: #f8f9fa;
    border-radius: var(--radius-lg);
}
.word-display.bad-blink { animation: badBlink 0.5s ease-in-out forwards; }
.word-display.medium-blink { animation: mediumBlink 0.5s ease-in-out forwards; }
.word-display.good-blink { animation: goodBlink 0.5s ease-in-out forwards; }
@keyframes badBlink { 0% {background:#f8f9fa;} 50% {background:#ffe4e6;} 100% {background:#f8f9fa;} }
@keyframes mediumBlink { 0% {background:#f8f9fa;} 50% {background:#fff7d6;} 100% {background:#f8f9fa;} }
@keyframes goodBlink { 0% {background:#f8f9fa;} 50% {background:#e6ffef;} 100% {background:#f8f9fa;} }

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    padding: .25rem .6rem;
    border-radius: 999px;
    font-size: .95rem;
    background: #e8f8f1;
    color: #1e7a57;
    border: 1px solid #ccefe3;
}

/* Responsive */
@media (max-width: 768px) {
    [data-testid="column"] { width: 100% !important; margin-bottom: var(--space-lg) !important; padding: 0 .5rem !important; }
    .stButton > button { font-size: 1.15rem !important; padding: 1.1rem 1.25rem !important; }
    .word-display { font-size: 84px !important; }
}
@media (min-width: 769px) and (max-width: 1200px) {
    [data-testid="column"] { width: calc(50% - 1rem) !important; margin: 0 .5rem !important; }
}
@media (min-width: 1201px) {
    [data-testid="column"] { width: calc(50% - 3rem) !important; margin: 0 1.5rem !important; }
}

main { max-width: 95% !important; margin: 0 auto !important; }
</style>
"""

CHILD_STYLE = """
<style>
/* Child-friendly theme overrides */
:root {
    --brand-green: #5ed2a2;
    --brand-green-dark: #46a37e;
    --panel-bg: #f7fbff;
}
button[data-testid="stBaseButton-primary"] {
    background-color: var(--brand-green) !important;
    border-color: var(--brand-green) !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background-color: var(--brand-green-dark) !important;
    border-color: var(--brand-green-dark) !important;
}
.word-display {
    background: var(--panel-bg) !important;
}
/* Badge style */
.badge {
    display: inline-block;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    font-size: 0.95rem;
    background: #e8f8f1;
    color: #1e7a57;
    border: 1px solid #ccefe3;
}
</style>
"""

# JavaScript for keyboard shortcuts AND animation handling
KEYBOARD_JS = """
<script>
// Function to trigger animation on word display
function triggerWordAnimation(animationType) {
    const wordDisplay = window.parent.document.querySelector('.word-display');
    if (wordDisplay) {
        console.log('Triggering animation:', animationType);
        // Remove all existing animation classes
        wordDisplay.classList.remove('good-blink', 'medium-blink', 'bad-blink');
        // Force reflow to ensure class removal is processed
        void wordDisplay.offsetWidth;
        // Add the new animation class
        const animationClass = animationType + '-blink';
        wordDisplay.classList.add(animationClass);
        console.log('Animation class added:', animationClass);
        // Remove the class after animation completes (0.5s)
        setTimeout(() => {
            wordDisplay.classList.remove(animationClass);
            console.log('Animation class removed:', animationClass);
        }, 500);
    }
}

// Add click listeners to rating buttons
function addButtonListeners() {
    // Wait a bit for Streamlit to render buttons
    setTimeout(() => {
        const buttons = window.parent.document.querySelectorAll('button');
        buttons.forEach(button => {
            const buttonText = button.textContent || button.innerText;
            // Remove existing listeners to avoid duplicates
            button.removeEventListener('click', button._animationHandler);
            if (buttonText.includes('🤔 Трудно')) {
                button._animationHandler = () => triggerWordAnimation('bad');
                button.addEventListener('click', button._animationHandler);
                console.log('Added listener to Трудно button');
            } else if (buttonText.includes('😐 Средне')) {
                button._animationHandler = () => triggerWordAnimation('medium');
                button.addEventListener('click', button._animationHandler);
                console.log('Added listener to Средне button');
            } else if (buttonText.includes('🎉 Отлично')) {
                button._animationHandler = () => triggerWordAnimation('good');
                button.addEventListener('click', button._animationHandler);
                console.log('Added listener to Отлично button');
            }
        });
    }, 100);
}

// Helper function to find button by text content
function findButtonByText(text) {
    const buttons = window.parent.document.querySelectorAll('button');
    for (let button of buttons) {
        if ((button.textContent || button.innerText).includes(text)) {
            return button;
        }
    }
    return null;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Rating keys during reading
    if (window.parent.document.querySelector('.word-display')) {
        if (e.key === '1') {
            triggerWordAnimation('bad');
            const button = findButtonByText('🤔 Трудно');
            if (button) button.click();
        } else if (e.key === '2') {
            triggerWordAnimation('medium');
            const button = findButtonByText('😐 Средне');
            if (button) button.click();
        } else if (e.key === '3') {
            triggerWordAnimation('good');
            const button = findButtonByText('🎉 Отлично');
            if (button) button.click();
        } else if (e.key === 'Escape') {
            const button = findButtonByText('← Вернуться');
            if (button) button.click();
        }
    } else {
        // Selection screen shortcuts
        if (e.key >= '1' && e.key <= '9') {
            const buttons = window.parent.document.querySelectorAll('button');
            let startButtons = [];
            buttons.forEach(button => {
                if ((button.textContent || button.innerText).includes('Начать чтение')) {
                    startButtons.push(button);
                }
            });
            let index = parseInt(e.key) - 1;
            if (startButtons[index]) startButtons[index].click();
        }
    }
});

// Initialize button listeners when page loads
addButtonListeners();

// Re-add listeners on Streamlit updates
const observer = new MutationObserver(addButtonListeners);
observer.observe(window.parent.document.body, { childList: true, subtree: true });

console.log('Animation event handlers initialized');
</script>
"""


def load_phrases():
    return _load_phrases()


def save_phrases(phrases_data):
    return _save_phrases(phrases_data)


def add_new_text_to_collection(text):
    """Add new text to phrases collection"""
    logger.info(f"Adding new text to collection: '{text[:50]}...'")

    # Check if text already exists
    text_normalized = text.strip()
    for existing_phrase in st.session_state.phrases_data:
        if existing_phrase["text"].strip() == text_normalized:
            logger.warning(f"Text already exists in collection: '{text[:50]}...'")
            st.warning(f"⚠️ Текст '{text[:100]}...' уже существует в коллекции!")
            return False

    try:
        # Create new phrase object
        new_phrase = {"text": text_normalized, "is_read": False, "read_date": None}

        # Calculate complexity for the new phrase
        new_phrase["complexity"] = calculate_text_complexity_universal(
            text_normalized,
            age=st.session_state.child_age,
            include_cognitive_load=st.session_state.use_cognitive_load,
            use_children_algorithm=st.session_state.get("use_children_algorithm", True),
        )

        # Add to END of session state (no sorting here - preserve file order)
        st.session_state.phrases_data.append(new_phrase)

        # Save to file (this will add to the end of the file)
        save_phrases(st.session_state.phrases_data)

        logger.info(f"Successfully added new text to end of collection with complexity {new_phrase['complexity']:.1f}")

        # Show success message
        complexity_emoji = get_complexity_emoji(new_phrase["complexity"], st.session_state.child_age)
        st.success(f"✅ Текст добавлен в коллекцию! Сложность: {complexity_emoji} {new_phrase['complexity']:.1f}")

        # Force page refresh to show new text in correctly sorted unread column
        # This will also clear the form automatically
        st.session_state.need_rerun = True

        return True

    except Exception as e:
        logger.error(f"Error adding new text to collection: {e}")
        st.error(f"❌ Ошибка при добавлении текста: {e}")
        return False


def init_session_state():
    # Delegate to services.session
    _init_session_state()


def start_reading_session(text):
    """Initialize reading session"""
    try:
        result = process_text(text)
        if not result:
            raise ValueError("Invalid processing result")

        st.session_state.reading_state = {
            "current_level": 1,
            "levels": {
                1: {"words": result[1]["words"], "progress": 0},
                2: {"words": result[2]["words"], "progress": 0},
                3: {"words": result[3]["words"], "progress": 0},
            },
            "stats": {
                "total_words": sum(len(level["words"]) for level in result.values()),
                "good": 0,
                "medium": 0,
                "bad": 0,
            },
        }
        st.session_state.current_text = text
    except Exception as e:
        logger.error(f"Error initializing session: {str(e)}")
        st.error("Ошибка обработки текста. Пожалуйста, попробуйте другой текст.")


def handle_rating(rating):
    """Process user rating and advance progress"""
    logger.debug(f"Processing rating: {rating}")
    state = st.session_state.reading_state
    current_level = state["current_level"]
    level_data = state["levels"][current_level]

    # Update stats
    state["stats"][rating] += 1

    # Advance to next word (animation is handled by JavaScript)
    level_data["progress"] += 1

    # Check level completion
    if level_data["progress"] >= len(level_data["words"]):
        if current_level < 3:
            logger.info(f"Completed level {current_level}, advancing to level {current_level + 1}")
            state["current_level"] += 1
        else:
            # Calculate success rate
            success_rate = (state["stats"]["good"] + state["stats"]["medium"] * 0.5) / state["stats"]["total_words"]
            logger.info(f"Completed all levels. Success rate: {success_rate:.2f}")
            if success_rate >= 0.95:
                # Update phrase status
                current_text = st.session_state.current_text
                logger.info(f"Success rate >= 0.95, marking text as read: '{current_text[:50]}...'")
                for phrase in st.session_state.phrases_data:
                    if phrase["text"] == current_text:
                        old_status = phrase["is_read"]
                        phrase["is_read"] = True
                        phrase["read_date"] = datetime.now().isoformat()
                        logger.info(f"Changed phrase status from {old_status} to {phrase['is_read']} with date {phrase['read_date']}")
                        save_phrases(st.session_state.phrases_data)
                        logger.info("Successfully saved phrase status after completion")
                        break
            else:
                logger.info(f"Success rate {success_rate:.2f} < 0.95, not marking as read")


def show_text_selection():
    """Display text selection screen"""
    logger.info("Starting show_text_selection function")
    # Apply base style + optional child theme
    st.markdown(BASE_STYLE, unsafe_allow_html=True)
    if st.session_state.get("child_mode"):
        st.markdown(CHILD_STYLE, unsafe_allow_html=True)

    st.title("Тренажер чтения")

    # Check if phrases are loaded (safe)
    if not st.session_state.get("phrases_data"):
        logger.warning("No phrases_data in session state")
        st.error(f"Файл {PHRASES_FILE} не найден или пуст. Пожалуйста, создайте файл с фразами.")
        st.info(
            """
        Создайте файл `phrases.json` в корневой папке проекта со следующей структурой:
        ```json
        [
          {
            "text": "Мама мыла раму.",
            "is_read": false,
            "complexity": 18
          }
        ]
        ```
        """
        )
        return

    logger.info(f"Displaying {len(st.session_state.phrases_data)} phrases")

    tab_texts, tab_collection, tab_add, tab_quick, tab_settings = st.tabs(
        [
            "📚 Тексты",
            "📜 Коллекция",
            "➕ Добавить",
            "🚀 Быстрое чтение",
            "⚙️ Настройки",
        ]
    )

    # ============ TAB: ТЕКСТЫ ============
    with tab_texts:
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.subheader("📚 Непрочитанные тексты")

            # Search & controls
            filter_query = st.text_input("Поиск по непрочитанным", key="unread_search", placeholder="Начните вводить текст...")

            # Get unread phrases and sort by complexity for display only
            unread_phrases = [
                (idx, phrase_data) for idx, phrase_data in enumerate(st.session_state.phrases_data) if not phrase_data["is_read"]
            ]

            # Text filter
            if filter_query:
                q = filter_query.lower()
                unread_phrases = [(i, p) for i, p in unread_phrases if q in p["text"].lower()]

            # Sort unread phrases by complexity for better learning progression
            unread_phrases.sort(key=lambda x: x[1]["complexity"])

            # Limit to next N by complexity unless user wants to see all
            total_unread = len(unread_phrases)
            if st.session_state.show_all_phrases:
                display_unread_phrases = unread_phrases
            else:
                display_unread_phrases = unread_phrases[: st.session_state.phrases_limit]

            ctrl_col1, ctrl_col2 = st.columns([2, 1])
            with ctrl_col1:
                st.caption(f"Показано {len(display_unread_phrases)} из {total_unread} по возрастанию сложности")
            with ctrl_col2:
                toggle_label = "Показать все тексты" if not st.session_state.show_all_phrases else "Показать только 20"
                if st.button(toggle_label, key="toggle_show_all_unread", type="secondary", use_container_width=True):
                    st.session_state.show_all_phrases = not st.session_state.show_all_phrases
                    st.rerun()

            unread_count = 0
            for _display_idx, (original_idx, phrase_data) in enumerate(display_unread_phrases):
                unread_count += 1
                with st.container(border=True):
                    title = truncate_text(phrase_data["text"], 120)
                    complexity_emoji = get_complexity_emoji(phrase_data["complexity"], st.session_state.child_age)
                    st.markdown(
                        f"**{unread_count}. {title}**  <span class='badge'>Сложность: {complexity_emoji} {phrase_data['complexity']}</span>",
                        unsafe_allow_html=True,
                    )

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        start_key = f"unread_start_button_{original_idx}_{hash(phrase_data['text']) % 10000}"
                        st.button(
                            "Начать чтение",
                            key=start_key,
                            on_click=start_reading_session,
                            args=(phrase_data["text"],),
                            type="primary",
                            use_container_width=True,
                        )
                    with c2:
                        mark_key = f"unread_button_{original_idx}_{hash(phrase_data['text']) % 10000}"
                        if st.button("✅ Отметить как прочитанное", key=mark_key, type="secondary", use_container_width=True):
                            logger.info(f"User marked phrase as READ: '{phrase_data['text'][:50]}...' (original index: {original_idx})")
                            old_status = phrase_data["is_read"]
                            phrase_data["is_read"] = True
                            phrase_data["read_date"] = datetime.now().isoformat()
                            logger.info(
                                f"Changed phrase status from {old_status} to {phrase_data['is_read']} with date {phrase_data['read_date']}"
                            )
                            save_phrases(st.session_state.phrases_data)
                            try:
                                with open(PHRASES_FILE, encoding="utf-8") as f:
                                    saved_data = json.load(f)
                                    for saved_phrase in saved_data:
                                        if saved_phrase["text"] == phrase_data["text"]:
                                            if saved_phrase.get("is_read", False):
                                                logger.info("Verified: phrase was successfully saved as read")
                                            else:
                                                logger.error("ERROR: phrase was not saved as read!")
                                            break
                            except Exception as verify_error:
                                logger.warning(f"Could not verify save: {verify_error}")
                            logger.info("Successfully saved phrase status")
                            st.success("Текст отмечен как прочитанный! ✅")
                            st.session_state.need_rerun = True

            if len(display_unread_phrases) == 0:
                st.info("Все тексты прочитаны! 🎉")

            logger.info(f"Displayed {unread_count} unread phrases in left column")

        with col2:
            st.subheader("✅ Прочитанные тексты")
            read_phrases = [(idx, phrase_data) for idx, phrase_data in enumerate(st.session_state.phrases_data) if phrase_data["is_read"]]
            read_phrases.sort(key=lambda x: x[1].get("read_date", ""), reverse=True)
            read_count = len(read_phrases)

            for _display_idx, (idx, phrase_data) in enumerate(read_phrases):
                with st.container(border=True):
                    st.markdown(f"**{truncate_text(phrase_data['text'], 120)}**")
                    read_date_str = ""
                    if phrase_data.get("read_date"):
                        try:
                            read_date = datetime.fromisoformat(phrase_data["read_date"])
                            read_date_str = f" • Прочитано: {read_date.strftime('%d.%m.%Y %H:%M')}"
                        except ValueError:
                            read_date_str = f" • Прочитано: {phrase_data['read_date']}"
                    complexity_emoji = get_complexity_emoji(phrase_data["complexity"], st.session_state.child_age)
                    st.caption(f"Сложность: {complexity_emoji} {phrase_data['complexity']}{read_date_str}")

                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.button(
                            "Читать снова",
                            key=f"read_again_button_{idx}_{hash(phrase_data['text']) % 10000}",
                            on_click=start_reading_session,
                            args=(phrase_data["text"],),
                            type="secondary",
                            use_container_width=True,
                        )
                    with c2:
                        unique_key = f"read_button_{idx}_{hash(phrase_data['text']) % 10000}"
                        if st.button("📚 Отметить как непрочитанное", key=unique_key, type="secondary", use_container_width=True):
                            logger.info(f"User marked phrase as UNREAD: '{phrase_data['text'][:50]}...' (index: {idx})")
                            old_status = phrase_data["is_read"]
                            phrase_data["is_read"] = False
                            phrase_data["read_date"] = None
                            logger.info(f"Changed phrase status from {old_status} to {phrase_data['is_read']} and reset read_date")
                            save_phrases(st.session_state.phrases_data)
                            try:
                                with open(PHRASES_FILE, encoding="utf-8") as f:
                                    saved_data = json.load(f)
                                    for saved_phrase in saved_data:
                                        if saved_phrase["text"] == phrase_data["text"]:
                                            if not saved_phrase.get("is_read", True):
                                                logger.info("Verified: phrase was successfully saved as unread")
                                            else:
                                                logger.error("ERROR: phrase was not saved as unread!")
                                            break
                            except Exception as verify_error:
                                logger.warning(f"Could not verify save: {verify_error}")
                            logger.info("Successfully saved phrase status")
                            st.success("Текст отмечен как непрочитанный! 📚")
                            st.session_state.need_rerun = True

            if read_count == 0:
                st.info("Пока нет прочитанных текстов")

            logger.info(f"Displayed {read_count} read phrases in right column")

        st.caption("Шорткаты: в выборе — 1-9 для старта чтения. В чтении — 1: Трудно, 2: Средне, 3: Отлично, Esc: Назад.")

    # ============ TAB: КОЛЛЕКЦИЯ ============
    with tab_collection:
        query = st.text_input("Поиск по всей коллекции", key="all_texts_search", placeholder="Введите часть текста...")
        all_items = st.session_state.phrases_data
        if query:
            low_q = query.lower()
            all_items = [p for p in all_items if low_q in p["text"].lower()]
        for phrase in all_items:
            complexity_emoji = get_complexity_emoji(phrase["complexity"], st.session_state.child_age)
            status_icon = "✅" if phrase.get("is_read") else "📖"
            st.markdown(f"{status_icon} {complexity_emoji} {phrase['complexity']}: {truncate_text(phrase['text'], 140)}")

    # ============ TAB: ДОБАВИТЬ ============
    with tab_add, st.form(key="add_text_form", clear_on_submit=True):
        new_text = st.text_area("Введите новый текст для добавления в коллекцию:", height=180)
        col1, col2 = st.columns(2)
        with col1:
            save_only = st.form_submit_button("💾 Сохранить в коллекцию", use_container_width=True)
        with col2:
            save_and_start = st.form_submit_button("📖 Сохранить и начать чтение", use_container_width=True)
        if save_only or save_and_start:
            if new_text.strip():
                success = add_new_text_to_collection(new_text.strip())
                if success and save_and_start:
                    start_reading_session(new_text.strip())
            else:
                st.error("Пожалуйста, введите текст!")

    # ============ TAB: БЫСТРОЕ ЧТЕНИЕ ============
    with tab_quick, st.form(key="quick_reading_form", clear_on_submit=True):
        custom_text = st.text_area("Введите текст для чтения (без сохранения):", height=180)
        start_reading = st.form_submit_button("Начать чтение", use_container_width=True)
        if start_reading:
            if custom_text.strip():
                start_reading_session(custom_text.strip())
            else:
                st.error("Пожалуйста, введите текст!")

    # ============ TAB: НАСТРОЙКИ ============
    with tab_settings:
        st.subheader("Параметры сложности и отображения")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            new_age = st.selectbox(
                "Возраст ребенка",
                options=[6, 7, 8, 9, 10, 11],
                index=[6, 7, 8, 9, 10, 11].index(st.session_state.child_age),
                help="Возраст влияет на оценку сложности текста",
            )
            if new_age != st.session_state.child_age:
                st.session_state.child_age = new_age
                config = {
                    "child_age": st.session_state.child_age,
                    "use_cognitive_load": st.session_state.use_cognitive_load,
                    "use_children_algorithm": st.session_state.use_children_algorithm,
                }
                save_config(config)
                update_phrases_complexity()
                st.success(f"Возраст изменен на {new_age} лет. Сложность пересчитана!")
                logger.info(f"Age changed to {new_age}, complexity recalculated (file order preserved)")
                st.rerun()
        with col2:
            new_cognitive = st.checkbox(
                "Учитывать длину текста",
                value=st.session_state.use_cognitive_load,
                help="Для младших детей (6-7 лет) длина текста сильно влияет на сложность",
            )
            if new_cognitive != st.session_state.use_cognitive_load:
                st.session_state.use_cognitive_load = new_cognitive
                config = {
                    "child_age": st.session_state.child_age,
                    "use_cognitive_load": st.session_state.use_cognitive_load,
                    "use_children_algorithm": st.session_state.use_children_algorithm,
                }
                save_config(config)
                update_phrases_complexity()
                status = "включен" if new_cognitive else "выключен"
                st.success(f"Учет длины текста {status}. Сложность пересчитана!")
                logger.info(f"Cognitive load setting changed to {new_cognitive}, complexity recalculated (file order preserved)")
                st.rerun()
        with col3:
            new_algorithm = st.checkbox(
                "🆕 Детский алгоритм",
                value=st.session_state.use_children_algorithm,
                help="Улучшенный алгоритм специально для детской литературы (рекомендуется)",
            )
            if new_algorithm != st.session_state.use_children_algorithm:
                st.session_state.use_children_algorithm = new_algorithm
                config = {
                    "child_age": st.session_state.child_age,
                    "use_cognitive_load": st.session_state.use_cognitive_load,
                    "use_children_algorithm": st.session_state.use_children_algorithm,
                }
                save_config(config)
                update_phrases_complexity()
                algorithm_name = "детский (улучшенный)" if new_algorithm else "стандартный"
                st.success(f"Алгоритм изменен на {algorithm_name}. Сложность пересчитана!")
                logger.info(f"Algorithm changed to children={new_algorithm}, complexity recalculated (file order preserved)")
                st.rerun()

        st.checkbox(
            "🎨 Детский режим (крупнее кнопки, мягкие цвета)",
            key="child_mode",
            help="Делает интерфейс ещё дружелюбнее для ребёнка",
        )

        config = load_config()
        last_updated = config.get("last_updated", "Неизвестно")
        try:
            if last_updated != "Неизвестно":
                update_time = datetime.fromisoformat(last_updated)
                last_updated_str = update_time.strftime("%d.%m.%Y %H:%M")
            else:
                last_updated_str = last_updated
        except Exception:
            last_updated_str = str(last_updated)
        algorithm_name = "🆕 Детский (улучшенный)" if st.session_state.use_children_algorithm else "📚 Стандартный"
        st.info(
            f"""
        **Текущие настройки:**
        - Возраст: {st.session_state.child_age} лет
        - Учет длины текста: {'✅ Включен' if st.session_state.use_cognitive_load else '❌ Выключен'}
        - Алгоритм: {algorithm_name}
        - Последнее обновление: {last_updated_str}

        **Пороги сложности для {st.session_state.child_age} лет:**
        {get_age_thresholds_info(st.session_state.child_age)}

        **🆕 Детский алгоритм включает:**
        - Частотность букв в детской литературе
        - Анализ сложности буквосочетаний (биграммы)
        - Возрастная адаптация восприятия букв
        - Научно обоснованные коэффициенты (исследование 2022 г.)
        """
        )


def truncate_text(text, max_length):
    return text[:max_length] + "..." if len(text) > max_length else text


def show_reading_interface():
    """Display reading interface"""
    # Apply base style + optional child theme
    st.markdown(BASE_STYLE, unsafe_allow_html=True)
    if st.session_state.get("child_mode"):
        st.markdown(CHILD_STYLE, unsafe_allow_html=True)
    state = st.session_state.reading_state
    current_level = state["current_level"]
    level_data = state["levels"][current_level]

    # Progress header
    total_levels = 3
    level_progress = level_data["progress"] / len(level_data["words"])
    progress = (current_level - 1) / total_levels + level_progress / total_levels
    progress = min(progress, 1.0)

    st.progress(progress, text=f"Уровень {current_level} из {total_levels} - {LEVEL_NAMES[current_level]}")

    # Word display - simple, no animation logic (JavaScript handles it)
    if current_level <= 3 and level_data["progress"] < len(level_data["words"]):
        current_word = level_data["words"][level_data["progress"]]

        # Simple word display - JavaScript will handle all animation
        st.markdown(f'<div class="word-display">{current_word}</div>', unsafe_allow_html=True)

        # Rating buttons - large
        cols = st.columns(3)
        with cols[0]:
            st.button(
                "🤔 Трудно (1)",
                on_click=handle_rating,
                args=("bad",),
                type="secondary",
                use_container_width=True,
            )
        with cols[1]:
            st.button(
                "😐 Средне (2)",
                on_click=handle_rating,
                args=("medium",),
                type="secondary",
                use_container_width=True,
            )
        with cols[2]:
            st.button(
                "🎉 Отлично! (3)",
                on_click=handle_rating,
                args=("good",),
                type="primary",
                use_container_width=True,
            )

        # Add return button
        st.button(
            "← Вернуться к выбору текста (Esc)",
            on_click=lambda: st.session_state.update({"reading_state": None, "current_text": None}),
            type="secondary",
            use_container_width=True,
        )
    else:
        show_results()


def show_results():
    """Display final results screen"""
    # Apply base style + optional child theme
    st.markdown(BASE_STYLE, unsafe_allow_html=True)
    if st.session_state.get("child_mode"):
        st.markdown(CHILD_STYLE, unsafe_allow_html=True)
    state = st.session_state.reading_state

    st.title("Результаты обучения")

    # Summary metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Всего слов", state["stats"]["total_words"])
    with cols[1]:
        score = (state["stats"]["good"] * 1 + state["stats"]["medium"] * 0.5) / state["stats"]["total_words"] * 10
        st.metric("Общий балл", f"{score:.1f}/10")
    with cols[2]:
        st.metric("Завершено уровней", "3/3")

    # Detailed stats
    with st.expander("Подробная статистика"):
        st.subheader("Результаты по оценкам")
        rating_cols = st.columns(3)
        with rating_cols[0]:
            st.metric("🎉 Отлично", state["stats"]["good"])
        with rating_cols[1]:
            st.metric("😐 Средне", state["stats"]["medium"])
        with rating_cols[2]:
            st.metric("🤔 Трудно", state["stats"]["bad"])

        for level in range(1, 4):
            st.subheader(f"Уровень {level}: {LEVEL_NAMES[level]}")
            level_data = state["levels"][level]
            st.write(f"Прогресс: {len(level_data['words'])}/{len(level_data['words'])} слов")

    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        # Detailed complexity analysis
        with st.expander("📊 Анализ сложности текста", expanded=False):
            text = st.session_state.current_text
            breakdown = get_complexity_breakdown_universal(
                text,
                age=st.session_state.child_age,
                include_cognitive_load=st.session_state.use_cognitive_load,
                use_children_algorithm=st.session_state.use_children_algorithm,
            )

            col1, col2 = st.columns(2)

            with col1:
                algorithm_name = "🆕 Детский" if st.session_state.use_children_algorithm else "📚 Стандартный"
                st.markdown("**Общие показатели:**")
                st.write(f"📝 Слов: {breakdown['words']}")
                st.write(f"🎯 Возраст: {breakdown['age']} лет")
                st.write(f"🔧 Алгоритм: {algorithm_name}")
                st.write(f"📊 Итоговая сложность: **{breakdown['total_complexity']:.1f}**")

                # Complexity rating
                emoji = get_complexity_emoji(breakdown["total_complexity"], st.session_state.child_age)
                if emoji == "✅":
                    st.success("Идеально подходит для этого возраста!")
                elif emoji == "👍":
                    st.info("Хорошо подходит для практики")
                elif emoji == "⚠️":
                    st.warning("Может потребоваться помощь")
                else:
                    st.error("Слишком сложно для этого возраста")

            with col2:
                st.markdown("**Компоненты сложности:**")
                st.write(f"🗣️ Лингвистическая: {breakdown['linguistic_complexity']:.1f}")
                if st.session_state.use_cognitive_load:
                    st.write(f"🧠 Когнитивная нагрузка: {breakdown['cognitive_load']:.1f}")

                st.markdown("**Детализация:**")
                st.write(f"• Слоги: {breakdown['syllable_component']:.1f}")
                st.write(f"• Структура: {breakdown['structural_component']:.1f}")
                st.write(f"• Лексика: {breakdown['lexical_component']:.1f}")

                if st.session_state.use_children_algorithm:
                    st.write(f"• 🆕 Биграммы: {breakdown.get('bigram_component', 0):.1f}")
                    st.write(f"• Морфология: {breakdown['morphological_component']:.1f}")
                else:
                    st.write(f"• Морфология: {breakdown['morphological_component']:.1f}")
                    st.write(f"• Фонетика: {breakdown['phonetic_component']:.1f}")

                # Показать дополнительную информацию для детского алгоритма
                if st.session_state.use_children_algorithm and "optimization_note" in breakdown:
                    st.info(f"✨ {breakdown['optimization_note']}")

                    # Возможность сравнить с оригинальным алгоритмом
                    if st.button("🔄 Сравнить с оригинальным", key="compare_algorithms"):
                        comparison = compare_algorithms_children_vs_original(
                            text,
                            age=st.session_state.child_age,
                            include_cognitive_load=st.session_state.use_cognitive_load,
                        )
                        st.write("**Сравнение алгоритмов:**")
                        st.write(f"📚 Оригинальный: {comparison['original_algorithm']:.1f}")
                        st.write(f"🆕 Детский: {comparison['children_optimized']:.1f}")
                        st.write(f"📊 Разница: {comparison['difference']:+.1f} ({comparison['improvement_percent']:+.1f}%)")

        if st.button("Читать другой текст", type="primary", use_container_width=True):
            st.session_state.reading_state = None
            st.session_state.current_text = None
            st.rerun()


def main():
    logger.info("=== Starting main application ===")
    init_session_state()

    if st.session_state.reading_state:
        logger.info("Displaying reading interface")
        show_reading_interface()
    else:
        logger.info("Displaying text selection interface")
        show_text_selection()

    if st.session_state.need_rerun:
        st.session_state.need_rerun = False
        st.rerun()

    # Inject JS for keyboard
    st.components.v1.html(KEYBOARD_JS, height=0)

    logger.info("=== Main application completed ===")


if __name__ == "__main__":
    main()
