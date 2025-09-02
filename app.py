import os
import streamlit as st
from groq import Groq
from tavily import TavilyClient


# SETUP KEYS


groq_api_key = st.secrets["GROQ_API_KEY"]
tavily_api_key = st.secrets["TAVILY_API_KEY"]



if not groq_api_key or not tavily_api_key:
    st.error("❌ Please set GROQ_API_KEY and TAVILY_API_KEY as environment variables")
    st.stop()

# Initialize clients
groq_client = Groq(api_key=groq_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)


# STREAMLIT APP UI

st.set_page_config(page_title="📈 Stock Analyzer Agent", layout="centered")
st.title("📈 AI Finance Copilot")
""""
YOUR AI-POWERED ASSISTANT FOR STOCK ANALYSIS
"""

st.markdown("Enter a stock ticker (e.g., **AAPL**, **TSLA**, **MSFT**) to get the latest news & AI-driven insights.")

ticker = st.text_input("Stock Symbol:", value="TSLA")

if st.button("🔍 Analyze Stock"):
    with st.spinner("Fetching latest market data..."):
        try:

            # Step 1: Search news

            query = f"{ticker} stock latest news 2025"
            search_results = tavily_client.search(query=query, max_results=5)

            if not search_results or "results" not in search_results:
                st.error("⚠️ No search results found. Try another stock symbol.")
                st.stop()

            news_texts = "\n\n".join(
                [f"- {res['title']}: {res['url']}" for res in search_results["results"]]
            )


            # Step 2: Build prompt

            final_prompt = f"""
You are an AI Stock Analyst. Based on the following latest news about **{ticker}**, provide:

1. 📊 Stock sentiment (Positive, Neutral, or Negative).
2. 📰 Key insights (summarize latest events).
3. 💡 Investment suggestion (short-term and long-term).
4. ⚠️ Risks to consider.

News Sources:
{news_texts}
"""


            # Step 3: Call Groq LLM

            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",  # ✅ stable model
                messages=[
                    {"role": "system", "content": "You are a professional stock analyst."},
                    {"role": "user", "content": final_prompt},
                ],
                temperature=0.4,
                max_tokens=500,
                stream=False
            )

            ai_output = response.choices[0].message.content


            # Step 4: Display Results

            st.subheader(f"📊 Analysis for {ticker}")
            st.write(ai_output)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
