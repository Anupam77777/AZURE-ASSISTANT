import streamlit as st
import base64

# ==== Set a Custom Background from Local Image + Modern CSS ====
def set_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .bot-card {{
            text-align: center;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 18px;
            margin: 10px;
            background: rgba(0,0,0,0.35);
            transition: all 0.2s ease-in-out;
        }}
        .bot-card:hover {{
            background: rgba(37, 99, 235, 0.25);
            transform: translateY(-4px);
        }}
        .bot-label {{
            font-size: 1rem !important;
            color: #e0e7ff !important;
            font-weight: 600;
        }}
        .bot-icon {{
            font-size: 1.8rem;
            display: block;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==== Apply the background ====
set_bg_from_local("https://github.com/Anupam77777/AZURE-ASSISTANT/blob/main/CLOUD%20INTREGATOR%20BOT/images/background_AI_2.jpg")

# ==== Streamlit Page Config ====
st.set_page_config(
    page_title="BAU ASSISTANT",
    page_icon="☁️",
    layout="wide"
)

# ==== Sidebar Layout ====
with st.sidebar:
    st.image("C:/Users/Anupam/OneDrive/Desktop/CLOUD INTREGATOR BOT/images/azure_logo.png", width=160)
    st.markdown("## ☁️ Welcome to BAU Assistant")
    st.divider()
    st.markdown("### 📚 Useful Links")
    st.markdown("[Microsoft Docs](https://learn.microsoft.com/)")
    st.markdown("[Azure Advisor](https://portal.azure.com/#blade/Microsoft_Azure_Advisor/AzureAdvisorBrowseBlade)")
    st.markdown("[Perplexity AI](https://www.perplexity.ai/)")
    with st.expander("💡 Suggestion Box"):
        st.text_area("Got an idea? Share your suggestion here:")
    st.markdown("---")
    st.markdown("Made with ❤ by Cloud Exponence Team")
    st.markdown("---")
    st.markdown("*POWERED BY TCS*")

# ==== Main Header ====
st.image("C:/Users/Anupam/OneDrive/Desktop/CLOUD INTREGATOR BOT/images/azure_logo.png", width=200)
st.title("☁️ BAU ASSISTANT")
st.subheader("Your all-in-one Azure Cloud operations assistant.")
st.markdown("This app simplifies your Azure day-to-day tasks — select any of the intelligent automation bots below.")
st.markdown("---")

# ==== Bot Navigation Pages ====
bot_pages = [
    ("pages/RAG bot.py", "RAG BOT - PDF Reader", "📘"),
    ("pages/IP Allocater.py", "IP Address Allocator", "🌐"),
    ("pages/file converter.py", "File Converter", "🛠️"),
    ("pages/azure server controler console.py", "Azure Server Console", "🖥️"),
    ("pages/VM patch status.py", "VM Patching Status", "⚙️"),
    ("pages/MY Server Vulnerabilities.py", "MY Server Vulnerabilities", "🛡️"),
    ("pages/SERVER UPTIME STATUS.py", "VM UPTIME", "🔍"),
    ("pages/KNOW YOUR TAGS.py", "KNOW YOUR TAGS", "🏷️"),
]

# Arrange the bots evenly (rows of 3 but fully centered)
cols_per_row = 3
rows = [bot_pages[i:i + cols_per_row] for i in range(0, len(bot_pages), cols_per_row)]
for row in rows:
    cols = st.columns(cols_per_row)
    for i, (page, label, icon) in enumerate(row):
        with cols[i]:
            st.markdown(
                f"""
                <div class="bot-card">
                    <span class="bot-icon">{icon}</span>
                    <div class="bot-label">{label}</div>
                    <br>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.page_link(page, label=f"Open {label}")

st.markdown("---")

# ==== External Links ====
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🧾 Azure Pricing Calculator"):
        st.components.v1.html("<script>window.open('https://azure.microsoft.com/en-us/pricing/calculator/','_blank')</script>", height=0)
with col2:
    if st.button("📚 Microsoft Learning"):
        st.components.v1.html("<script>window.open('https://learn.microsoft.com/','_blank')</script>", height=0)
with col3:
    if st.button("🧠 Perplexity AI"):
        st.components.v1.html("<script>window.open('https://www.perplexity.ai/','_blank')</script>", height=0)

