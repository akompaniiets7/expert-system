import streamlit as st
import json
import os
from datetime import datetime

# Завантаження лекцій
@st.cache_data
def load_lectures():
    lectures = {}
    for file in os.listdir("lectures"):
        if file.endswith(".json"):
            with open(os.path.join("lectures", file), encoding="utf-8-sig") as f:
                data = json.load(f)
                lectures[data["тема"]] = data
    return lectures

# Завантаження тестів
@st.cache_data
def load_tests():
    tests = {}
    for file in os.listdir("tests"):
        if file.endswith(".json"):
            with open(os.path.join("tests", file), encoding="utf-8-sig") as f:
                data = json.load(f)
                tests[data["тема"]] = data["питання"]
    return tests

# Збереження результату
def save_result(user, тема, правильних, всього, рекомендації):
    result = {
        "користувач": user,
        "тема": тема,
        "дата": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "правильних": правильних,
        "усього": всього,
        "рекомендації": рекомендації
    }
    if os.path.exists("results.json"):
        with open("results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []
    results.append(result)
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# Пояснення з лекції
def show_explanation(lecture, заголовок, ключ):
    for пункт in lecture.get("пункти", []):
        if пункт.get("заголовок") == заголовок:
            for підтема in пункт.get("підтеми", []):
                if підтема.get("ключ") == ключ:
                    st.info(f"📘 Пояснення: {підтема['текст']}")
                    return

# Основна логіка тестування
st.set_page_config(page_title="Експертна система з матеріалознавства")
st.title("🎓 Експертна система з матеріалознавства")

lectures = load_lectures()
tests = load_tests()

topics = list(tests.keys())

# --- Стан користувача ---
if "user_started" not in st.session_state:
    st.session_state.user_started = False

if not st.session_state.user_started:
    user_name = st.text_input("Введіть ваше ім'я для збереження результату:")
    selected_topic = st.selectbox("Оберіть тему для проходження тесту:", ["Всі теми"] + topics)

    if st.button("Почати тестування") and user_name.strip() != "":
        st.session_state.user_started = True
        st.session_state.user_name = user_name
        st.session_state.selected_topic = selected_topic
        st.experimental_rerun()
else:
    user_name = st.session_state.user_name
    selected_topic = st.session_state.selected_topic
    st.success(f"Вітаємо, {user_name}! Ви проходите тест з теми: {selected_topic}")

    recommendations = []
    correct_total = 0
    question_total = 0

    for тема in (topics if selected_topic == "Всі теми" else [selected_topic]):
        st.subheader(f"📚 Тема: {тема}")
        questions = tests[тема]
        correct = 0

        for idx, q in enumerate(questions):
            st.markdown(f"**{q['текст']}**")

            if isinstance(q["правильна"], list):
                selected = st.multiselect("Оберіть варіанти:", q["варіанти"], key=f"q_{тема}_{idx}")
                selected_idx = [q["варіанти"].index(x) for x in selected]
                if sorted(selected_idx) == sorted(q["правильна"]):
                    st.success("✅ Правильно!")
                    correct += 1
                else:
                    st.error("❌ Неправильно.")
                    show_explanation(lectures[тема], q["заголовок"], q["ключ"])
                    recommendations.append((тема, q["заголовок"], q["ключ"]))
            else:
                answer = st.radio("Оберіть один варіант:", q["варіанти"], key=f"q_{тема}_{idx}", index=None)
                answer_idx = q["варіанти"].index(answer)
                if answer_idx == q["правильна"]:
                    st.success("✅ Правильно!")
                    correct += 1
                else:
                    st.error("❌ Неправильно.")
                    show_explanation(lectures[тема], q["заголовок"], q["ключ"])
                    recommendations.append((тема, q["заголовок"], q["ключ"]))

        st.markdown(f"**Результат по темі \"{тема}\": {correct}/{len(questions)}**")
        correct_total += correct
        question_total += len(questions)

    st.markdown("---")
    st.subheader("📊 Загальний результат")
    st.write(f"Правильних відповідей: **{correct_total} / {question_total}** ({(correct_total/question_total)*100:.1f}%)")

    if recommendations:
        st.warning("📌 Рекомендації:")
        for тема, заголовок, ключ in recommendations:
            st.write(f"- **{тема} → {заголовок} → {ключ}**")
    else:
        st.success("Вітаємо! Усі відповіді правильні 🎉")

    save_result(user_name, selected_topic, correct_total, question_total, recommendations)
