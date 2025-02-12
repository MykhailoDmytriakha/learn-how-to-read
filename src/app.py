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
    "Мальчик разворачивает книгу в блестящей обёртке.",
    "Тётя дала Тане вкусный торт.",
    "Дима и Таня идут домой.",
    "У дома стоит большой дуб.",
    "Дед тихо читает детям книгу.",
    "Таня гладит кота по спине.",
    "Дети едят сладкие спелые фрукты.",
    "Дядя Толя водит красный автобус.",
    "Тома и Дима рисуют дом.",
    "Даша дарит Тане красивый цветок.",
    "Тигр в клетке громко рычит.",
    "Дождь стучит по крыше дома.",
    "Тётя Даша делает вкусный суп.",
    "Дети гуляют в тёплый день.",
    "Таня и Дима играют мячом.",
    "У Димы есть добрый кот.",
    "Тоня ест сладкую спелую дыню.",
    "Дед и внук идут гулять.",
    "Таня моет руки тёплой водой.",
    "Дима держит в руке карандаш.",
    "Тётя и дядя едут домой."
]

LEVEL_NAMES = {
    1: "Слоги",
    2: "Слова по слогам",
    3: "Полный текст"
}

# Сортируем фразы по сложности
SAMPLE_PHRASES = sorted(SAMPLE_PHRASES, key=lambda x: calculate_text_complexity(x))

STYLE = """
<style>
/* Target the specific button structure */
button[data-testid="stBaseButton-primary"] {
    background-color: #76c893 !important;
    border-color: #76c893 !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

button[data-testid="stBaseButton-primary"]:hover {
    background-color: #5a9c6f !important;
    border-color: #5a9c6f !important;
}

/* Target the button's inner div */
button[data-testid="stBaseButton-primary"] > div {
    color: white !important;
}

/* Add focus state */
button[data-testid="stBaseButton-primary"]:focus {
    box-shadow: 0 0 0 0.2rem rgba(118, 200, 147, 0.5) !important;
    outline: none !important;
}

/* Card styling */
.phrase-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.2s;
}
.phrase-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Progress bar */
.stProgress > div > div > div > div {
    background-color: #4CAF50 !important;
}

/* Word display */
.word-display {
    font-size: 96px;
    text-align: center;
    margin: 3rem 0;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 15px;
}

/* Rating buttons */
.rating-button {
    padding: 1rem 2rem !important;
    font-size: 1.2rem !important;
    transition: all 0.3s ease !important;
}
</style>
"""

def init_session_state():
    """Initialize session state variables"""
    if 'current_text' not in st.session_state:
        st.session_state.current_text = None
    if 'reading_state' not in st.session_state:
        st.session_state.reading_state = None
    if 'processed_result' not in st.session_state:
        st.session_state.processed_result = None
    if 'read_status' not in st.session_state:
        st.session_state.read_status = load_read_status()

