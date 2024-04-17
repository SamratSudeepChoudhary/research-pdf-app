import time
import streamlit as st
import os
import shutil
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import openai
from collections import deque

@st.cache_data
def unzip_files(temp_var):
    shutil.unpack_archive("_pdfs.zip")
    shutil.unpack_archive("_txts.zip")
    shutil.unpack_archive("_txts2.zip")
    shutil.unpack_archive("_txts3.zip")
    shutil.unpack_archive("_dbs3.zip")
    return True

@st.cache_resource
def create_qa(db_name):
    db = FAISS.load_local('./_dbs3/' + db_name, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=1), chain_type="stuff", retriever=db.as_retriever())
    return qa

st.title("Chat with Research reports📈")

unzip_files(True)

db_name = st.sidebar.selectbox(
    "Choose a Research report:",
    os.listdir('./_dbs3')
)

with open("./_pdfs/" + db_name + ".pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

st.sidebar.download_button(label="Download PDF",
                            data=PDFbyte,
                            file_name=db_name + ".pdf",
                            mime='application/octet-stream')

caption_message = open('./_txts/' + db_name + '_simplified.txt').read()
st.sidebar.caption(caption_message)

caption_message2 = open('./_txts2/' + db_name + '_parameters.txt').read()
st.sidebar.caption(caption_message2)

info_message = open('./_txts3/' + db_name + '_reasons.txt').read()
st.sidebar.info(info_message)

openai.api_key = st.secrets["OPENAI_API_KEY"]

qa = create_qa(db_name)

questions_list = [
  'Custom',
  'EPS (Rs) for different years?',
  'Div. yield (%) for different years?',
  'Sales (Rs bn) for different years?',
  'EBITDA (Rs bn) for different years?',
  'Net profits (Rs bn) for different years?',
]

selected_question = st.sidebar.selectbox("Select a question:", questions_list)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if selected_question =='Custom':
    # Accept user input
    if prompt := st.chat_input("Send a message"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            assistant_response = qa({"query": prompt})["result"]

            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)

                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    # Add selected question to chat history
    st.session_state.messages.append({"role": "user", "content": selected_question})

    # Display user message in chat message container
    with st.chat_message("user"):
         st.markdown(selected_question)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
         message_placeholder = st.empty()
         full_response = ""
         assistant_response = qa({"query": selected_question})["result"]

         # Simulate stream of response with milliseconds delay
         for chunk in assistant_response.split():
             full_response += chunk + " "
             time.sleep(0.05)

             # Add a blinking cursor to simulate typing
             message_placeholder.markdown(full_response + "▌")
         message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = body.scrollHeight
    </script>
    '''

    st.components.v1.html(js)
