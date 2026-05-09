import streamlit as st
import duckdb
import pandas as pd
import altair as alt
import sys
import os

# Add parent directory to path to import agentic workflow
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_workflows.agentic_analyst import AgenticDataAnalyst

# Set page config
st.set_page_config(page_title="E-commerce Analytics & AI Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a View:", ["Executive Scorecard", "AI Data Assistant"])

@st.cache_data
def load_data():
    con = duckdb.connect('../ecommerce.duckdb')
    fct_orders = con.execute("SELECT * FROM fct_orders").df()
    dim_customers = con.execute("SELECT * FROM dim_customers").df()
    dim_products = con.execute("SELECT * FROM dim_products").df()
    con.close()
    return fct_orders, dim_customers, dim_products

if page == "Executive Scorecard":
    st.title("Executive Scorecard")
    st.markdown("A demonstration of governed KPI reporting, BI platforms, and semantic metric definitions.")
    
    try:
        fct_orders, dim_customers, dim_products = load_data()
        
        st.header("Governed KPIs")
        col1, col2, col3, col4 = st.columns(4)

        total_revenue = fct_orders['order_revenue'].sum()
        total_profit = fct_orders['order_profit'].sum()
        total_orders = len(fct_orders)
        
        # Calculate Mock Conversion Rate (Assuming 100k visitors)
        visitors = 100000
        conversion_rate = (total_orders / visitors) * 100
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        col1.metric("Total Revenue", f"${total_revenue:,.2f}", "+12% YoY")
        col2.metric("Conversion Rate", f"{conversion_rate:.2f}%", "+0.5% MoM")
        col3.metric("Total Orders", f"{total_orders:,}", "-2% MoM")
        col4.metric("Avg Order Value", f"${avg_order_value:,.2f}", "+5% YoY")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Revenue Pacing Over Time")
            fct_orders['month'] = pd.to_datetime(fct_orders['order_date']).dt.to_period('M').astype(str)
            rev_by_month = fct_orders.groupby('month')['order_revenue'].sum().reset_index()
            
            chart1 = alt.Chart(rev_by_month).mark_line(point=True, color='#1f77b4').encode(
                x='month',
                y='order_revenue',
                tooltip=['month', 'order_revenue']
            ).properties(height=300)
            st.altair_chart(chart1, use_container_width=True)

        with col2:
            st.subheader("Order Status Distribution")
            status_dist = fct_orders['status'].value_counts().reset_index()
            status_dist.columns = ['status', 'count']
            
            chart2 = alt.Chart(status_dist).mark_arc().encode(
                theta=alt.Theta(field="count", type="quantitative"),
                color=alt.Color(field="status", type="nominal"),
                tooltip=['status', 'count']
            ).properties(height=300)
            st.altair_chart(chart2, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading data. Have you run the pipeline? Error: {e}")

elif page == "AI Data Assistant":
    st.title("AI Data Assistant")
    st.markdown("""
    **Agentic Workflow Demonstration:** This interface simulates an LLM-powered agent that uses tool/function calling to query the semantic layer.
    It decomposes the user's natural language request, retrieves the database schema, generates SQL, executes it, and formats the output.
    """)
    
    user_query = st.text_input("Ask a question about the data:", "What are the top 5 products by revenue?")
    
    if st.button("Run AI Analysis"):
        with st.spinner("Agent is reasoning..."):
            agent = AgenticDataAnalyst(db_path='../ecommerce.duckdb')
            result = agent.run_agentic_workflow(user_query)
            
            st.success("Analysis Complete!")
            
            st.subheader("Agent Logic Trace (Tool Calls)")
            col1, col2 = st.columns(2)
            with col1:
                st.checkbox("Step 1: Database Schema Retrieved", value=result['step_1_schema_retrieved'], disabled=True)
                st.checkbox("Step 3: SQL Executed Successfully", value=result['step_3_execution_success'], disabled=True)
            with col2:
                with st.expander("Step 2: Generated SQL (Click to view)"):
                    st.code(result['step_2_generated_sql'], language='sql')
            
            st.subheader("Data Output")
            if result['step_3_execution_success'] and isinstance(result['final_result'], list):
                st.dataframe(pd.DataFrame(result['final_result']), use_container_width=True)
            else:
                st.error(f"Execution failed: {result['final_result']}")
