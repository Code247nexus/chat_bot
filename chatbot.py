


import streamlit as st 
from langchain_groq import ChatGroq
from gtts import gTTS
from fpdf import FPDF
import base64
from datetime import datetime
import os

# Initialize Groq Model
llm = ChatGroq(
    temperature = 1.0,
    groq_api_key = "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",
    model_name ="llama-3.3-70b-versatile"

)


# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
    
    
 # Function to convert text to speech
def text_to_speech(text, filename="response.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename
    
    
# Function to play audio
def play_audio(audio_file):
    with open(audio_file, "rb") as file:
        audio_bytes = file.read()
    st.audio(audio_bytes, format="audio/mp3")


# Function to create PDF
def create_pdf(conversations, filename="chat_history.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Roman", size=14)
    pdf.cell(200, 10, txt="Chatbot Conversation History", ln=True, align='C')
    pdf.ln(10)
    for convo in conversations:
        pdf.multi_cell(0, 10, txt=convo)
        pdf.ln(5)
    pdf.output(filename)
    
# ----------------------------
# Background Image Function
# ----------------------------
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: white;
    }}
    .stTextArea textarea, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border-radius: 8px;
    }}
    .stButton button {{
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
    }}
    .stButton button:hover {{
        background-color: #45a049;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


set_background("chatbot.jpg") 
    
# Streamlit UI
#st.sidebar.header("About")
#st.sidebar.write("A chatbot powered by Llama3 (via Groq) to answer any queries — just by adjusting the system prompt.")

# System prompt input (optional)
#system_prompt = st.sidebar.text_area("System Prompt (optional)", 
 #                                    "You are a helpful AI assistant. Answer the user's queries politely and informatively.")
st.title("🤖 Robin - The Chatbot")

st.sidebar.header("About")
st.sidebar.write("A universal chatbot using Llama3 via Groq API. Includes TTS, PDF export, and custom background.")

system_prompt = st.sidebar.text_area("System Prompt (optional)", 
                                     "You are a helpful AI assistant. Answer queries politely and informatively.")

user_query = st.text_area("Enter your query:")

if st.button("Get Response"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            final_query = f"{system_prompt}\nUser: {user_query}"

            response = llm.invoke(final_query)

            if response.content:
                st.success("Response:")
                st.write(response.content)

                st.session_state.conversation_history.append(
                    f"[{timestamp}]\nUser: {user_query}\nBot: {response.content}\n"
                )

                audio_file = text_to_speech(response.content)
                st.write("🔊 Listen to the response:")
                play_audio(audio_file)
            else:
                st.error("No response received.")
    else:
        st.warning("Please enter a query.")

if st.button("Download Conversation as PDF"):
    if st.session_state.conversation_history:
        pdf_file = "chat_history.pdf"
        create_pdf(st.session_state.conversation_history, pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name=pdf_file)
    else:
        st.warning("No conversation history yet.")






