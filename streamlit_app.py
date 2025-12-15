import streamlit as st
import asyncio
from config_manager import load_config, get_provider_config
from model_utils import get_available_models, get_response

# Must be the first Streamlit command
st.set_page_config(layout="wide", page_title="Triple AI Chat")

# --- Custom CSS ---
st.markdown("""
    <style>
        .stTextInput > div > div > input {
            background-color: #f0f2f6;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Triple AI Chat Interface")

# --- Configuration & Setup ---
config = load_config()

# Construct the list of available providers
# Format: {"Display Name": "Internal Name/Identifier"}
# Fixed standard providers
providers_map = {}

# Only add Gemini/OpenAI if keys are present (or allow selection to show "Configure in Settings")
# Actually, better to always show them but they might fail if no key.
providers_map["Gemini"] = "Gemini"
providers_map["OpenAI"] = "OpenAI"

# Add Custom Providers
for p in config.get("custom_providers", []):
    providers_map[p["name"]] = p["name"]

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = {
        "col1": [],
        "col2": [],
        "col3": []
    }

if "column_configs" not in st.session_state:
    st.session_state.column_configs = {
        "col1": {"provider": "Gemini", "model": None},
        "col2": {"provider": "Gemini", "model": None},
        "col3": {"provider": "Gemini", "model": None}
    }

# --- Helper to get models for a provider ---
@st.cache_data(ttl=60) # Cache for a minute to avoid constant fetching
def fetch_models_cached(provider_name):
    p_config = get_provider_config(provider_name, config)
    # Since get_available_models is async, we need to run it in a loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        models = loop.run_until_complete(get_available_models(p_config))
        loop.close()
        return models
    except Exception as e:
        return []

# --- Layout ---
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]
col_ids = ["col1", "col2", "col3"]

# Render Columns
active_configs = [] # To store (provider_config, model, col_id) for execution

for i, col in enumerate(cols):
    col_id = col_ids[i]
    with col:
        st.subheader(f"Agent {i+1}")

        # Provider Selection
        current_provider = st.session_state.column_configs[col_id]["provider"]
        # Ensure current provider is still valid (e.g. if custom provider was deleted)
        if current_provider not in providers_map:
            current_provider = "OpenAI" # Fallback

        selected_provider = st.selectbox(
            "Provider",
            options=list(providers_map.keys()),
            index=list(providers_map.keys()).index(current_provider) if current_provider in providers_map else 0,
            key=f"provider_{col_id}"
        )

        # Update session state if changed
        if selected_provider != st.session_state.column_configs[col_id]["provider"]:
             st.session_state.column_configs[col_id]["provider"] = selected_provider
             # Reset model when provider changes
             st.session_state.column_configs[col_id]["model"] = None
             # We might want to rerun to fetch models immediately?
             # Streamlit reruns on widget change, so next pass handles it.

        # Model Selection
        available_models = fetch_models_cached(selected_provider)

        current_model = st.session_state.column_configs[col_id]["model"]
        if not available_models:
            st.warning("No models found. Check Settings.")
            selected_model = None
        else:
            index = 0
            if current_model in available_models:
                index = available_models.index(current_model)

            selected_model = st.selectbox(
                "Model",
                available_models,
                index=index,
                key=f"model_{col_id}"
            )

        st.session_state.column_configs[col_id]["model"] = selected_model

        # Store for execution
        active_configs.append({
            "col_id": col_id,
            "provider_name": selected_provider,
            "model": selected_model
        })

        # Chat History
        with st.container(height=500, border=True):
            for msg in st.session_state.messages[col_id]:
                if msg["role"] == "user":
                    st.info(f"You: {msg['content']}")
                else:
                    st.success(f"{selected_provider}: {msg['content']}")

# --- Input Area ---
input_col, clear_col = st.columns([6, 1])

# We use session state to clear the input after submission
if "input_text" not in st.session_state:
    st.session_state.input_text = ""

def submit_input():
    st.session_state.input_text = st.session_state.widget_input
    st.session_state.widget_input = "" # Clear the widget

with input_col:
    st.text_input("Message", key="widget_input", on_change=submit_input, label_visibility="collapsed")

with clear_col:
    if st.button("Clear"):
        for cid in col_ids:
            st.session_state.messages[cid] = []
        st.rerun()

# --- Execution Logic ---
if st.session_state.input_text:
    user_input = st.session_state.input_text
    st.session_state.input_text = "" # Clear processed input to prevent loop
    
    # Add user message to all columns
    for cid in col_ids:
        st.session_state.messages[cid].append({"role": "user", "content": user_input})
    
    async def run_all_chats():
        tasks = []
        for cfg in active_configs:
            col_id = cfg["col_id"]
            prov_name = cfg["provider_name"]
            model = cfg["model"]

            if not model:
                tasks.append(asyncio.create_task(asyncio.sleep(0, result="Please select a model.")))
                continue

            prov_config = get_provider_config(prov_name, config)
            # Pass full history
            history = st.session_state.messages[col_id]

            tasks.append(
                get_response(prov_config, model, history)
            )

        return await asyncio.gather(*tasks)

    with st.spinner("Fetching responses..."):
        try:
            # Create a new event loop for async execution within this sync context
            results = asyncio.run(run_all_chats())

            for i, res in enumerate(results):
                col_id = col_ids[i]
                st.session_state.messages[col_id].append({
                    "role": "assistant",
                    "content": str(res) # Ensure string
                })

        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.rerun()
