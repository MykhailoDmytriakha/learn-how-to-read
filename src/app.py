import streamlit as st
import json
import logging
import os
from datetime import datetime
from syllable_processor import process_text
from text_complexity_improved import (
    calculate_text_complexity_improved,
    calculate_complexity_for_age,
    get_complexity_breakdown
)

# Set page config for wide layout
st.set_page_config(layout="wide")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Add this at the top of the file with other imports
PHRASES_FILE = "phrases.json"
CONFIG_FILE = "config.json"

LEVEL_NAMES = {
    1: "Слоги",
    2: "Слова по слогам",
    3: "Полный текст"
}

def get_age_thresholds_info(age):
    """Return formatted threshold information for the given age"""
    thresholds = {
        6: "✅ 0-20: Идеально | 👍 20-30: Хорошо | ⚠️ 30-40: Сложно | ❌ 40+: Очень сложно",
        7: "✅ 0-25: Идеально | 👍 25-35: Хорошо | ⚠️ 35-45: Сложно | ❌ 45+: Очень сложно", 
        8: "✅ 0-25: Идеально | 👍 25-35: Хорошо | ⚠️ 35-45: Сложно | ❌ 45+: Очень сложно",
        9: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно",
        10: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно",
        11: "✅ 0-30: Идеально | 👍 30-40: Хорошо | ⚠️ 40-50: Сложно | ❌ 50+: Очень сложно"
    }
    return thresholds.get(age, thresholds[8])

def get_complexity_emoji(complexity, age):
    """Return emoji based on complexity score and age"""
    if age <= 6:
        if complexity <= 20: return "✅"
        elif complexity <= 30: return "👍"
        elif complexity <= 40: return "⚠️"
        else: return "❌"
    elif age <= 8:
        if complexity <= 25: return "✅"
        elif complexity <= 35: return "👍"  
        elif complexity <= 45: return "⚠️"
        else: return "❌"
    else:  # 9+
        if complexity <= 30: return "✅"
        elif complexity <= 40: return "👍"
        elif complexity <= 50: return "⚠️"
        else: return "❌"

def load_config():
    """Load configuration from config file"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"Configuration loaded from {CONFIG_FILE}")
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load config from {CONFIG_FILE}: {e}")
        # Return default configuration
        default_config = {
            "child_age": 8,
            "use_cognitive_load": True,
            "last_updated": datetime.now().isoformat()
        }
        save_config(default_config)
        return default_config

def save_config(config):
    """Save configuration to config file"""
    try:
        config["last_updated"] = datetime.now().isoformat()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Could not save config to {CONFIG_FILE}: {e}")

def update_phrases_complexity():
    """Update complexity for all phrases (no sorting - preserve original order)"""
    if not st.session_state.phrases_data:
        return
    
    logger.info("Updating complexity for all phrases (preserving original file order)")
    
    # Recalculate complexity for all phrases
    for phrase in st.session_state.phrases_data:
        phrase['complexity'] = calculate_text_complexity_improved(
            phrase['text'], 
            age=st.session_state.child_age,
            include_cognitive_load=st.session_state.use_cognitive_load
        )
    
    # No sorting here - file order is preserved like a database
    # UI will sort for display purposes only
    
    logger.info("Complexity updated (file order preserved)")

STYLE = """
<style>
/* Target the specific button structure */
button[data-testid="stBaseButton-primary"] {
    background-color: #76c893 !important;
    border-color: #76c893 !important;
    color: white !important;
    transition: all 0.3s ease !important;
    font-size: 1.2rem !important;
    padding: 1rem !important;
    height: auto !important;
}

button[data-testid="stBaseButton-primary"]:hover {
    background-color: #5a9c6f !important;
    border-color: #5a9c6f !important;
}

button[data-testid="stBaseButton-secondary"] {
    font-size: 1.2rem !important;
    padding: 1rem !important;
    height: auto !important;
}

