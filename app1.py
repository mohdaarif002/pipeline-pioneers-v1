# app.py
import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from helpers import read_uploaded_file, memory_usage_mb, basic_profile
from processing import default_config, apply_preview
from llm import GroqLangChain, GROQ_AVAILABLE
from config import PROMPT_TEMPLATE

st.set_page_config(page_title="CSV Cleaner + LLM Code Generator", layout="wide")
st.title("🧹 CSV Cleaner & LLM Code Generator")

upload = st.file_uploader("📤 Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
if not upload:
    st.info("Upload a CSV or Excel file to begin.")
    st.stop()

with st.spinner("Reading upload..."):
    df = read_uploaded_file(upload)

st.success("File loaded!")
st.dataframe(df.head(), use_container_width=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Rows", f"{len(df):,}")
col2.metric("Columns", f"{df.shape[1]:,}")
col3.metric("Duplicates", f"{df.duplicated().sum():,}")
col4.metric("Memory (MB)", f"{memory_usage_mb(df)}")

with st.expander("🔎 Quick column profile", expanded=True):
    prof = basic_profile(df)
    st.dataframe(prof, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("🧩 Column Cleaning Options (editable table)")

cfg_df = default_config(prof)
edited = st.data_editor(cfg_df, use_container_width=True, num_rows="fixed", hide_index=True)

# preview
if st.button("🧪 Preview cleaning (apply in-session)"):
    preview_df = apply_preview(df, edited, st.session_state.get("global_conditions", None))
    st.dataframe(preview_df.head(100), use_container_width=True)

# LLM section
st.markdown("---")
st.subheader("🔮 Generate code with Groq (via LangChain wrapper)")
if not GROQ_AVAILABLE:
    st.warning("The `groq` package is not available in this environment. Install it to enable code generation.")

api_key_input = st.text_input("Groq API Key (paste here to set for this session)", type="password")
if api_key_input:
    os.environ["GROQ_API_KEY"] = api_key_input

groq_api_key = os.getenv("GROQ_API_KEY")
model = st.selectbox("Model", options=["compound-beta", "compound-beta-mini", "llama3-70b-8192"], index=0)

col_cfg_json = edited.to_json(orient="records")
global_cfg_json = json.dumps(st.session_state.get("global_conditions", []))

if st.button("🔮 Generate code with Groq (via LangChain wrapper)"):
    if not groq_api_key:
        st.error("Groq API key missing. Set it above or export GROQ_API_KEY in environment.")
    elif not GROQ_AVAILABLE:
        st.error("`groq` package not available.")
    else:
        llm = GroqLangChain(api_key=groq_api_key, model=model)
        prompt = PROMPT_TEMPLATE.format(column_config=col_cfg_json, global_conditions=global_cfg_json)
        generated = llm(prompt)
        if generated:
            st.code(generated, language="python")
            st.download_button("⬇️ Download generated script", data=generated.encode("utf-8"), file_name="generated_cleaning.py", mime="text/x-python")
