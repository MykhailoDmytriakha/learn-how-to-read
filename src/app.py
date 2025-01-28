import streamlit as st
import json
import logging
import os
from syllable_processor import process_text
from text_complexity import calculate_text_complexity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add this at the top of the file with other imports
READ_STATUS_FILE = "read_status.json"

# Sample phrases
SAMPLE_PHRASES = [
    "Мама мыла раму.",
    "Саша ест кашу.",
    "На реке рыбаки.",
    "Мама любит папу. Папа любит маму.",
    "Мама готовит суп. Папа читает книгу.",
    "На улице дети играют. Даниил играет в мяч.",
    "Сегодня хорошая погода. Я люблю кушать мороженое.",
    "Мы дружная семья.",
    "Наоми едет на велосипеде. Олег играет машинками. Все веселятся и смеются.",
    "Кошка пьёт молоко. Дети играют в парке. Мы любим лето.",
    "Кот спит тут.",
    "Дом высокий.",
    "Мяч летит вверх.",
    "Солнце светит ярко.",
    "Луна светит ночью.",
    "Рыба в воде.",
    "Ёж в траве.",
    "Дым идёт вверх.",
    "Мама и папа дома.",
    "Собака лает, а кот бежит.",
    "Я рисую и ты рисуешь.",
    "Бабушка вяжет шарф, а дедушка читает.",
    "Большой слон стоит в зоопарке.",
    "Красная машина едет быстро.",
    "Жёлтый цыплёнок клюёт зёрна.",
    "Вкусный суп в кастрюле.",
    "Ура! Дождь идёт!",
    "Ой! Мяч упал!",
    "Кто тут? Это я!",
    "Мама говорит: «Пора спать». Папа говорит: «Спокойной ночи».",
    "Зимой падает снег. Дети лепят снеговика.",
    "Летом жарко. Мы купаемся в речке.",
    "Утром я умываюсь. Вечером чищу зубы.",
    "Муравей нашел большое зерно. Он не мог тащить его один.",
    "Муравей позвал на помощь товарищей. Вместе муравьи легко притащили зерно в муравейник.",
    "Долго сидел я с удочкой на берегу. Не клюют у меня пескари.",
    "А дед под кустиком сидит и уже ведерко наловил. Сел и я в тени. Сразу пескари клевать стали.", 
    "Оказывается, на чистом месте тень от удочки видна. Вот и не шла к крючку хитрая рыба. ",
    "Кате дали мыло. Она мыла руки, лицо и шею. Руки, лицо и шея были белы.",
    "Папа дома и Витя дома. Не шуми, Витя, не буди папу, а сиди тихо. Люби, Витя, папу.",
    "Данил бежит быстро!", 
    "Мяч летит вверх!",
    "Играем в догонялки!",
    "Качели летят высоко.",
    "Данил смеётся громко.",
    "Собака виляет хвостом.",
    "Солнце светит ярко.",
    "Мы прыгаем на кровати.",  
    "Ведро с песком тяжёлое.",
    "Папа катит машинку.",
    "Данил строит высокую башню из кубиков.", 
    "Мы запускаем воздушного змея в парке.",
    "Горячий шарик лопнул с треском!",
    "На роликах качусь быстро-быстро!",
    "Весёлые брызги в бассейне.",  
    "Прячемся за большим деревом.",
    "Собираем пазл на полу.",
    "Сладкая клубника в корзинке.",
    "Мячик закатился под диван.",
    "Дождь! Бежим домой быстро!",
    "Данил объезжает лужи на велосипеде.", 
    "Разноцветные мелки рисуют радугу.", 
    "Весёлая гонка с друзьями во дворе.",
    "Прыжки через скакалку: раз-два-три!",
    "Строим секретную базу из одеял.",
    "Съехал с горки — ура! — в сугроб.",
    "Футбольный матч: гол забил Данилка!",
    "Прятки: кто спрятался за шторой?",
    "Мыльные пузыри летят к облакам.",
    "Пирог с яблоками пахнет вкусно.",
    "Данил играет с мячом.",
    "Дерево растёт в саду.",
    "Дождь идёт, и мы под зонтом.",
    "Дедушка рассказывает сказки.",
    "Девочка рисует на бумаге.",
    "Дорога ведёт к реке.",
    "Друзья играют в парке.",
    "Дома тепло и уютно.",
    "День солнечный и ясный.",
    "Дети смеются и играют.",
    "Мама мыла раму мыльной пеной.",
    "Саша ест горячую кашу с маслом.",
    "Рыбаки сидят с удочками на реке.",
    "Мама и папа обнимаются на кухне.",
    "Папа читает детям сказку перед сном.",
    "Даниил бросает мяч в баскетбольное кольцо.",
    "Я ем клубничное мороженое в вафельном стаканчике.",
    "Мы всей семьёй играем в настольную игру.",
    "Наоми крутит педали синего велосипеда.",
    "Пушистый кот лакает молоко из миски.",
    "Рыжий кот спит на подоконнике.",
    "Высокий дом с красной крышей стоит на горке.",
    "Мяч взлетает вверх к облакам.",
    "Яркое солнце освещает зелёное поле.",
    "Серебристая луна светит в ночном окне.",
    "Золотая рыбка плавает в круглом аквариуме.",
    "Колючий ёжик бежит через лесную тропинку.",
    "Серый дым поднимается из трубы дома.",
    "Мама печёт яблочный пирог к чаю.",
    "Собака громко лает на проезжающую машину.",
    "Я рисую радугу цветными карандашами.",
    "Бабушка вяжет тёплый шарф из шерсти.",
    "Большой слон ест сено в зоопарке.",
    "Красная гоночная машина мчится по трассе.",
    "Жёлтый цыплёнок клюёт зёрнышки во дворе.",
    "Ароматный суп с овощами стоит на плите.",
    "Дождевые капли барабанят по подоконнику.",
    "Резиновый мяч упал в лужу с брызгами.",
    "За дверью слышен весёлый смех детей.",
    "Мама зажигает ночник в детской комнате.",
    "Дети лепят снеговика с морковным носом.",
    "Мы ныряем в прохладную речную воду.",
    "Я чищу зубы пастой с мятным вкусом.",
    "Муравей тащит веточку в свой муравейник.",
    "Старик ловит серебристых пескарей на удочку.",
    "Девочка намыливает руки душистым мылом.",
    "Мальчик тихо собирает пазл на ковре.",
    "Данил бежит быстрее всех на спортивной площадке.",
    "Воздушный змей парит высоко над парком.",
    "Лопнувший шарик испугал спящего кота.",
    "Ролики громко стучат по асфальтовой дорожке.",
    "Дети прыгают в бассейн с разноцветными кругами.",
    "Мальчик прячется за толстым дубом в прятках.",
    "Корзинка с клубникой стоит на кухонном столе.",
    "Пёс радостно виляет хвостом у ворот.",
    "Мы вешаем мокрые зонтики сушиться в прихожей.",
    "Данил объезжает на велосипеде большую лужу.",
    "Дети рисуют мелом радугу на асфальте.",
    "Мальчишки играют в футбол с новым мячом.",
    "Девочка находит брата за шторой в прятках.",
    "Мыльные пузыри переливаются на солнце.",
    "Яблочный пирог румянится в духовке.",
    "Кот запрыгнул на стол за кусочком сыра.",
    "Дождевые капли танцуют на железной крыше.",
    "Бабушка ставит пирог с вишней на окошко остывать.",
    "Осенние листья кружатся в золотом вихре.",
    "Вова ловит сачком яркую бабочку.",
    "Собака бежит за мячом по мокрой траве.",
    "В ночной тишине стрекочут лесные сверчки.",
    "Алёна рисует радугу после дождя.",
    "Папа чинит проколотое велосипедное колесо.",
    "В старой коробке блестят стеклянные бусины.",
    "Утренний туман стелется над рекой.",
    "Учитель демонстрирует извержение самодельного вулкана.",
    "Альпинисты поднимаются по каменистой тропе.",
    "Ледяные сосульки сверкают на утреннем солнце.",
    "Старинная карта лежит в кожаной папке.",
    "Бумажный кораблик плывёт против течения ручья.",
    "Лягушка прыгает с листа кувшинки в пруд.",
    "Дети стучат ложками по железным кастрюлям.",
    "Снежок врезается в ствол сосны.",
    "Девочка прыгает в классики на асфальте.",
    "Муравьиная цепочка движется к сахарной крошке.",
    "В капле воды под микроскопом плавают инфузории.",
    "Северное сияние мерцает над заснеженным лесом.",
    "Учёный в очках рассматривает кусок вулканической лавы.",
    "Чёрные котяра играют с клубком шерсти.",
    "Бенгальские огни искрятся в новогоднюю ночь.",
    "Фейерверк рассыпается звёздочками над городом.",
    "Ветер гудит в печной трубе холодным вечером.",
    "Сосульки тают, капая на подоконник.",
    "Мальчик разворачивает книгу в блестящей обёртке."
]

