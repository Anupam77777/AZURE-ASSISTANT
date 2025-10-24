import streamlit as st
import pandas as pd
import os

# Path to your Excel file
EXCEL_PATH = r"C:\Users\Anupam\OneDrive\Desktop\CLOUD INTREGATOR BOT\VULF\VUL.xlsx"

@st.cache_data
def load_data(path):
    if not os.path.exists(path):
        st.error(f"Excel file not found at path: {path}")
        return pd.DataFrame()
    df = pd.read_excel(path)
    required_cols = ['IP', 'DNS', 'Server Owner', 'Support Team']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        st.error(f"Excel missing columns: {missing_cols}")
        return pd.DataFrame()
    return df[required_cols]

st.title("Azure Servers Vulnerabilities By Owner")

df = load_data(EXCEL_PATH)

if df.empty:
    st.warning("No data loaded. Check Excel path and columns.")
else:
    # User types owner name to search for (case-insensitive substring)
    owner_query = st.text_input("Type your name (Owner) to search for your servers")

    if owner_query:
        filtered = df[df['Server Owner'].str.contains(owner_query, case=False, na=False)]
        if filtered.empty:
            st.info(f"No records found matching owner name: {owner_query}")
        else:
            st.write(f"Showing servers and vulnerabilities matching owner: '{owner_query}'")
            st.dataframe(filtered.reset_index(drop=True))
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")

