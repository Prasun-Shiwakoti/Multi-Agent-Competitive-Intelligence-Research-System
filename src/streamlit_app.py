import streamlit as st
import json
from coordinator import CoordinatorAgent

st.set_page_config(page_title="Competitive Intelligence Dashboard", layout="centered")
st.title("Multi-Agent Competitive Intelligence Research System")

# Sidebar parameters

product_options = ["Notion AI", "ChatGPT", "Grammarly", "GitHub Copilot", "Other"]

st.sidebar.header("Settings")
product_choice = st.sidebar.selectbox("Product/Topic", product_options, index=0)
num_results = st.sidebar.slider("Number of results", 1, 10, 5)
max_age = st.sidebar.slider("Max age (months)", 1, 12, 6)

if product_choice == "Other":
    custom_product = st.text_input("Enter custom product/topic name:", "")
    product_name = custom_product.strip()
else:
    product_name = product_choice


# Main input
query = st.text_input("Enter your search query:", f"{product_name or '.....'} new features 2025")

if st.button("Run Pipeline"):
    if not query:
        st.error("Please enter a search query.")
    else:
        with st.spinner("Running agents... this may take a moment"):
            agent = CoordinatorAgent(
                product_name=product_name,
                num_results=num_results,
                max_months_old=max_age,
                output_dir="outputs"
            )
            results = agent.run(query=query)

            try:
                results = json.loads(json.dumps(results, default=str))
            except Exception:
                pass


        if results:
            st.success(f"Retrieved {len(results)} updates.")
            
            df = st.dataframe(results)
           
            st.subheader("JSON Output:")
            st.json(results)
        else:
            st.warning("No valid updates found.")

st.sidebar.markdown("---")
st.sidebar.write("Developed by Prasun Shiwakoti")