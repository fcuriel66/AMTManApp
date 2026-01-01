import sqlite3

from link_extract import extract_links_by_text, extract_chapter, copy_pdf_list
from langchain_core.messages import HumanMessage, AIMessage


gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');

.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 4em;
  background: linear-gradient(90deg, #ff6a00, #ee0979);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
  margin: 0;
  padding: 20px 0;
  text-align: center;
}
</style>
<div class="snowchat-title">AMTMan</div>
"""


def find_pdf_from_task_numbers(task_numbers: list):
    """ Find PDF files from a list of task numbers."""

    # Extraction of chapter number to put in the search path
    tasks_chapter = extract_chapter(task_numbers)

    # Extraction of the links in pdf TOC chapter files associated with the text of tasks in task_num list
    matches = extract_links_by_text(f"PDF/025-MPP1285_{tasks_chapter}-TOC.PDF", task_numbers)

    # Copy selected PDF files from MPP original directory to single working directory (AMM_EXTRACTED)
    result = copy_pdf_list(
        matches,
        destination_dir="/Users/fernandocuriel/PycharmProjects/RAG/PDF/AMM_EXTRACTED/" + f"{tasks_chapter}",
        base_dir="/Users/fernandocuriel/PycharmProjects/RAG/PDF"
    )

    print(f"Copied in ../AMM_EXTRACTED/{tasks_chapter}")
    print()
    for f in result["copied"]:
        print("  ✓", f)

    print("\nMissing:")
    for f in result["missing"]:
        print("  ✗", f)

    return result


def extract_human_ai_messages(history):
    filtered = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            filtered.append(("human", msg.content))
        elif isinstance(msg, AIMessage):
            filtered.append(("ai", msg.content))
    return filtered


def ensure_user(user_id, conn):
    conn.execute(
        "INSERT OR IGNORE INTO users (id) VALUES (?)",
        (user_id,)
    )


# Saving of history defaults to same path as in streamlit_app3.py
def save_history(user_id, history, db_path="database/maintenance.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    ensure_user(user_id, conn)

    messages = extract_human_ai_messages(history)

    cursor.executemany(
        """
        INSERT INTO maintenance_history (user_id, role, content)
        VALUES (?, ?, ?)
        """,
        [(user_id, role, content) for role, content in messages]
    )

    conn.commit()
    conn.close()


def load_history(user_id, db_path="database/maintenance.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content, created_at
        FROM maintenance_history
        WHERE user_id = ?
        ORDER BY created_at ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users(db_path="database/maintenance.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users ORDER BY created_at DESC")
    users = [row[0] for row in cursor.fetchall()]

    conn.close()
    return users
