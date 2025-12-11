import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import AsyncOpenAI
from groq import AsyncGroq

# Set up the Streamlit page (must be first Streamlit command)
st.set_page_config(layout="wide", page_title="Triple AI Chat")

# Load environment variables
load_dotenv()

# Configure Google API client
# OpenAI and Groq clients will be initialized asynchronously where needed or here if they are thread-safe/async-compatible globally.
# Typically AsyncOpenAI/AsyncGroq are lightweight to instantiate per request or globally.
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Cached function to get available Gemini models
@st.cache_data
def get_gemini_models():
    try:
        models = genai.list_models()
        return [m.name for m in models if 'gemini' in m.name]
    except Exception as e:
        # Don't show error on UI during model fetch to avoid clutter, just log or return fallback
        print(f"Error fetching Gemini models: {str(e)}")
        return ['gemini-pro']  # Fallback

# Cached function to get available OpenAI models
@st.cache_data
def get_openai_models():
    try:
        # We need a synchronous client for this list call.
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        return [m.id for m in models if m.id.startswith(('gpt-3.5', 'gpt-4'))]
    except Exception as e:
        print(f"Error fetching OpenAI models: {str(e)}")
        return ['gpt-3.5-turbo']  # Fallback

# Cached function to get available Groq models
@st.cache_data
def get_groq_models():
    try:
        # List of currently available models from Groq documentation
        available_models = [
            'mixtral-8x7b-32768',
            'llama2-70b-32768',
            'gemma-7b-it',
            'llama2-13b-32768',
            'llama2-7b-32768',
            'llama3-8b-8192',
            'llama3-70b-8192'
        ]
        return available_models
    except Exception as e:
        print(f"Error fetching Groq models: {str(e)}")
        return ['mixtral-8x7b-32768']  # Fallback

# Async functions to get responses
async def get_gemini_response(model_name, prompt):
    try:
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

async def get_openai_response(model_name, prompt):
    try:
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def get_groq_response(model_name, prompt):
    try:
        client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def get_all_responses(gemini_model, openai_model, groq_model, prompt):
    return await asyncio.gather(
        get_gemini_response(gemini_model, prompt),
        get_openai_response(openai_model, prompt),
        get_groq_response(groq_model, prompt)
    )

# Get available models
GEMINI_MODELS = get_gemini_models()
OPENAI_MODELS = get_openai_models()
GROQ_MODELS = get_groq_models()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {
        "gemini": [],
        "openai": [],
        "groq": []
    }
if "current_input" not in st.session_state:
    st.session_state.current_input = None

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stTextInput > div > div > input {
            background-color: #f0f2f6;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Triple AI Chat Interface")

# Create three columns for the chat interfaces
col1, col2, col3 = st.columns(3)

# Left pane (Gemini)
with col1:
    st.subheader("Gemini")
    gemini_model = st.selectbox(
        "Select Gemini Model",
        GEMINI_MODELS,
        key="gemini_model"
    )
    
    with st.container(height=500, border=True):
        for msg in st.session_state.messages["gemini"]:
            if msg["role"] == "user":
                st.info(f"You: {msg['content']}")
            else:
                st.success(f"Gemini: {msg['content']}")

# Middle pane (OpenAI)
with col2:
    st.subheader("OpenAI")
    openai_model = st.selectbox(
        "Select OpenAI Model",
        OPENAI_MODELS,
        key="openai_model"
    )
    
    with st.container(height=500, border=True):
        for msg in st.session_state.messages["openai"]:
            if msg["role"] == "user":
                st.info(f"You: {msg['content']}")
            else:
                st.success(f"OpenAI: {msg['content']}")

# Right pane (Groq)
with col3:
    st.subheader("Groq")
    groq_model = st.selectbox(
        "Select Groq Model",
        GROQ_MODELS,
        key="groq_model"
    )
    
    with st.container(height=500, border=True):
        for msg in st.session_state.messages["groq"]:
            if msg["role"] == "user":
                st.info(f"You: {msg['content']}")
            else:
                st.success(f"Groq: {msg['content']}")

# Input area
col4, col5 = st.columns([6, 1])
with col4:
    if "input_value" not in st.session_state:
        st.session_state.input_value = ""
    
    def submit():
        if st.session_state.user_input:
            st.session_state.input_value = st.session_state.user_input
            st.session_state.user_input = ""
    
    user_input = st.text_input(
        "Message",
        key="user_input",
        label_visibility="collapsed",
        on_change=submit
    )

with col5:
    if st.button("Clear"):
        st.session_state.messages = {"gemini": [], "openai": [], "groq": []}
        st.session_state.current_input = None
        st.session_state.input_value = ""
        st.rerun()

# Handle user input
if st.session_state.input_value and st.session_state.input_value != st.session_state.current_input:
    current_input = st.session_state.input_value
    st.session_state.current_input = current_input
    st.session_state.input_value = ""
    
    # Add user message to all conversations
    for model in ["gemini", "openai", "groq"]:
        st.session_state.messages[model].append({
            "role": "user",
            "content": current_input
        })
    
    # Run async requests in parallel
    with st.spinner("Fetching responses from all models..."):
        try:
            gemini_res, openai_res, groq_res = asyncio.run(get_all_responses(
                gemini_model, openai_model, groq_model, current_input
            ))

            st.session_state.messages["gemini"].append({
                "role": "assistant",
                "content": gemini_res
            })

            st.session_state.messages["openai"].append({
                "role": "assistant",
                "content": openai_res
            })

            st.session_state.messages["groq"].append({
                "role": "assistant",
                "content": groq_res
            })

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    st.rerun()
