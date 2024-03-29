# Brian Lesko
# 3/18/2024

import streamlit as st
from SQLConnect import SQLConnectDocker as SQLConnect
from customize_gui import gui as gui 
gui = gui()
import os
import time
import chunk_documents
import pandas as pd

def main(): 
    gui.setup(wide=True, text="Chunk Documents, no overlap, use scentance or token ends and have a min and max chunk size by token.")
    st.title('Chunk Documents')
    current_task = st.empty()

    # Keep the connection to the SQL container accross reruns
    if "sql" not in st.session_state:
        st.session_state.sql = SQLConnect()
        st.session_state.sql.connect()
    if "sql" in st.session_state:
        sql = st.session_state.sql

    with st.sidebar:
        result = sql.get_tables()
        Tables = st.empty()
        with Tables: st.table(result)
        "---"
        st.write('Docker installed:', sql.docker_version)
        st.write('Docker running:', sql.docker_is_running)
        if not sql.docker_is_running: 
            st.write("Docker is not running")
        st.write('Container running:', sql.container_is_running)

        if st.button("Restart the MySQL Container"):
            sql.stop_container()
            sql.start_container()
    
    # Prep
    sql.query("USE user")
    names = sql.query("SELECT name FROM summary;")
    names_df = pd.DataFrame(names)
    unique_names = names_df['name'].unique()
    st.write(f"{len(unique_names)} Unique entries in the library.")
    content_count = sql.query("SELECT COUNT(*) as count FROM content;")
    st.write(f"{content_count[0]['count']} rows in the content table.")
    if content_count[0]['count'] == unique_names.size:
        st.write("The content table is up to date.")
    else:
        st.write("The content table is not up to date. Please run the 'Add Content' script.")
    num_chunks = sql.query("SELECT COUNT(*) FROM chunks;")
    st.write(f"{num_chunks[0]['COUNT(*)']} Document chunks in the database.")

    if st.button("Clear the document chunks?"):
        sql.query("DELETE FROM chunks;")
        sql.connection.commit()
        st.write("Document chunks cleared.")

    if not st.button("Chunk each document?"):
        st.stop()

    for name in unique_names:
        st.caption(name)
        try:
            document = sql.query(f"SELECT content FROM content WHERE name = '{name}'")[0]['content']
            st.write(f"There are this many characters in the document: {len(document)}")
            tokens = chunk_documents.tokenizer.tokenize(document)
            st.write(f"There are this many tokens in the document: {len(tokens)}")

            with st.spinner("Chunking the document..."):
                chunks = chunk_documents.chunk_document(tokens, min_chunk_size=300, max_chunk_size=800)
                #st.write(f"There are this many chunks in the document: {len(chunks)}")

            # Write to a new row
            for i, chunk in enumerate(chunks):
                sql.cursor.execute("INSERT INTO chunks (source, chunk_number, content) VALUES (%s, %s, %s);", (name, i, chunk))
            st.write(f"{i+1} Chunks have been added to the database.")
            sql.connection.commit()
        except:
            st.write(f"{name} does not exist")
        
main()