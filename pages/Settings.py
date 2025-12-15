import streamlit as st
from config_manager import load_config, save_config

st.set_page_config(layout="wide", page_title="Settings - Triple AI Chat")

st.title("Settings")

# Load current config
config = load_config()

st.header("Global API Keys")
with st.expander("Configure Standard Providers", expanded=True):
    gemini_key = st.text_input(
        "Gemini API Key",
        value=config.get("gemini_key", ""),
        type="password"
    )
    openai_key = st.text_input(
        "OpenAI API Key",
        value=config.get("openai_key", ""),
        type="password"
    )

st.header("Custom OpenAI-Compatible Providers")
st.write("Add your own providers (e.g., LocalAI, Together AI, etc.)")

# Session state to manage the temporary list of providers before saving
if "custom_providers" not in st.session_state:
    st.session_state.custom_providers = config.get("custom_providers", [])

# Function to add a new empty provider
def add_provider():
    st.session_state.custom_providers.append({
        "name": f"New Provider {len(st.session_state.custom_providers) + 1}",
        "base_url": "http://localhost:8000/v1",
        "api_key": ""
    })

# Display and edit existing custom providers
providers_to_remove = []
for i, provider in enumerate(st.session_state.custom_providers):
    with st.expander(f"Provider {i+1}: {provider.get('name', 'Unnamed')}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            provider["name"] = st.text_input(f"Name #{i}", value=provider.get("name", ""), key=f"name_{i}")
            provider["base_url"] = st.text_input(f"Base URL #{i}", value=provider.get("base_url", ""), key=f"url_{i}", help="e.g., http://localhost:8000/v1")
        with col2:
            provider["api_key"] = st.text_input(f"API Key #{i}", value=provider.get("api_key", ""), type="password", key=f"key_{i}")

        if st.button("Remove Provider", key=f"remove_{i}"):
            providers_to_remove.append(i)

# Process removals
if providers_to_remove:
    for i in sorted(providers_to_remove, reverse=True):
        del st.session_state.custom_providers[i]
    st.rerun()

if st.button("Add New Custom Provider"):
    add_provider()
    st.rerun()

st.markdown("---")

if st.button("Save Settings", type="primary"):
    new_config = {
        "gemini_key": gemini_key,
        "openai_key": openai_key,
        "custom_providers": st.session_state.custom_providers
    }
    save_config(new_config)
    st.success("Settings saved successfully!")
