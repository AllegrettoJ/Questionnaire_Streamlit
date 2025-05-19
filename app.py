
import streamlit as st
import pandas as pd
import random
import altair as alt
from datetime import datetime
import os

QUESTIONS_FILE = "questions.csv"
ANSWERS_FILE = "answers.csv"

@st.cache_data
def load_questions():
    return pd.read_csv(QUESTIONS_FILE, encoding="utf-8")

def get_random_questions(df, num_questions=10):
    questions = df.sample(n=num_questions).reset_index(drop=True)
    question_list = []
    for _, row in questions.iterrows():
        correct_letter = row["正确答案"].strip()
        correct_text = row[f"选项{correct_letter}"].strip()
        question_list.append({
            "题号": row["题号"],
            "题目": row["题目"],
            "选项": [
                row["选项A"].strip(),
                row["选项B"].strip(),
                row["选项C"].strip(),
                row["选项D"].strip()
            ],
            "正确答案文本": correct_text
        })
    return question_list

def save_answers(data):
    df_new = pd.DataFrame(data)
    if os.path.exists(ANSWERS_FILE):
        df_old = pd.read_csv(ANSWERS_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(ANSWERS_FILE, index=False)

def show_altair_charts(correct_count, wrong_count):
    data = pd.DataFrame({
        "结果": ["答对", "答错"],
        "数量": [correct_count, wrong_count]
    })

    bar_chart = alt.Chart(data).mark_bar(size=60).encode(
        x=alt.X("结果", sort=["答对", "答错"]),
        y="数量",
        color=alt.Color("结果", scale=alt.Scale(domain=["答对", "答错"], range=["#1f77b4", "#ff7f0e"]))
    ).properties(width=300, height=300, title="Chart 1")

    pie_chart = alt.Chart(data).mark_arc(innerRadius=60).encode(
        theta="数量",
        color=alt.Color("结果", scale=alt.Scale(domain=["答对", "答错"], range=["#1f77b4", "#ff7f0e"])),
        tooltip=["结果", "数量"]
    ).properties(width=300, height=300, title="Chart 2")

    col1, col2 = st.columns(2)
    col1.altair_chart(bar_chart, use_container_width=True)
    col2.altair_chart(pie_chart, use_container_width=True)

def main():
    st.title("Questionnaire")

    st.subheader("请输入您的信息")
    name = st.text_input("姓名")
    emp_id = st.text_input("工号")

    if name and emp_id:
        st.success("信息录入成功，请开始答题")

        if "quiz_data" not in st.session_state:
            raw_df = load_questions()
            st.session_state.quiz_data = get_random_questions(raw_df)

        quiz_data = st.session_state.quiz_data
        submitted = False
        answers = []

        with st.form("quiz_form"):
            st.write("请回答以下问题：")
            for i, q in enumerate(quiz_data):
                answer = st.radio(
                    f"{i+1}. {q['题目']}",
                    q["选项"],
                    key=q["题号"],
                    index=None
                )
                answers.append((q["题号"], answer, q["正确答案文本"]))
            submitted = st.form_submit_button("提交")

        if submitted:
            missing = [i for i, ans in enumerate(answers) if ans[1] is None]
            if missing:
                st.error("❌ 提交失败：请完成所有题目再提交。")
                for i, (qid, answer, _) in enumerate(answers):
                    if answer is None:
                        st.markdown(
                            f"<div style='color:#f39c12;font-size:0.9rem;margin-top:-10px;margin-bottom:20px;'>⚠ 第 {i+1} 题未选择答案</div>",
                            unsafe_allow_html=True
                        )
            else:
                result_data = []
                correct = 0
                wrong = 0
                for i, (qid, selected, correct_text) in enumerate(answers):
                    sel = selected.strip()
                    corr = correct_text.strip()
                    is_correct = sel == corr
                    if is_correct:
                        correct += 1
                    else:
                        wrong += 1

                    st.markdown(f"""
                        **第{i+1}题：{qid}**  
                        - 你选了：`{repr(sel)}`  
                        - 正确答案：`{repr(corr)}`  
                        - 判断：`{"✔ 正确" if is_correct else "❌ 错误"}`
                    """)

                    result_data.append({
                        "姓名": name,
                        "工号": emp_id,
                        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "题号": qid,
                        "选择": selected,
                        "正确答案": correct_text,
                        "是否正确": int(is_correct)
                    })

                save_answers(result_data)
                st.success(f"✅ 提交成功！您本次答对了 {correct}/10 题。")
                show_altair_charts(correct, wrong)

if __name__ == "__main__":
    main()
