import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Launch Intelligence", layout="wide")

st.title("🚀 Launch Performance Intelligence Dashboard")

# Connect to database
conn = sqlite3.connect('database/launch_performance.db')

# Check if tables exist
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
st.write("Tables in database:", tables['name'].tolist())

# Load data
try:
    df = pd.read_sql_query("SELECT * FROM launch_metrics LIMIT 50", conn)
    st.success(f"✅ Loaded {len(df)} records from launch_metrics")
    
    if not df.empty:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Visitors", f"{df['visitors'].sum():,}")
        with col2:
            st.metric("Total Signups", f"{df['signups'].sum():,}")
        with col3:
            st.metric("Total Revenue", f"${df['revenue'].sum():,.0f}")
        with col4:
            st.metric("Avg Quality", f"{df['quality_score'].mean():.1%}")
        
        # Chart
        st.subheader("📈 Performance Trends")
        fig = px.line(df, x='metric_date', y=['visitors', 'signups', 'hires'], 
                      title="Performance Trends")
        st.plotly_chart(fig, use_container_width=True)
        
        # Company breakdown
        st.subheader("🏢 Company Breakdown")
        company_data = df.groupby('company').agg({
            'visitors': 'sum',
            'revenue': 'sum'
        }).reset_index()
        fig2 = px.bar(company_data, x='company', y='revenue', 
                     title="Revenue by Company")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Data table
        st.subheader("📋 Data Preview")
        st.dataframe(df)
    else:
        st.warning("No data in launch_metrics table")
        
except Exception as e:
    st.error(f"Error loading data: {e}")

conn.close()