/* Target the button's inner div */
button > div {
    color: inherit !important;
}

/* Add focus state */
button:focus {
    box-shadow: 0 0 0 0.2rem rgba(118, 200, 147, 0.5) !important;
    outline: none !important;
}

/* Card styling */
.stContainer {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.2s;
    font-size: 1.1rem;
}
.stContainer:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Progress bar */
.stProgress > div > div > div > div {
    background-color: #4CAF50 !important;
}

/* Word display base */
.word-display {
    font-size: 96px;
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 15px;
}

/* Blink animations for each rating */
.word-display.bad-blink {
    animation: badBlink 0.5s ease-in-out forwards;
}

.word-display.medium-blink {
    animation: mediumBlink 0.5s ease-in-out forwards;
}

.word-display.good-blink {
    animation: goodBlink 0.5s ease-in-out forwards;
}

@keyframes badBlink {
    0% { background-color: #f8f9fa; }
    50% { background-color: #ffcccc; } /* Light red */
    100% { background-color: #f8f9fa; }
}

@keyframes mediumBlink {
    0% { background-color: #f8f9fa; }
    50% { background-color: #fffbcc; } /* Light yellow */
    100% { background-color: #f8f9fa; }
}

@keyframes goodBlink {
    0% { background-color: #f8f9fa; }
    50% { background-color: #ccffcc; } /* Light green */
    100% { background-color: #f8f9fa; }
}

/* Responsive columns - wider and adaptive */
@media (max-width: 768px) {
    [data-testid="column"] {
        width: 100% !important;
        margin-bottom: 2rem !important;
        padding: 0 0.5rem !important;
    }
    .stButton > button {
        font-size: 1.5rem !important;
        padding: 1.5rem !important;
    }
    .word-display {
        font-size: 72px !important; /* Smaller for mobile */
    }
}

@media (min-width: 769px) and (max-width: 1200px) {
    [data-testid="column"] {
        width: calc(50% - 1rem) !important;
        margin: 0 0.5rem !important;
    }
}

@media (min-width: 1201px) {
    [data-testid="column"] {
        width: calc(50% - 3rem) !important;
        margin: 0 1.5rem !important;
    }
}

/* Improve spacing */
main {
    max-width: 95% !important;
    margin: 0 auto !important;
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
    """Load phrases from file only"""
    logger.info(f"Starting to load phrases from {PHRASES_FILE}")
    
    if not os.path.exists(PHRASES_FILE):
        logger.error(f"File {PHRASES_FILE} not found. Please create it with phrases data.")
        st.error(f"Файл {PHRASES_FILE} не найден. Пожалуйста, создайте его с данными фраз.")
        return []
    
    try:
        logger.info(f"Opening file {PHRASES_FILE} for reading")
        with open(PHRASES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Successfully loaded {len(data)} phrases from JSON file")
        
        # Ensure all phrases have required fields and ALWAYS calculate complexity
        read_count = 0
        unread_count = 0
        for i, phrase in enumerate(data):
            if 'text' not in phrase:
                phrase['text'] = phrase.get('phrase', '')  # Backward compatibility
                logger.debug(f"Phrase {i}: Added missing 'text' field")
            
            if 'is_read' not in phrase:
                phrase['is_read'] = False
                logger.debug(f"Phrase {i}: Added missing 'is_read' field as False")
            
            # Ensure is_read is boolean
            if isinstance(phrase['is_read'], str):
                old_value = phrase['is_read']
                phrase['is_read'] = phrase['is_read'].lower() == 'true'
                logger.debug(f"Phrase {i}: Converted 'is_read' from string '{old_value}' to boolean {phrase['is_read']}")
            
            # Add read_date field if missing
            if 'read_date' not in phrase:
                if phrase['is_read']:
                    # For existing read phrases, set current date
                    phrase['read_date'] = datetime.now().isoformat()
                    logger.debug(f"Phrase {i}: Added read_date for existing read phrase")
                else:
                    phrase['read_date'] = None
                    logger.debug(f"Phrase {i}: Added read_date as None for unread phrase")
            
            # Count read/unread
            if phrase['is_read']:
                read_count += 1
            else:
                unread_count += 1
            
            # ALWAYS calculate complexity using current settings
            phrase['complexity'] = calculate_text_complexity_improved(
                phrase['text'], 
                age=st.session_state.get('child_age', 8),
                include_cognitive_load=st.session_state.get('use_cognitive_load', True)
            )
        
        # Do NOT sort here - preserve original file order
        # Sorting will be done in UI for display purposes only
        
        logger.info(f"Processed {len(data)} phrases: {read_count} read, {unread_count} unread")
        logger.info(f"Successfully loaded and processed phrases from {PHRASES_FILE} (preserving original order)")
        return data
        
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading {PHRASES_FILE}: {e}")
        st.error(f"Ошибка чтения файла {PHRASES_FILE}: {e}")
        return []

def save_phrases(phrases_data):
    """Save phrases to file"""
    logger.info(f"Starting to save {len(phrases_data)} phrases to {PHRASES_FILE}")
    
    try:
        # Create a copy of phrases_data without complexity field for saving
        phrases_to_save = []
        read_count = 0
        unread_count = 0
        
        for i, phrase in enumerate(phrases_data):
            phrase_copy = {k: v for k, v in phrase.items() if k != 'complexity'}
            phrases_to_save.append(phrase_copy)
            
            # Count read/unread for logging
            if phrase.get('is_read', False):
                read_count += 1
            else:
                unread_count += 1
        
        logger.info(f"Prepared {len(phrases_to_save)} phrases for saving: {read_count} read, {unread_count} unread")
        
        logger.info(f"Opening file {PHRASES_FILE} for writing")
        with open(PHRASES_FILE, 'w', encoding='utf-8') as f:
            json.dump(phrases_to_save, f, ensure_ascii=False, indent=2)
            logger.debug(f"JSON data written to file")
            
            f.flush()  # Force write to disk
            logger.debug(f"File flushed to disk")
            
            os.fsync(f.fileno())  # Force sync to disk
            logger.debug(f"File synced to disk")
        
        logger.info(f"Successfully saved {len(phrases_to_save)} phrases to {PHRASES_FILE}")
        logger.info(f"Saved data summary: {read_count} read, {unread_count} unread phrases")
        
        # Verify the save by reading back the file
        try:
            with open(PHRASES_FILE, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            logger.info(f"Verified save: read back {len(saved_data)} phrases from file")
        except Exception as verify_error:
            logger.warning(f"Could not verify save: {verify_error}")
        
    except Exception as e:
        logger.error(f"Error saving phrases to {PHRASES_FILE}: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        st.error(f"Ошибка сохранения данных: {e}")

def add_new_text_to_collection(text):
    """Add new text to phrases collection"""
    logger.info(f"Adding new text to collection: '{text[:50]}...'")
    
    # Check if text already exists
    text_normalized = text.strip()
    for existing_phrase in st.session_state.phrases_data:
        if existing_phrase['text'].strip() == text_normalized:
            logger.warning(f"Text already exists in collection: '{text[:50]}...'")
            st.warning(f"⚠️ Текст '{text[:100]}...' уже существует в коллекции!")
            return False
    
    try:
        # Create new phrase object
        new_phrase = {
            'text': text_normalized,
            'is_read': False,
            'read_date': None
        }
        
        # Calculate complexity for the new phrase
        new_phrase['complexity'] = calculate_text_complexity_improved(
            text_normalized,
            age=st.session_state.child_age,
            include_cognitive_load=st.session_state.use_cognitive_load
        )
        
        # Add to END of session state (no sorting here - preserve file order)
        st.session_state.phrases_data.append(new_phrase)
        
        # Save to file (this will add to the end of the file)
        save_phrases(st.session_state.phrases_data)
        
        logger.info(f"Successfully added new text to end of collection with complexity {new_phrase['complexity']:.1f}")
        
        # Show success message
        complexity_emoji = get_complexity_emoji(new_phrase['complexity'], st.session_state.child_age)
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
    """Initialize session state variables"""
    logger.info("Initializing session state")
    
    if 'current_text' not in st.session_state:
        st.session_state.current_text = None
        logger.debug("Initialized current_text as None")
    
    if 'reading_state' not in st.session_state:
        st.session_state.reading_state = None
        logger.debug("Initialized reading_state as None")
    
    if 'processed_result' not in st.session_state:
        st.session_state.processed_result = None
        logger.debug("Initialized processed_result as None")
    
    if 'need_rerun' not in st.session_state:
        st.session_state.need_rerun = False
        logger.debug("Initialized need_rerun as False")
    
    # Initialize age settings for complexity calculation from config file
    if 'child_age' not in st.session_state or 'use_cognitive_load' not in st.session_state:
        config = load_config()
        st.session_state.child_age = config.get('child_age', 8)
        st.session_state.use_cognitive_load = config.get('use_cognitive_load', True)
        logger.info(f"Initialized settings from config: age={st.session_state.child_age}, cognitive_load={st.session_state.use_cognitive_load}")
    
    # CRITICAL FIX: Only load phrases_data if it doesn't exist in session state
    # This prevents reloading data on every rerun and preserves user changes
    if 'phrases_data' not in st.session_state:
        logger.info("Loading phrases_data for the first time")
        st.session_state.phrases_data = load_phrases()
        logger.info(f"Loaded {len(st.session_state.phrases_data)} phrases into session state")
    elif not st.session_state.phrases_data:
        logger.info("phrases_data is empty, reloading")
        st.session_state.phrases_data = load_phrases()
        logger.info(f"Reloaded {len(st.session_state.phrases_data)} phrases into session state")
    else:
        logger.debug(f"phrases_data already exists with {len(st.session_state.phrases_data)} phrases")
        logger.debug("Keeping existing session state data to preserve user changes")
    
    logger.info("Session state initialization completed")

def start_reading_session(text):
    """Initialize reading session"""
    try:
        result = process_text(text)
        if not result:
            raise ValueError("Invalid processing result")
            
        st.session_state.reading_state = {
            'current_level': 1,
            'levels': {
                1: {'words': result[1]['words'], 'progress': 0},
                2: {'words': result[2]['words'], 'progress': 0},
                3: {'words': result[3]['words'], 'progress': 0}
            },
            'stats': {
                'total_words': sum(len(level['words']) for level in result.values()),
                'good': 0,
                'medium': 0,
                'bad': 0
            }
        }
        st.session_state.current_text = text
    except Exception as e:
        logger.error(f"Error initializing session: {str(e)}")
        st.error("Ошибка обработки текста. Пожалуйста, попробуйте другой текст.")

def handle_rating(rating):
    """Process user rating and advance progress"""
    logger.debug(f"Processing rating: {rating}")
    state = st.session_state.reading_state
    current_level = state['current_level']
    level_data = state['levels'][current_level]
    
    # Update stats
    state['stats'][rating] += 1
    
    # Advance to next word (animation is handled by JavaScript)
    level_data['progress'] += 1
    
    # Check level completion
    if level_data['progress'] >= len(level_data['words']):
        if current_level < 3:
            logger.info(f"Completed level {current_level}, advancing to level {current_level + 1}")
            state['current_level'] += 1
        else:
            # Calculate success rate
            success_rate = (state['stats']['good'] + state['stats']['medium'] * 0.5) / state['stats']['total_words']
            logger.info(f"Completed all levels. Success rate: {success_rate:.2f}")
            if success_rate >= 0.95:
                # Update phrase status
                current_text = st.session_state.current_text
                logger.info(f"Success rate >= 0.95, marking text as read: '{current_text[:50]}...'")
                for phrase in st.session_state.phrases_data:
                    if phrase['text'] == current_text:
                        old_status = phrase['is_read']
                        phrase['is_read'] = True
                        phrase['read_date'] = datetime.now().isoformat()
                        logger.info(f"Changed phrase status from {old_status} to {phrase['is_read']} with date {phrase['read_date']}")
                        save_phrases(st.session_state.phrases_data)
                        logger.info("Successfully saved phrase status after completion")
                        break
            else:
                logger.info(f"Success rate {success_rate:.2f} < 0.95, not marking as read")

def show_text_selection():
    """Display text selection screen"""
    logger.info("Starting show_text_selection function")
    st.markdown(STYLE, unsafe_allow_html=True)
    
    st.title("Тренажер чтения")
    
    # Check if phrases are loaded
    if not st.session_state.phrases_data:
        logger.warning("No phrases_data in session state")
        st.error(f"Файл {PHRASES_FILE} не найден или пуст. Пожалуйста, создайте файл с фразами.")
        st.info("""
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
        """)
        return
    
    logger.info(f"Displaying {len(st.session_state.phrases_data)} phrases")
    
    # Settings section
    with st.expander("⚙️ Настройки сложности", expanded=False):
        col_age, col_cognitive = st.columns([1, 1])
        
        with col_age:
            new_age = st.selectbox(
                "Возраст ребенка",
                options=[6, 7, 8, 9, 10, 11],
                index=[6, 7, 8, 9, 10, 11].index(st.session_state.child_age),
                help="Возраст влияет на оценку сложности текста"
            )
            
            if new_age != st.session_state.child_age:
                st.session_state.child_age = new_age
                
                # Save configuration to file
                config = {
                    "child_age": st.session_state.child_age,
                    "use_cognitive_load": st.session_state.use_cognitive_load
                }
                save_config(config)
                
                # Update complexity (preserve file order)
                update_phrases_complexity()
                
                st.success(f"Возраст изменен на {new_age} лет. Сложность пересчитана!")
                logger.info(f"Age changed to {new_age}, complexity recalculated (file order preserved)")
                st.rerun()  # Rerun to show updated complexity values
        
        with col_cognitive:
            new_cognitive = st.checkbox(
                "Учитывать длину текста",
                value=st.session_state.use_cognitive_load,
                help="Для младших детей (6-7 лет) длина текста сильно влияет на сложность"
            )
            
            if new_cognitive != st.session_state.use_cognitive_load:
                st.session_state.use_cognitive_load = new_cognitive
                
                # Save configuration to file
                config = {
                    "child_age": st.session_state.child_age,
                    "use_cognitive_load": st.session_state.use_cognitive_load
                }
                save_config(config)
                
                # Update complexity (preserve file order)
                update_phrases_complexity()
                
                status = "включен" if new_cognitive else "выключен"
                st.success(f"Учет длины текста {status}. Сложность пересчитана!")
                logger.info(f"Cognitive load setting changed to {new_cognitive}, complexity recalculated (file order preserved)")
                st.rerun()  # Rerun to show updated complexity values
        
        # Show current settings info
        config = load_config()
        last_updated = config.get('last_updated', 'Неизвестно')
        try:
            if last_updated != 'Неизвестно':
                update_time = datetime.fromisoformat(last_updated)
                last_updated_str = update_time.strftime('%d.%m.%Y %H:%M')
            else:
                last_updated_str = last_updated
        except:
            last_updated_str = last_updated
            
        st.info(f"""
        **Текущие настройки:**
        - Возраст: {st.session_state.child_age} лет
        - Учет длины текста: {'✅ Включен' if st.session_state.use_cognitive_load else '❌ Выключен'}
        - Последнее обновление: {last_updated_str}
        
        **Пороги сложности для {st.session_state.child_age} лет:**
        {get_age_thresholds_info(st.session_state.child_age)}
        """)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📚 Непрочитанные тексты")
        
        # Get unread phrases and sort by complexity for display only
        unread_phrases = [
            (idx, phrase_data) for idx, phrase_data in enumerate(st.session_state.phrases_data)
            if not phrase_data['is_read']
        ]
        
        # Sort unread phrases by complexity for better learning progression
        unread_phrases.sort(key=lambda x: x[1]['complexity'])
        
        unread_count = 0
        unread_buttons = []  # Для шорткатов
        
        for display_idx, (original_idx, phrase_data) in enumerate(unread_phrases):
            unread_count += 1
            with st.container():
                st.markdown(f"**{unread_count}. {truncate_text(phrase_data['text'], 100)}**")
                complexity_emoji = get_complexity_emoji(phrase_data['complexity'], st.session_state.child_age)
                st.caption(f"Сложность: {complexity_emoji} {phrase_data['complexity']}")
                
                unique_key = f"unread_button_{original_idx}_{hash(phrase_data['text']) % 10000}"
                
                if st.button(
                    "✅ Отметить как прочитанное",
                    key=unique_key,
                    type="secondary",
                    use_container_width=True
                ):
                    logger.info(f"User marked phrase as READ: '{phrase_data['text'][:50]}...' (original index: {original_idx})")
                    old_status = phrase_data['is_read']
                    phrase_data['is_read'] = True
                    phrase_data['read_date'] = datetime.now().isoformat()
                    logger.info(f"Changed phrase status from {old_status} to {phrase_data['is_read']} with date {phrase_data['read_date']}")
                    
                    save_phrases(st.session_state.phrases_data)
                    
                    try:
                        with open(PHRASES_FILE, 'r', encoding='utf-8') as f:
                            saved_data = json.load(f)
                            for saved_phrase in saved_data:
                                if saved_phrase['text'] == phrase_data['text']:
                                    if saved_phrase.get('is_read', False):
                                        logger.info("Verified: phrase was successfully saved as read")
                                    else:
                                        logger.error("ERROR: phrase was not saved as read!")
                                    break
                    except Exception as verify_error:
                        logger.warning(f"Could not verify save: {verify_error}")
                    
                    logger.info("Successfully saved phrase status")
                    st.success("Текст отмечен как прочитанный! ✅")
                    st.session_state.need_rerun = True
                
                start_button = st.button(
                    "Начать чтение",
                    key=f"unread_start_button_{original_idx}_{hash(phrase_data['text']) % 10000}",
                    on_click=start_reading_session,
                    args=(phrase_data['text'],),
                    type="primary",
                    use_container_width=True
                )
                unread_buttons.append(start_button)
        
        if unread_count == 0:
            st.info("Все тексты прочитаны! 🎉")
        
        logger.info(f"Displayed {unread_count} unread phrases in left column")
    
    with col2:
        st.subheader("✅ Прочитанные тексты")
        
        # Get read phrases and sort by read_date (newest first)
        read_phrases = [
            (idx, phrase_data) for idx, phrase_data in enumerate(st.session_state.phrases_data)
            if phrase_data['is_read']
        ]
        
        # Sort by read_date (newest first), handle None values
        read_phrases.sort(
            key=lambda x: x[1].get('read_date', ''), 
            reverse=True
        )
        
        read_count = len(read_phrases)
        
        for display_idx, (idx, phrase_data) in enumerate(read_phrases):
            with st.container():
                # Display phrase text
                st.markdown(f"**{truncate_text(phrase_data['text'], 100)}**")
                
                # Display complexity and read date
                read_date_str = ""
                if phrase_data.get('read_date'):
                    try:
                        read_date = datetime.fromisoformat(phrase_data['read_date'])
                        read_date_str = f" • Прочитано: {read_date.strftime('%d.%m.%Y %H:%M')}"
                    except ValueError:
                        read_date_str = f" • Прочитано: {phrase_data['read_date']}"
                
                complexity_emoji = get_complexity_emoji(phrase_data['complexity'], st.session_state.child_age)
                st.caption(f"Сложность: {complexity_emoji} {phrase_data['complexity']}{read_date_str}")
                
                unique_key = f"read_button_{idx}_{hash(phrase_data['text']) % 10000}"
                
                if st.button(
                    "📚 Отметить как непрочитанное",
                    key=unique_key,
                    type="secondary",
                    use_container_width=True
                ):
                    logger.info(f"User marked phrase as UNREAD: '{phrase_data['text'][:50]}...' (index: {idx})")
                    old_status = phrase_data['is_read']
                    phrase_data['is_read'] = False
                    phrase_data['read_date'] = None
                    logger.info(f"Changed phrase status from {old_status} to {phrase_data['is_read']} and reset read_date")
                    
                    save_phrases(st.session_state.phrases_data)
                    
                    try:
                        with open(PHRASES_FILE, 'r', encoding='utf-8') as f:
                            saved_data = json.load(f)
                            for saved_phrase in saved_data:
                                if saved_phrase['text'] == phrase_data['text']:
                                    if not saved_phrase.get('is_read', True):
                                        logger.info("Verified: phrase was successfully saved as unread")
                                    else:
                                        logger.error("ERROR: phrase was not saved as unread!")
                                    break
                    except Exception as verify_error:
                        logger.warning(f"Could not verify save: {verify_error}")
                    
                    logger.info("Successfully saved phrase status")
                    st.success("Текст отмечен как непрочитанный! 📚")
                    st.session_state.need_rerun = True
                
                st.button(
                    "Читать снова",
                    key=f"read_again_button_{idx}_{hash(phrase_data['text']) % 10000}",
                    on_click=start_reading_session,
                    args=(phrase_data['text'],),
                    type="secondary",
                    use_container_width=True
                )
        
        if read_count == 0:
            st.info("Пока нет прочитанных текстов")
        
        logger.info(f"Displayed {read_count} read phrases in right column")
    
    logger.info(f"show_text_selection completed: {unread_count} unread, {read_count} read phrases")
    
    # Add new text section
    st.divider()
    with st.expander("➕ Добавить новый текст в коллекцию", expanded=False):
        with st.form(key="add_text_form", clear_on_submit=True):
            new_text = st.text_area("Введите новый текст для добавления в коллекцию:", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                save_only = st.form_submit_button("💾 Сохранить в коллекцию", use_container_width=True)
            
            with col2:
                save_and_start = st.form_submit_button("📖 Сохранить и начать чтение", use_container_width=True)
            
            # Handle form submissions
            if save_only or save_and_start:
                if new_text.strip():
                    success = add_new_text_to_collection(new_text.strip())
                    if success and save_and_start:
                        start_reading_session(new_text.strip())
                else:
                    st.error("Пожалуйста, введите текст!")
    
    # Custom text input for immediate reading
    with st.expander("🚀 Быстрое чтение (без сохранения)", expanded=False):
        with st.form(key="quick_reading_form", clear_on_submit=True):
            custom_text = st.text_area("Введите текст для чтения:", height=150)
            start_reading = st.form_submit_button("Начать чтение", use_container_width=True)
            
            if start_reading:
                if custom_text.strip():
                    start_reading_session(custom_text.strip())
                else:
                    st.error("Пожалуйста, введите текст!")

    # Info about shortcuts
    st.info("Шорткаты: В выборе — цифры 1-9 для старта чтения. В чтении — 1: Трудно, 2: Средне, 3: Отлично, Esc: Назад.")

def truncate_text(text, max_length):
    return text[:max_length] + "..." if len(text) > max_length else text

def show_reading_interface():
    """Display reading interface"""
    st.markdown(STYLE, unsafe_allow_html=True)
    state = st.session_state.reading_state
    current_level = state['current_level']
    level_data = state['levels'][current_level]
    
    # Progress header
    total_levels = 3
    level_progress = level_data['progress'] / len(level_data['words'])
    progress = (current_level - 1) / total_levels + level_progress / total_levels
    progress = min(progress, 1.0)
    
    st.progress(progress, text=f"Уровень {current_level} из {total_levels} - {LEVEL_NAMES[current_level]}")
    
    # Word display - simple, no animation logic (JavaScript handles it)
    if current_level <= 3 and level_data['progress'] < len(level_data['words']):
        current_word = level_data['words'][level_data['progress']]
        
        # Simple word display - JavaScript will handle all animation
        st.markdown(
            f'<div class="word-display">{current_word}</div>', 
            unsafe_allow_html=True
        )
        
        # Rating buttons - large
        cols = st.columns(3)
        with cols[0]:
            st.button("🤔 Трудно (1)", 
                     on_click=handle_rating, args=('bad',), 
                     type="secondary", 
                     use_container_width=True)
        with cols[1]:
            st.button("😐 Средне (2)", 
                     on_click=handle_rating, args=('medium',), 
                     type="secondary",
                     use_container_width=True)
        with cols[2]:
            st.button("🎉 Отлично! (3)", 
                     on_click=handle_rating, args=('good',), 
                     type="primary",
                     use_container_width=True)
        
        # Add return button
        st.button("← Вернуться к выбору текста (Esc)", 
                 on_click=lambda: st.session_state.update({'reading_state': None, 'current_text': None}),
                 type="secondary",
                 use_container_width=True)
    else:
        show_results()

def show_results():
    """Display final results screen"""
    st.markdown(STYLE, unsafe_allow_html=True)
    state = st.session_state.reading_state
    
    st.title("Результаты обучения")
    
    # Summary metrics
    cols = st.columns(3)
    with cols[0]:
        st.metric("Всего слов", state['stats']['total_words'])
    with cols[1]:
        score = (state['stats']['good'] * 1 + state['stats']['medium'] * 0.5) / state['stats']['total_words'] * 10
        st.metric("Общий балл", f"{score:.1f}/10")
    with cols[2]:
        st.metric("Завершено уровней", "3/3")
    
    # Detailed stats
    with st.expander("Подробная статистика"):
        st.subheader("Результаты по оценкам")
        rating_cols = st.columns(3)
        with rating_cols[0]:
            st.metric("🎉 Отлично", state['stats']['good'])
        with rating_cols[1]:
            st.metric("😐 Средне", state['stats']['medium'])
        with rating_cols[2]:
            st.metric("🤔 Трудно", state['stats']['bad'])
        
        for level in range(1, 4):
            st.subheader(f"Уровень {level}: {LEVEL_NAMES[level]}")
            level_data = state['levels'][level]
            st.write(f"Прогресс: {len(level_data['words'])}/{len(level_data['words'])} слов")
    
    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        # Detailed complexity analysis
        with st.expander("📊 Анализ сложности текста", expanded=False):
            text = st.session_state.current_text
            breakdown = get_complexity_breakdown(
                text, 
                age=st.session_state.child_age,
                include_cognitive_load=st.session_state.use_cognitive_load
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Общие показатели:**")
                st.write(f"📝 Слов: {breakdown['words']}")
                st.write(f"🎯 Возраст: {breakdown['age']} лет")
                st.write(f"📊 Итоговая сложность: **{breakdown['total_complexity']:.1f}**")
                
                # Complexity rating
                emoji = get_complexity_emoji(breakdown['total_complexity'], st.session_state.child_age)
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
                st.write(f"• Морфология: {breakdown['morphological_component']:.1f}")
                st.write(f"• Фонетика: {breakdown['phonetic_component']:.1f}")
        
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