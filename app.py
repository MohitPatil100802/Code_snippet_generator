import sqlite3
import datetime
import openai
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QTextEdit, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout
)

# Load the .env file
load_dotenv()

# Database Initialization
def initialize_database():
    """Initialize the SQLite database and create the required table."""
    conn = sqlite3.connect("code_snippets.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            code TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Generate Code Snippet using ChatGPT API
def generate_code_snippet(task):
    """Generate code snippet dynamically using ChatGPT API."""
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Load API key from .env
    if not openai.api_key:
        return "Error: OpenAI API key is not set. Please configure it in the .env file."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",  # Use gpt-3.5-turbo or gpt-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates Python code snippets."},
                {"role": "user", "content": f"Write a Python code for the following task:\n{task}"}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        return f"Error generating code: {e}"

# Store Snippet in Database
def store_snippet(task, code):
    """Store the task, generated code, and timestamp in the database."""
    conn = sqlite3.connect("code_snippets.db")
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO snippets (task, code, timestamp) VALUES (?, ?, ?)
    """, (task, code, timestamp))
    conn.commit()
    conn.close()

# Retrieve Snippets from Database
def retrieve_snippets():
    """Retrieve all stored snippets from the database."""
    conn = sqlite3.connect("code_snippets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM snippets")
    rows = cursor.fetchall()
    conn.close()
    return rows

# PyQt5 GUI Application
class CodeSnippetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Snippet Generator")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.layout = QVBoxLayout()

        # Task Input
        self.task_label = QLabel("Enter Programming Task:")
        self.layout.addWidget(self.task_label)
        self.task_input = QLineEdit()
        self.layout.addWidget(self.task_input)

        # Generate Button
        self.generate_button = QPushButton("Generate Code Snippet")
        self.generate_button.clicked.connect(self.generate_snippet)
        self.layout.addWidget(self.generate_button)

        # Generated Code Display
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.layout.addWidget(self.code_output)

        # View Snippets Button
        self.view_button = QPushButton("View Stored Snippets")
        self.view_button.clicked.connect(self.display_snippets)
        self.layout.addWidget(self.view_button)

        # Snippets Table
        self.snippets_table = QTableWidget()
        self.snippets_table.setColumnCount(4)
        self.snippets_table.setHorizontalHeaderLabels(["ID", "Task", "Code", "Timestamp"])
        self.layout.addWidget(self.snippets_table)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def generate_snippet(self):
        """Handle snippet generation and storage."""
        task = self.task_input.text()
        if not task:
            self.code_output.setText("Please enter a task.")
            return

        code = generate_code_snippet(task)
        store_snippet(task, code)
        self.code_output.setText(code)

    def display_snippets(self):
        """Display all stored snippets in the table."""
        snippets = retrieve_snippets()
        self.snippets_table.setRowCount(len(snippets))

        for row_index, row_data in enumerate(snippets):
            for col_index, col_data in enumerate(row_data):
                self.snippets_table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

# Main Application Entry Point
def main():
    initialize_database()

    app = QApplication([])
    window = CodeSnippetApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
