import streamlit as st
import pandas as pd

st.set_page_config(page_title="Оценка риска ССЗ", layout="centered")
st.title("🫀 Оценка риска сердечно-сосудистых заболеваний (ССЗ)")

uploaded_file = st.file_uploader("Загрузите Excel-файл с метаболомным профилем", type=["xlsx"])

# Таблица критериев оценки по маркерам
criteria = [
    {"marker": "ADMA", "thresholds": [0.45, 0.6], "score": [0, 1, 2], "direction": ">"},
    {"marker": "TotalDMA", "thresholds": [0.45, 0.6], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Arg/ADMA", "thresholds": [100, 150], "score": [2, 1, 0], "direction": "<"},
    {"marker": "(Arg+HomoArg)/ADMA", "thresholds": [150, 200], "score": [2, 1, 0], "direction": "<"},
    {"marker": "TMAO", "thresholds": [0.05, 0.08], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Betaine/Choline", "thresholds": [1.5, 2.0], "score": [2, 1, 0], "direction": "<"},
    {"marker": "(C16+C18)/C2", "thresholds": [0.5, 0.7], "score": [0, 1, 2], "direction": ">"},
    {"marker": "C0/(C16+C18)", "thresholds": [1.6, 2.0], "score": [2, 1, 0], "direction": "<"},
    {"marker": "BCAA", "thresholds": [300, 450], "score": [0, 1, 2], "direction": ">"},
    {"marker": "BCAA/AAA", "thresholds": [2.0, 2.5], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Kyn/Trp", "thresholds": [0.045, 0.06], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Quin/HIAA", "thresholds": [1.5, 2.5], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Quinolinic acid", "thresholds": [50, 80], "score": [0, 1, 2], "direction": ">"},
    {"marker": "Serotonin", "thresholds": [0.05, 0.1], "score": [2, 1, 0], "direction": "<"},
    {"marker": "Melatonin", "thresholds": [15, 30], "score": [2, 1, 0], "direction": "<"},
    {"marker": "Cortisol", "thresholds": [500, 650], "score": [0, 1, 2], "direction": ">"}
]

interpretation_scale = {
    (9, 10): "Метаболическая ось в хорошем или оптимальном состоянии (все ключевые показатели в референсе или выше по 'плюсам')",
    (7, 8): "Незначительные отклонения, компенсаторные механизмы работают",
    (5, 6): "Умеренные нарушения — не критично, но уже требует коррекции",
    (3, 4): "Существенные изменения — снижен резерв, хроническая нагрузка",
    (1, 2): "Выраженные патологии, декомпенсация, высокий риск"
}

def interpret_score(score):
    for (low, high), text in interpretation_scale.items():
        if low <= score <= high:
            return text
    return "Недостаточно данных для интерпретации"

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)
    headers = df.iloc[0]
    values = df.iloc[1]
    row = pd.Series(data=values.values, index=headers.values)

    total_score = 0
    report = []

    for rule in criteria:
        marker = rule["marker"]
        if marker in row:
            try:
                value = float(row[marker])
                t1, t2 = rule["thresholds"]
                s0, s1, s2 = rule["score"]
                if rule["direction"] == ">":
                    score = s0 if value <= t1 else s1 if value <= t2 else s2
                else:
                    score = s0 if value >= t2 else s1 if value >= t1 else s2
                total_score += score
                report.append((marker, value, score))
            except:
                continue

    max_score = len(report) * 2
    if max_score > 0:
        scaled_score = round((total_score / max_score) * 10)
        interpretation = interpret_score(scaled_score)

        st.subheader("📊 Результаты оценки")
        st.metric("Суммарный балл", scaled_score)
        st.write(interpretation)

        st.subheader("🔍 Подробности")
        st.dataframe(pd.DataFrame(report, columns=["Показатель", "Значение", "Баллы"]))
    else:
        st.error("❗️Файл не содержит необходимых маркеров. Убедитесь, что названия показателей соответствуют.")
else:
    st.info("Пожалуйста, загрузите файл Excel с метаболомными показателями.")
