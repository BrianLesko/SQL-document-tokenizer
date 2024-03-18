# Brian Lesko
# 3/18/2024

import streamlit as st
from SQLConnect import SQLConnectDocker as SQLConnect
from customize_gui import gui as gui 
gui = gui()
import os
import time

def main(): 

    gui.setup(wide=True, text="Chunk Documents, no overlap, use scentance or token ends and have a min and max chunk size by token.")
    st.title('Chunk Documents')
    current_task = st.empty()

    if "sql" not in st.session_state:
        st.session_state.sql = SQLConnect()
        st.session_state.sql.connect()
    if "sql" in st.session_state:
        sql = st.session_state.sql

    with st.sidebar:
        result = sql.get_summary()
        Databases = st.empty()
        with Databases: st.table(result)
        "---"
        st.write('Docker installed:', sql.docker_version)
        st.write('Docker running:', sql.docker_is_running)
        if not sql.docker_is_running: 
            st.write("Docker is not running")
        st.write('Container running:', sql.container_is_running)

        if st.button("Restart the MySQL Container"):
            sql.stop_container()
            sql.start_container()
    
    sql.query("USE user")
    existing = sql.query("SELECT name FROM size;")
    st.write(f"{len(existing)} Rows in the database.")
    # Convert existing to a set
    existing_files = set([file['name'] for file in existing])
    st.write(f"{len(existing_files)} Unique files in the database.")

    import chunk_documents
    library = sql.query("SELECT content FROM content;")
    names = sql.query("SELECT name FROM content;")
    st.write(f"{len(library)} Documents in the library.")
    st.write(f"{len(names)} Names in the library.")
    st.write(f"About to Write to the database.")

    for j, document in enumerate(library):
        document = document['content']
        name = names[j]['name']
        st.write(name)
        st.write(f"There are this many characters in the document: {len(document)}")
        tokens = chunk_documents.tokenizer.tokenize(document)
        st.write(f"There are this many tokens in the document: {len(tokens)}")
        #st.write(f"Tokens: {tokens}")

        chunks = chunk_documents.chunk_document(tokens, min_chunk_size=300, max_chunk_size=600)
        st.write(f"There are this many chunks in the document: {len(chunks)}")

        # Write to a new row
        for i, chunk in enumerate(chunks):
            sql.cursor.execute("INSERT INTO chunks (source, chunk_number, content) VALUES (%s, %s, %s);", (name, i, chunk))
        st.write(f"{i} Chunks have been added to the database.")
        sql.connection.commit()
main()