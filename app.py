import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from dotenv import load_dotenv

# Optional AI
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except:
    GROQ_AVAILABLE = False

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page Setting
st.set_page_config(
    page_title="Konsultan Usaha UMKM",
    layout="wide",
    page_icon="💼"
)

st.title("💼 Aplikasi Konsultan Usaha UMKM")
st.write("Analisis Keuangan, Variance, KPI, & Insight Otomatis")

# Upload Section
uploaded_file = st.file_uploader("📂 Upload file Excel (.xlsx)", type=["xlsx"])

if not uploaded_file:
    st.info("Silakan upload file Excel Anda.")
    st.stop()

try:
    df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Gagal membaca Excel: {e}")
    st.stop()

# Normalisasi nama kolom
df.columns = [c.strip() for c in df.columns]

required_cols = ["Category", "Budget", "Actual"]
if not all(col in df.columns for col in required_cols):
    st.error("File harus mengandung kolom: Category, Budget, Actual")
    st.stop()

# Convert numeric
for col in ["Budget", "Actual"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Variance
df["Variance"] = df["Actual"] - df["Budget"]
df["Variance %"] = np.where(df["Budget"] == 0, np.nan, (df["Variance"] / df["Budget"]) * 100)

st.subheader("📋 Data & Variance")
st.dataframe(df, use_container_width=True)

# KPI Summary
total_budget = df["Budget"].sum()
total_actual = df["Actual"].sum()
total_variance = total_actual - total_budget
total_var_pct = (total_variance / total_budget * 100) if total_budget != 0 else 0

c = st.columns(3)
c[0].metric("Total Budget", f"Rp {total_budget:,.0f}")
c[1].metric("Total Actual", f"Rp {total_actual:,.0f}")
c[2].metric("Total Variance", f"Rp {total_variance:,.0f}", f"{total_var_pct:.2f}%")

# Grafik
st.subheader("📈 Visualisasi Variance")
fig = px.bar(
    df,
    x="Category",
    y="Variance",
    title="Variance per Category",
    color="Variance",
    text_auto=True
)
st.plotly_chart(fig, use_container_width=True)

# AI Insight
st.subheader("🤖 Insight Otomatis (AI)")

if not GROQ_AVAILABLE or not GROQ_API_KEY:
    st.warning("Groq API tidak aktif. Tambahkan GROQ_API_KEY pada .env")
else:
    try:
        client = Groq(api_key=GROQ_API_KEY)

        summary_text = (
            f"Total Budget: {total_budget}\n"
            f"Total Actual: {total_actual}\n"
            f"Total Variance: {total_variance}\n"
            "Berikan insight bisnis yang jelas dan actionable untuk UMKM."
        )

        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Anda adalah konsultan usaha UMKM profesional."},
                {"role": "user", "content": summary_text}
            ]
        )

        st.write(res.choices[0].message.content)

    except Exception as e:
        st.error(f"Error AI: {e}")

# Download Excel Hasil
def to_excel(df):
    from io import BytesIO
    import openpyxl

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, index=False)
    writer.close()
    return output.getvalue()

st.download_button(
    "⬇️ Download Hasil Analisis (Excel)",
    data=to_excel(df),
    file_name="umkm_analysis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
