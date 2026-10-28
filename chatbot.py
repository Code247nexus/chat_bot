


import streamlit as st 
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gtts import gTTS
from fpdf import FPDF
import base64
from datetime import datetime


# Initialize Groq Model
llm = ChatGroq(
    temperature=0.3,
    groq_api_key=st.secrets["GROQ_API_KEY"],
    model_name="openai/gpt-oss-120b"
)

DEFAULT_PROMPT = """You are Robin, an AI legal information assistant for Indian law.
- Answer using Indian laws: the Constitution of India, the Bharatiya Nyaya Sanhita (BNS), Bharatiya Nagarik Suraksha Sanhita (BNSS), Bharatiya Sakshya Adhiniyam (BSA), Consumer Protection Act 2019, IT Act 2000, etc.
- Note: BNS, BNSS and BSA replaced the IPC, CrPC and Evidence Act from 1 July 2024. Mention the old section only as a reference.
- Explain in simple language. Cite the Act and section only when you are confident.
- If you are not sure, say so. Never invent sections or case names.
- You give general legal information, not legal advice. Suggest consulting a qualified advocate for specific situations."""

# Initialize conversation history
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  
if "messages" not in st.session_state:
    st.session_state.messages = []   
    
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
    def clean(t):
        return t.encode("latin-1", "replace").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt="Robin - Conversation History", ln=True, align="C")
    pdf.ln(10)
    for convo in conversations:
        pdf.multi_cell(0, 8, txt=clean(convo))
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
st.sidebar.write("Robin is an AI legal assistant for Indian law, powered by GPT-OSS 120B via the Groq API. It gives general information, can make mistakes, and is not legal advice. Please consult a qualified advocate.")

# System prompt input (optional)
#system_prompt = st.sidebar.text_area("System Prompt (optional)", 
 #                                    "You are a helpful AI assistant. Answer the user's queries politely and informatively.")
st.title("🤖 Robin - AI Legal Assistant (Indian Law)")

st.sidebar.header("About")
st.sidebar.write(
    "Robin gives general information on Indian law using an LLM via the Groq API. "
    "It can make mistakes and is not legal advice. Please consult a qualified advocate."
)

system_prompt = st.sidebar.text_area("System Prompt (optional)", DEFAULT_PROMPT, height=300)

if st.sidebar.button("Clear conversation"):
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.rerun()

user_query = st.text_area("Enter your legal query:")

if st.button("Get Response"):
    if user_query.strip():
        with st.spinner("Thinking..."):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # System prompt + last 10 messages (memory) + new question
            msgs = [SystemMessage(content=system_prompt)]
            msgs += st.session_state.messages[-10:]
            msgs.append(HumanMessage(content=user_query))

            try:
                response = llm.invoke(msgs)
            except Exception:
                st.error("Could not get a response. Please try again in a moment.")
                st.stop()

            if response.content:
                st.success("Response:")
                st.write(response.content)

                # Memory for the model
                st.session_state.messages.append(HumanMessage(content=user_query))
                st.session_state.messages.append(AIMessage(content=response.content))

                # Log for the PDF
                st.session_state.conversation_history.append(
                    f"[{timestamp}]\nUser: {user_query}\nRobin: {response.content}\n"
                )

                try:
                    audio_file = text_to_speech(response.content)
                    st.write("🔊 Listen to the response:")
                    play_audio(audio_file)
                except Exception:
                    st.info("Audio is unavailable for this response.")
            else:
                st.error("No response received.")
    else:
        st.warning("Please enter a query.")





