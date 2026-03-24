import sqlite3

def build_db():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()

    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exams (exam_id INTEGER PRIMARY KEY, exam_name TEXT, exam_date DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS marks (mark_id INTEGER PRIMARY KEY, student_id INTEGER, exam_id INTEGER, correct_count INTEGER, incorrect_count INTEGER, marks_obtained REAL)''')

    # YOUR REAL DATA: ("Name", "Test Name", "Date", Correct, Wrong)
    my_test_data = [
        ("Student One", "History Mock 1", "2026-03-20", 40, 15),
        ("Student One", "Polity Mock 1", "2026-03-22", 60, 10),
        ("Student One", "CSAT Mock 1", "2026-03-24", 30, 25), # This will show as a "lag"
        
        ("Student Two", "History Mock 1", "2026-03-20", 70, 5),
        ("Student Two", "Polity Mock 1", "2026-03-22", 45, 20),
        ("Student Two", "CSAT Mock 1", "2026-03-24", 50, 15)
    ]

    for row in my_test_data:
        name, test_name, date, correct, wrong = row
        
        # 1. Add student if not exists
        c.execute("INSERT OR IGNORE INTO students (name) VALUES (?)", (name,))
        c.execute("SELECT student_id FROM students WHERE name = ?", (name,))
        s_id = c.fetchone()[0]

        # 2. Add exam if not exists
        c.execute("INSERT OR IGNORE INTO exams (exam_name, exam_date) VALUES (?, ?)", (test_name, date))
        c.execute("SELECT exam_id FROM exams WHERE exam_name = ?", (test_name,))
        e_id = c.fetchone()[0]

        # 3. Calculate Score and Add Marks
        score = round((correct * 2) - (wrong * 0.66), 2)
        c.execute("INSERT INTO marks (student_id, exam_id, correct_count, incorrect_count, marks_obtained) VALUES (?, ?, ?, ?, ?)", (s_id, e_id, correct, wrong, score))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_db()
