# streamlit_db.py

import streamlit as st
from sqlalchemy import text


# Create the SQL connection to pets_db as specified in your secrets file.
conn = st.connection('chat_db', type='sql')

# Insert some data with conn.session.
with conn.session as s:
    s.execute(text('CREATE TABLE IF NOT EXISTS chat_history (id INTEGER NOT NULL, chat_message VARCHAR(500) NOT NULL);'))
    s.execute(text('DELETE FROM chat_history;'))
    chat_history = {1: 'TEST CHAT 1', 2: 'TEST CHAT 2'}
    for k in chat_history:
        s.execute(
            text('INSERT INTO chat_history (id, chat_message) VALUES (:id, :chat_message);'),
            params=dict(id=k, chat_message=chat_history[k])
        )
    s.commit()

# Query and display the data you inserted
pet_owners = conn.query('SELECT * FROM chat_history;')
st.dataframe(pet_owners)