# Сортируем фразы по сложности
SAMPLE_PHRASES = sorted(SAMPLE_PHRASES, key=lambda x: calculate_text_complexity(x))

def load_read_status():
    """Load read status from file or create new if file doesn't exist"""
    if os.path.exists(READ_STATUS_FILE):
        with open(READ_STATUS_FILE, 'r', encoding='utf-8') as f:
            read_status = json.load(f)
    else:
        read_status = {}
    
    # Ensure all phrases are in the dictionary
    for phrase in SAMPLE_PHRASES:
        if phrase not in read_status:
            read_status[phrase] = False
    
    return read_status

def save_read_status():
    """Save current read status to file"""
    with open(READ_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.read_status, f, ensure_ascii=False, indent=2)

def init_session_state():
    logger.info("Initializing session state")
    if 'current_text' not in st.session_state:
        st.session_state.current_text = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'
    if 'reading_state' not in st.session_state:
        st.session_state.reading_state = None
    if 'processed_result' not in st.session_state:
        st.session_state.processed_result = None
    if 'read_status' not in st.session_state:
        st.session_state.read_status = load_read_status()
    logger.info(f"Session state: page={st.session_state.current_page}, has_text={st.session_state.current_text is not None}")

def start_reading():
    logger.info("Starting reading mode")
    if st.session_state.reading_state is None:
        text = st.session_state.current_text
        logger.info(f"Processing text for reading: {text}")
        try:
            result = process_text(text)
            if not result or 1 not in result:
                logger.error("Invalid result format from process_text")
                st.error("Error processing text. Please try again.")
                return_to_main()
                return
                
            # Get level 1 words (syllables)
            words = result[1]['words']
            
            if not words:
                logger.error("No words found in processed text")
                st.error("No words found in the text. Please try a different text.")
                return_to_main()
                return
            
            st.session_state.reading_state = {
                'current_word': 0,
                'total_words': len(words),
                'good_reads': 0,
                'medium_reads': 0,
                'bad_reads': 0,
                'words': words,
                'level': 1
            }
            logger.info(f"Reading state initialized with {len(words)} words")
            # Set page after initializing reading state
            st.session_state.current_page = 'reading'
            st.rerun()
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            st.error("Error processing text. Please try again.")
            return_to_main()
            return

