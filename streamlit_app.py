import streamlit as st
from openai import OpenAI
from parse_hh import get_html, extract_vacancy_data, extract_resume_data

# Клиент OpenAI. Ключ берём из секретов Streamlit Cloud (настраивается в настройках приложения)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """Проскорь кандидата, насколько он подходит для данной вакансии.
Сначала напиши короткий анализ, который будет пояснять оценку.
Отдельно оцени качество заполнения резюме (понятно ли, с какими задачами сталкивался кандидат и как решал задачи).
Потом представь результат в виде оценки от 1 до 10.
""".strip()

st.title("CV Scoring App")

st.markdown(
    "Это демо-приложение для прескоринга кандидатов. "
    "Вставь текст вакансии и резюме, нажми кнопку — и получишь анализ."
)

# Ввод данных
job_description = st.text_area("Введите описание вакансии", height=200)
cv = st.text_area("Введите описание резюме кандидата", height=200)

url_vacancy = st.text_input("Ссылка на вакансию с hh.ru (необязательно)")
url_resume = st.text_input("Ссылка на резюме с hh.ru (необязательно)")

if st.button("Спарсить данные по ссылкам hh.ru"):
    if url_vacancy:
        with st.spinner("Парсим вакансию..."):
            html = get_html(url_vacancy)
            vacancy_md = extract_vacancy_data(html)
            st.subheader("Спарсенная вакансия")
            st.markdown(vacancy_md)
            # Подставим в поле описания вакансии
            job_description = vacancy_md

    if url_resume:
        with st.spinner("Парсим резюме..."):
            html = get_html(url_resume)
            resume_md = extract_resume_data(html)
            st.subheader("Спарсенное резюме")
            st.markdown(resume_md)
            cv = resume_md

if st.button("Оценить резюме"):
    if not job_description or not cv:
        st.error("Нужно заполнить описание вакансии и резюме (либо текстом, либо через ссылки).")
    else:
        with st.spinner("Оцениваем резюме..."):
            user_prompt = f"# ВАКАНСИЯ\n{job_description}\n\n# РЕЗЮМЕ\n{cv}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=1200,
                temperature=0,
            )
            st.subheader("Результат прескоринга")
            st.write(response.choices[0].message.content)
