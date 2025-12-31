import streamlit as st
import pandas as pd
import plotly.express as px


# PAGE CONFIG
st.set_page_config(
    page_title="Personal UPI Usage & Financial Analyzer",
    layout="wide"
)


# HEADER
st.title("💰 Personal UPI Usage & Financial Analyzer")
st.caption("AI-powered spending insights & personalized financial advice")

st.write("")  # spacing


# FILE UPLOADER (DRAG & DROP)

uploaded_file = st.file_uploader(
    "📂 Upload UPI CSV (Paytm / GPay / PhonePe)",
    type=["csv"]
)


# PRE-UPLOAD SCREEN

if uploaded_file is None:
    st.info("⬆️ Upload a CSV file to begin analysis")
    st.markdown("---")
    st.caption("FinTech | NLP | LLMs | Streamlit | Hugging Face Ready")
    st.stop()  # stop execution until a file is uploaded


# LOAD CSV

df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.strip().str.lower()  # normalize column names


# SAFE COLUMN HANDLING
# Amount column
if "amount (inr)" in df.columns:
    df["amount (inr)"] = (
        df["amount (inr)"].astype(str).str.replace(",", "", regex=False)
    )
    df["amount (inr)"] = pd.to_numeric(df["amount (inr)"], errors="coerce").fillna(0)
else:
    st.error("CSV must contain 'amount (inr)' column")
    st.stop()

# Timestamp column
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# Merchant category
if "merchant_category" not in df.columns:
    df["merchant_category"] = "Other"


# DATA PREVIEW
st.subheader("📄 UPI Transaction Preview")
st.dataframe(df.head(10), use_container_width=True)


# KEY FINANCIAL METRICS
st.subheader("📊 Key Financial Metrics")
c1, c2, c3, c4 = st.columns(4)

total_txn = len(df)
total_spend = df["amount (inr)"].sum()
avg_spend = df["amount (inr)"].mean()
max_spend = df["amount (inr)"].max()

c1.metric("Total Transactions", total_txn)
c2.metric("Total Spend (₹)", round(total_spend, 2))
c3.metric("Average Spend (₹)", round(avg_spend, 2))
c4.metric("Highest Transaction (₹)", round(max_spend, 2))


# CATEGORY-WISE SPENDING
st.subheader("📊 Category-wise Spending")
cat_df = (
    df.groupby("merchant_category")["amount (inr)"]
    .sum()
    .reset_index()
    .sort_values(by="amount (inr)", ascending=False)
)

fig = px.bar(
    cat_df,
    x="merchant_category",
    y="amount (inr)",
    title="Spending by Merchant Category"
)
st.plotly_chart(fig, use_container_width=True)


# MONTHLY SPENDING TREND
st.subheader("📈 Monthly Spending Trend")
if "timestamp" in df.columns:
    trend_df = df.dropna(subset=["timestamp"])
    trend_df["month"] = trend_df["timestamp"].dt.to_period("M").astype(str)
    month_df = trend_df.groupby("month")["amount (inr)"].sum().reset_index()

    fig = px.line(
        month_df,
        x="month",
        y="amount (inr)",
        markers=True,
        title="Monthly Spending Trend"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Date column not available")


# WASTEFUL SPENDING (REALISTIC)
st.subheader("⚠️ Potential Wasteful Spending")
waste_keywords = [
    "restaurant", "movies",
    "entertainment", "shopping", "junk", "snacks"
]

waste_df = df[
    df["merchant_category"].str.lower().str.contains(
        "|".join(waste_keywords), na=False
    )
]

if not waste_df.empty:
    st.warning(f"{len(waste_df)} unnecessary transactions detected")
    st.dataframe(
        waste_df[["merchant_category", "amount (inr)"]],
        use_container_width=True
    )
else:
    st.success("No major wasteful spending detected 🎉")


# PERSONALIZED FINANCIAL ADVICE

st.subheader("🤖 Personalized Financial Advice")


st.write("✔️ Save at least 20% of income")
st.write("✔️ Reduce shopping & entertainment expenses")
st.write("✔️ Avoid impulse UPI payments")


# FOOTER
st.markdown("---")
st.caption("FinTech Project | Personal Finance Automation | Streamlit")
