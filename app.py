import gradio as gr
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt

# -------- PDF TEXT EXTRACTION --------
def extract_text(pdf):
    lines = []
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))
    return lines

# -------- CATEGORY NLP --------
def categorize(text):
    t = text.lower()
    if any(x in t for x in ["grocery", "milk", "vegetable", "supermarket"]):
        return "Grocery"
    if any(x in t for x in ["electricity", "water", "gas", "recharge", "bill"]):
        return "Bills"
    if any(x in t for x in ["swiggy", "zomato", "restaurant", "food"]):
        return "Food"
    if any(x in t for x in ["movie", "netflix", "spotify", "entertainment"]):
        return "Entertainment"
    if any(x in t for x in ["amazon", "flipkart", "shopping"]):
        return "Shopping"
    if any(x in t for x in ["uber", "ola", "cab"]):
        return "Travel"
    return "Others"

# -------- LLM STYLE ADVICE --------
def ai_advice(summary, waste_count):
    if summary.empty:
        return "No sufficient transaction data found for insights."

    top = summary.iloc[0]["Category"]
    return f"""
🔍 AI Financial Insight

• Highest spending category: **{top}**
• Wasteful transactions: **{waste_count}**
• Reduce impulse & entertainment spending
• Save at least **20% monthly income**

(LLM-style financial reasoning)
"""

# -------- MAIN ANALYSIS FUNCTION --------
def analyze(pdf):
    if pdf is None:
        return "No file uploaded", None, None, "No insights"

    raw = extract_text(pdf.name)

    rows = [l for l in raw if re.search(r"\d+\.\d{2}", l)]

    if not rows:
        return "No valid transactions detected", None, None, "No insights"

    df = pd.DataFrame(rows, columns=["Transaction"])
    df["Amount"] = df["Transaction"].str.extract(r"([\d,]+\.?\d*)")[0]
    df["Amount"] = df["Amount"].str.replace(",", "").astype(float)
    df["Category"] = df["Transaction"].apply(categorize)

    # -------- CATEGORY SUMMARY --------
    summary = df.groupby("Category")["Amount"].sum().reset_index()
    summary = summary.sort_values("Amount", ascending=False)

    # -------- BAR CHART --------
    fig, ax = plt.subplots()
    ax.bar(summary["Category"], summary["Amount"])
    ax.set_title("Category-wise Spending")
    ax.set_ylabel("Amount")
    ax.set_xlabel("Category")
    plt.xticks(rotation=30)

    # -------- WASTEFUL SPENDING --------
    wasteful = df[
        (df["Category"] == "Entertainment") |
        ((df["Category"] == "Shopping") & (df["Amount"] < 500))
    ]

    advice = ai_advice(summary, len(wasteful))

    return df, fig, wasteful, advice

# -------- GRADIO UI --------
gr.Interface(
    fn=analyze,
    inputs=gr.File(label="📄 Upload UPI PDF", file_types=[".pdf"]),
    outputs=[
        gr.Dataframe(label="📄 Transactions"),
        gr.Plot(label="📊 Category Summary"),
        gr.Dataframe(label="⚠ Wasteful Spending"),
        gr.Markdown(label="🤖 AI Advice"),
    ],
    title="💰 Personal UPI Usage & Financial Analyzer (LLM-Based)",
    description="Upload UPI PDF (Paytm / GPay / PhonePe). NLP-based financial analysis.",
).launch()
