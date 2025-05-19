
import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os

# 读取题库
QUESTIONS_FILE = "questions.csv"
ANSWERS_FILE = "answers.csv"

@st.cache_data
def load_questions():
    df = pd.read_csv(QUESTIONS_FILE)
    return df

def get_random_questions(df, num_questions=10):
    return df.sample(n=num_questions).reset_index(drop=True)

def save_answers(data):
    df_new = pd.DataFrame(data)
    if os.path.exists(ANSWERS_FILE):
        df_old = pd.read_csv(ANSWERS_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(ANSWERS_FILE, index=False)

def main():
    st.title("员工在线答题系统")

    st.subheader("请输入您的信息")
    name = st.text_input("姓名")
    emp_id = st.text_input("工号")

    if name and emp_id:
        st.success("信息录入成功，请开始答题")
        questions_df = load_questions()
        quiz_df = get_random_questions(questions_df)

        answers = []
        score = 0

        with st.form("quiz_form"):
            st.write("请回答以下问题：")
            for i, row in quiz_df.iterrows():
                qid = row["题号"]
                question = row["题目"]
                options = [row["选项A"], row["选项B"], row["选项C"], row["选项D"]]
                answer = st.radio(f"{i+1}. {question}", options, key=qid)
                answers.append((qid, answer))
            submitted = st.form_submit_button("提交")

        if submitted:
            result_data = []
            for i, (qid, selected) in enumerate(answers):
                correct = quiz_df.loc[quiz_df["题号"] == qid, "正确答案"].values[0]
                correct_option = quiz_df.loc[quiz_df["题号"] == qid, f"选项{correct}"].values[0]
                is_correct = selected == correct_option
                score += int(is_correct)
                result_data.append({
                    "姓名": name,
                    "工号": emp_id,
                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "题号": qid,
                    "选择": selected,
                    "正确答案": correct_option,
                    "是否正确": int(is_correct)
                })

            save_answers(result_data)
            st.success(f"提交成功！您本次答对了 {score}/10 题。")

if __name__ == "__main__":
    main()