def return_to_main():
    logger.info("Returning to main")
    st.session_state.current_page = 'main'
    st.session_state.reading_state = None
    st.session_state.current_text = None
    st.session_state.processed_result = None
    st.rerun()

def process_current_text():
    logger.info("Processing text")
    if st.session_state.current_text:
        st.session_state.processed_result = process_text(st.session_state.current_text)
        logger.info("Text processed successfully")
    else:
        logger.warning("No text to process")

def rate_word(rating):
    logger.info(f"Rating word as {rating}")
    if rating == 'bad':
        st.session_state.reading_state['bad_reads'] += 1
    elif rating == 'medium':
        st.session_state.reading_state['medium_reads'] += 1
    else:
        st.session_state.reading_state['good_reads'] += 1
    st.session_state.reading_state['current_word'] += 1
    logger.info(f"Word {st.session_state.reading_state['current_word']} rated as {rating}")

def show_reading_interface():
    logger.info("Showing reading interface")
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        .big-text {
            font-size: 96px !important;
            text-align: center;
            margin: 40px 0;
            padding: 30px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            background-color: rgba(248, 249, 250, 0.8);
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }
        .stats-text {
            font-size: 18px;
            margin: 5px 0;
        }
        .centered-title {
            text-align: center;
        }
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 15px 0;
            font-size: 20px;
            font-weight: 500;
            margin: 5px 0;
            border: 1px solid;
            transition: all 0.3s ease;
        }
        .return-button > button {
            background-color: #6c757d !important;
            color: white !important;
            max-width: 300px;
            margin: 20px auto;
        }
        .rating-buttons {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }
        .stats-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<h1 class="centered-title">Уровень {st.session_state.reading_state["level"]}: Слоги</h1>', unsafe_allow_html=True)
    
    # Return button with container for centering
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="return-button">', unsafe_allow_html=True)
        if st.button("Вернуться к выбору уровня", key="return_from_reading"):
            return_to_main()
            return
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.reading_state['current_word'] >= st.session_state.reading_state['total_words']:
        show_results()
        return
    
    # Display current word in large text
    current_word = st.session_state.reading_state['words'][st.session_state.reading_state['current_word']]
    st.markdown(f'<div class="big-text">{current_word}</div>', unsafe_allow_html=True)
    
    # Container for centered buttons
    st.markdown('<div class="rating-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown('<div class="bad-button">', unsafe_allow_html=True)
        st.button("Плохо", key="bad", on_click=rate_word, args=('bad',))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="medium-button">', unsafe_allow_html=True)
        st.button("Средне", key="medium", on_click=rate_word, args=('medium',))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="good-button">', unsafe_allow_html=True)
        st.button("Хорошо", key="good", on_click=rate_word, args=('good',))
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display statistics in a centered container
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="stats-text">Плохо: {st.session_state.reading_state["bad_reads"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stats-text">Средне: {st.session_state.reading_state["medium_reads"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stats-text">Хорошо: {st.session_state.reading_state["good_reads"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Progress text
    st.markdown(
        f'<div class="stats-text" style="text-align: center;">Слово {st.session_state.reading_state["current_word"] + 1} '
        f'из {st.session_state.reading_state["total_words"]} (Уровень {st.session_state.reading_state["level"]})</div>',
        unsafe_allow_html=True
    )

def start_next_level():
    logger.info("Starting next level")
    current_level = st.session_state.reading_state['level']
    text = st.session_state.current_text
    
    try:
        result = process_text(text)
        if not result or current_level + 1 not in result:
            logger.error(f"Invalid result format for level {current_level + 1}")
            st.error("Error loading next level. Please try again.")
            return
            
        # Get words for the next level
        words = result[current_level + 1]['words']
        
        if not words:
            logger.error("No words found for next level")
            st.error("No content found for next level. Please try a different text.")
            return
        
        st.session_state.reading_state = {
            'current_word': 0,
            'total_words': len(words),
            'good_reads': 0,
            'medium_reads': 0,
            'bad_reads': 0,
            'words': words,
            'level': current_level + 1
        }
        logger.info(f"Next level {current_level + 1} initialized with {len(words)} words")
        st.rerun()
    except Exception as e:
        logger.error(f"Error starting next level: {str(e)}")
        st.error("Error loading next level. Please try again.")

def show_results():
    logger.info("Showing results screen")
    
    # Custom CSS for results screen
    st.markdown("""
        <style>
        .results-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .results-title {
            text-align: center;
            margin-bottom: 30px;
        }
        .results-stats {
            font-size: 20px;
            margin: 10px 0;
        }
        .results-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }
        .next-level-button > button {
            background-color: #007bff !important;
            color: white !important;
        }
        .next-level-button > button:hover {
            background-color: #0056b3 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="results-title">Результаты чтения</h1>', unsafe_allow_html=True)
    st.markdown(f'<h2 class="results-title">Уровень {st.session_state.reading_state["level"]}: Слоги</h2>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="results-stats">Всего слов: {st.session_state.reading_state["total_words"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="results-stats">Плохо: {st.session_state.reading_state["bad_reads"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="results-stats">Средне: {st.session_state.reading_state["medium_reads"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="results-stats">Хорошо: {st.session_state.reading_state["good_reads"]}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="results-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="return-button">', unsafe_allow_html=True)
        if st.button("Вернуться к выбору уровня", key="return_from_results"):
            return_to_main()
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        current_level = st.session_state.reading_state['level']
        if current_level < 3:  # We have 3 levels total
            next_level_name = "Слова по слогам" if current_level == 1 else "Полный текст"
            st.markdown('<div class="next-level-button">', unsafe_allow_html=True)
            if st.button(f"Перейти к уровню {current_level + 1}: {next_level_name}", key="next_level"):
                start_next_level()
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def show_main_interface():
    logger.info("Showing main interface")
    
    # Show different title based on input mode
    input_type = st.radio(
        "Choose input method:",
        ["Select from examples", "Enter custom text"],
        key="input_type"
    )
    
    if input_type == "Select from examples":
        st.title("Phrase Selection")
    else:
        st.title("Syllable Processor")

    if input_type == "Select from examples":
        # Create a table with phrases, complexity, and read status
        st.write("### Phrases List")
        
        # Create columns for the table
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write("**Phrase**")
        with col2:
            st.write("**Complexity**")
        with col3:
            st.write("**Read**")
        
        # Display each phrase with its complexity and checkbox
        for idx, phrase in enumerate(SAMPLE_PHRASES):
            cols = st.columns([3, 1, 1])
            
            with cols[0]:
                if st.button(phrase, key=f"btn_{idx}"):
                    st.session_state.current_text = phrase
                    start_reading()
                    return
            
            with cols[1]:
                complexity = calculate_text_complexity(phrase)
                st.write(f"{complexity}%")
            
            with cols[2]:
                # Update session state and save to file when checkbox changes
                new_value = st.checkbox(
                    "Read", 
                    value=st.session_state.read_status[phrase],
                    key=f"chk_{idx}",
                    label_visibility="collapsed"
                )
                if new_value != st.session_state.read_status[phrase]:
                    st.session_state.read_status[phrase] = new_value
                    save_read_status()
    else:
        st.session_state.current_text = st.text_area(
            "Enter your text:", 
            height=100,
            key="text_input"
        )
        
        # Show Process Text button only in custom text mode
        if st.button("Process Text", key="process"):
            process_current_text()

    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.current_text:  # Only show Read button if there's text
            if st.button("Read the text", key="start_reading"):
                logger.info("Starting reading mode")
                start_reading()
        
    # Show results if text was processed
    if st.session_state.processed_result is not None:
        st.subheader("Results")
        json_str = json.dumps(st.session_state.processed_result, ensure_ascii=False, indent=2)
        st.code(json_str, language="json")
        
        if st.button("Copy to Clipboard", key="copy"):
            st.write(
                f'<script>navigator.clipboard.writeText({json.dumps(json_str)})</script>',
                unsafe_allow_html=True
            )

    st.markdown("""
        <style>
        .phrase-table {
            max-height: 500px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .phrase-row {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .phrase-row:hover {
            background-color: #f5f5f5;
        }
        .phrase-button {
            background: none;
            border: none;
            color: #1f6feb;
            cursor: pointer;
            text-align: left;
            padding: 0;
        }
        .phrase-button:hover {
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    logger.info("Application starting")
    st.set_page_config(page_title="Syllable Processor", layout="wide")
    init_session_state()
    
    logger.info(f"Current page: {st.session_state.current_page}")
    if st.session_state.current_page == 'reading':
        show_reading_interface()
    else:
        show_main_interface()

if __name__ == "__main__":
    main() 