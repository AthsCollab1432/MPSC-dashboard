import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# --- 1. AUTOMATIC DATABASE SETUP FROM YOUR CSV ---
def init_db():
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        conn = sqlite3.connect('academy.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS exams (exam_id INTEGER PRIMARY KEY, exam_name TEXT UNIQUE, exam_date DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS marks (mark_id INTEGER PRIMARY KEY, student_id INTEGER, exam_id INTEGER, correct_count INTEGER, incorrect_count INTEGER, marks_obtained REAL)''')
        
        for index, row in df.iterrows():
            name = str(row['STUDENT']).strip()
            test_name = str(row['TEST NAME']).strip()
            date = str(row['TEST DATE']).strip()
            correct = int(row['RIGHT'])
            wrong = int(row['WRONG'])
            
            c.execute("INSERT OR IGNORE INTO students (name) VALUES (?)", (name,))
            c.execute("SELECT student_id FROM students WHERE name = ?", (name,))
            s_id = c.fetchone()[0]

            c.execute("INSERT OR IGNORE INTO exams (exam_name, exam_date) VALUES (?, ?)", (test_name, date))
            c.execute("SELECT exam_id FROM exams WHERE exam_name = ?", (test_name,))
            e_id = c.fetchone()[0]

            score = round((correct * 2) - (wrong * 0.66), 2)
            c.execute("INSERT INTO marks (student_id, exam_id, correct_count, incorrect_count, marks_obtained) VALUES (?, ?, ?, ?, ?)", (s_id, e_id, correct, wrong, score))
        
        conn.commit()
        conn.close()

# If the database doesn't exist, build it using the CSV
if not os.path.exists('academy.db'):
    init_db()

# --- 2. MOBILE DASHBOARD UI ---
st.set_page_config(page_title="MPSC Analytics", layout="vertical")

def get_data(query):
    conn = sqlite3.connect('academy.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("📱 Subject Analytics")

if not os.path.exists('academy.db'):
    st.error("Error: Could not build database. Is your data.csv file uploaded?")
else:
    # Dropdown to select a student from your CSV
    students = get_data("SELECT name FROM students ORDER BY name ASC")
    choice = st.selectbox("Search Student Profile", students['name'].tolist())

    if choice:
        query = f"""
        SELECT e.exam_name, e.exam_date, m.correct_count, m.incorrect_count, m.marks_obtained
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN exams e ON m.exam_id = e.exam_id
        WHERE s.name = '{choice}'
        ORDER BY e.exam_date ASC
        """
        df_history = get_data(query)
        
        if not df_history.empty:
            st.subheader(f"Performance Tracking: {choice}")
            
            # Calculate Accuracy
            df_history['Accuracy %'] = (df_history['correct_count'] / (df_history['correct_count'] + df_history['incorrect_count'])) * 100
            
            # Subject Lag Bar Chart
            fig = px.bar(df_history, x='exam_name', y='Accuracy %', 
                          title="Subject-Wise Accuracy",
                          labels={'exam_name': 'Test Name'},
                          color='Accuracy %',
                          color_continuous_scale=['red', 'yellow', 'green'])
            
            fig.add_hline(y=50, line_dash="dot", annotation_text="Danger Zone (<50%)", line_color="red")
            st.plotly_chart(fig, use_container_width=True)

            st.write("Detailed Test Breakdown")
            st.dataframe(df_history[['exam_date', 'exam_name', 'correct_count', 'incorrect_count', 'marks_obtained']])