def load_read_status():
    """Load read status from file"""
    if os.path.exists(READ_STATUS_FILE):
        with open(READ_STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {phrase: False for phrase in SAMPLE_PHRASES}

def save_read_status():
    """Save read status to file"""
    with open(READ_STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.read_status, f, ensure_ascii=False, indent=2)

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
    state = st.session_state.reading_state
    current_level = state['current_level']
    level_data = state['levels'][current_level]
    
    # Update stats
    state['stats'][rating] += 1
    
    # Advance to next word
    level_data['progress'] += 1
    
    # Check level completion
    if level_data['progress'] >= len(level_data['words']):
        if current_level < 3:
            state['current_level'] += 1
        else:
            # Calculate success rate
            success_rate = (state['stats']['good'] + state['stats']['medium'] * 0.5) / state['stats']['total_words']
            if success_rate >= 0.95:
                st.session_state.read_status[st.session_state.current_text] = True
                save_read_status()

def show_text_selection():
    """Display text selection screen"""
    st.markdown(STYLE, unsafe_allow_html=True)
    
    st.title("Тренажер чтения")
    
    st.subheader("Примеры текстов")
    
    # Sample phrases grid
    for idx, phrase in enumerate(sorted(SAMPLE_PHRASES, key=lambda x: calculate_text_complexity(x))):
        with st.container(border=True):
            # Adjust column widths based on screen size
            cols = st.columns([4, 1.5, 1])  # Wider middle column for checkbox
            
            with cols[0]:
                st.markdown(f"\n{truncate_text(phrase, 100)}")
                st.caption(f"Сложность: {calculate_text_complexity(phrase)}")
                
            with cols[1]:
                # Add checkbox with dynamic text
                is_read = st.session_state.read_status.get(phrase, False)
                checkbox_label = "Прочитано" if is_read else "Не прочитано"
                
                # Use a unique key combining phrase and index
                unique_key = f"read_{idx}_{hash(phrase)}"
                new_status = st.checkbox(
                    checkbox_label,
                    value=is_read,
                    key=unique_key,
                    label_visibility="visible"
                )
                
                # Update status only if it changed
                if new_status != is_read:
                    st.session_state.read_status[phrase] = new_status
                    save_read_status()
                    st.rerun()
                
            with cols[2]:
                if is_read:
                    st.button(
                        "Снова",
                        key=f"ph_{idx}",
                        on_click=start_reading_session,
                        args=(phrase,),
                        type="secondary",
                        use_container_width=True
                    )
                else:
                    st.button(
                        "Начать",
                        key=f"ph_{idx}",
                        on_click=start_reading_session,
                        args=(phrase,),
                        type="primary",
                        use_container_width=True
                    )
    
    # Custom text input
    with st.expander("Ввести свой текст", expanded=False):
        custom_text = st.text_area("Введите текст:", height=150)
        if st.button("Начать чтение", key="custom_start"):
            start_reading_session(custom_text)

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
    # Fix progress calculation to ensure it stays between 0 and 1
    level_progress = level_data['progress'] / len(level_data['words'])
    progress = (current_level - 1) / total_levels + level_progress / total_levels
    progress = min(progress, 1.0)  # Ensure progress doesn't exceed 1.0
    
    st.progress(progress, text=f"Уровень {current_level} из {total_levels} - {LEVEL_NAMES[current_level]}")
    
    # Word display
    if current_level <= 3 and level_data['progress'] < len(level_data['words']):
        current_word = level_data['words'][level_data['progress']]
        st.markdown(f'<div class="word-display">{current_word}</div>', unsafe_allow_html=True)
        
        # Rating buttons
        cols = st.columns(3)
        with cols[0]:
            st.button("🤔 Трудно", 
                     on_click=handle_rating, args=('bad',), 
                     type="secondary", 
                     use_container_width=True)
        with cols[1]:
            st.button("😐 Средне", 
                     on_click=handle_rating, args=('medium',), 
                     type="secondary",
                     use_container_width=True)
        with cols[2]:
            st.button("🎉 Отлично!", 
                     on_click=handle_rating, args=('good',), 
                     type="primary",
                     use_container_width=True)
        
        # Add return button
        st.button("← Вернуться к выбору текста", 
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
        # Add rating statistics
        st.subheader("Результаты по оценкам")
        rating_cols = st.columns(3)
        with rating_cols[0]:
            st.metric("🎉 Отлично", state['stats']['good'])
        with rating_cols[1]:
            st.metric("😐 Средне", state['stats']['medium'])
        with rating_cols[2]:
            st.metric("🤔 Трудно", state['stats']['bad'])
        
        # Level progress
        for level in range(1, 4):
            st.subheader(f"Уровень {level}: {LEVEL_NAMES[level]}")
            level_data = state['levels'][level]
            st.write(f"Прогресс: {len(level_data['words'])}/{len(level_data['words'])} слов")
    
    # Navigation
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Читать другой текст", type="primary"):
            st.session_state.reading_state = None
            st.session_state.current_text = None
            st.rerun()

def main():
    init_session_state()
    
    if st.session_state.reading_state:
        show_reading_interface()
    else:
        show_text_selection()

if __name__ == "__main__":
    main()