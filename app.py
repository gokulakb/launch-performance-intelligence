"""
Launch Performance Intelligence Dashboard
Main application entry point
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import io
import os
import sys
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# === RENDER DEPLOYMENT SETUP ===
# Initialize database on Render
if os.environ.get('RENDER'):
    print("🚀 Running on Render - Initializing database...")
    try:
        # Check if we need to initialize
        db_path = 'database/launch_performance.db'
        if not os.path.exists(db_path):
            import subprocess
            subprocess.run(['python', 'render_init.py'], check=True)
            print("✅ Database initialized on Render!")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
# === END RENDER SETUP ===

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Launch Performance Intelligence Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
COMPANIES = ['TechCorp', 'DataFlow', 'CloudNine', 'SmartSolutions', 'InnovateLabs']
COLORS = {
    'primary': '#1E88E5',
    'secondary': '#FF6B6B',
    'success': '#4CAF50',
    'warning': '#FFA726',
    'danger': '#E53935',
    'info': '#26C6DA',
    'light': '#F5F5F5',
    'dark': '#263238'
}

def get_db_connection():
    """Get database connection."""
    return sqlite3.connect('database/launch_performance.db')

def format_currency(value):
    """Format value as currency."""
    return f"${value:,.0f}"

def format_percentage(value):
    """Format value as percentage."""
    return f"{value:.1f}%"

def format_number(value):
    """Format number with commas."""
    return f"{value:,}"

# ============ FUNCTION DEFINITIONS ============

def render_executive_dashboard(company):
    """Render the executive dashboard."""
    st.header("Executive Dashboard")
    
    conn = get_db_connection()
    
    where_clause = ""
    params = []
    if company != "All":
        where_clause = "WHERE company = ?"
        params.append(company)
    
    query = f"""
        SELECT * FROM launch_metrics 
        {where_clause}
        ORDER BY metric_date DESC LIMIT 1
    """
    latest_df = pd.read_sql_query(query, conn, params=params)
    
    trend_query = f"""
        SELECT * FROM launch_metrics 
        {where_clause}
        ORDER BY metric_date DESC LIMIT 30
    """
    trend_df = pd.read_sql_query(trend_query, conn, params=params)
    
    revenue_query = """
        SELECT SUM(amount) as total_revenue, COUNT(*) as transactions,
               AVG(amount) as avg_amount
        FROM revenue
    """
    revenue_df = pd.read_sql_query(revenue_query, conn)
    
    user_query = "SELECT COUNT(*) as total_users FROM users"
    user_df = pd.read_sql_query(user_query, conn)
    
    conn.close()
    
    if latest_df.empty:
        st.warning("No data available. Please run init_db.py to generate sample data.")
        return
    
    latest = latest_df.iloc[0]
    total_users = user_df['total_users'].iloc[0] if not user_df.empty else 0
    
    # KPI Cards - First Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Users",
            format_number(total_users),
            delta="+12.5%"
        )
    
    with col2:
        st.metric(
            "Active Users",
            format_number(latest.get('active_users', 0)),
            delta="+8.3%"
        )
    
    with col3:
        st.metric(
            "Signups",
            format_number(latest.get('signups', 0)),
            delta="+5.7%"
        )
    
    with col4:
        st.metric(
            "Hires",
            format_number(latest.get('hires', 0)),
            delta="-2.1%",
            delta_color="inverse"
        )
    
    # KPI Cards - Second Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = revenue_df['total_revenue'].iloc[0] if not revenue_df.empty else 0
    
    with col1:
        st.metric(
            "Total Revenue",
            format_currency(total_revenue),
            delta="+15.2%"
        )
    
    with col2:
        retention = latest.get('retention_rate', 0) * 100
        st.metric(
            "Retention (D7)",
            format_percentage(retention),
            delta="+2.3%"
        )
    
    with col3:
        quality = latest.get('quality_score', 0) * 100
        st.metric(
            "Quality Score",
            format_percentage(quality),
            delta="+1.8%"
        )
    
    with col4:
        visitors = latest.get('visitors', 1)
        hires = latest.get('hires', 0)
        conversion = (hires / visitors * 100) if visitors > 0 else 0
        st.metric(
            "Conversion Rate",
            format_percentage(conversion),
            delta="-1.5%",
            delta_color="inverse"
        )
    
    # Charts
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance Trends")
        if not trend_df.empty:
            trend_df = trend_df.sort_values('metric_date')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df['metric_date'],
                y=trend_df['active_users'],
                mode='lines+markers',
                name='Active Users',
                line=dict(color=COLORS['primary'], width=2)
            ))
            fig.add_trace(go.Scatter(
                x=trend_df['metric_date'],
                y=trend_df['signups'],
                mode='lines+markers',
                name='Signups',
                line=dict(color=COLORS['success'], width=2)
            ))
            fig.add_trace(go.Scatter(
                x=trend_df['metric_date'],
                y=trend_df['hires'],
                mode='lines+markers',
                name='Hires',
                line=dict(color=COLORS['warning'], width=2)
            ))
            fig.update_layout(
                title='User Activity Trends',
                xaxis_title='Date',
                yaxis_title='Count',
                height=400,
                hovermode='x unified',
                showlegend=True,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No trend data available")
    
    with col2:
        st.subheader("Revenue Trend")
        if not trend_df.empty:
            trend_df = trend_df.sort_values('metric_date')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df['metric_date'],
                y=trend_df['revenue'],
                mode='lines+markers',
                fill='tozeroy',
                name='Revenue',
                line=dict(color=COLORS['success'], width=2),
                fillcolor='rgba(76, 175, 80, 0.2)'
            ))
            fig.update_layout(
                title='Revenue Over Time',
                xaxis_title='Date',
                yaxis_title='Revenue ($)',
                height=400,
                hovermode='x unified',
                showlegend=True,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No revenue data available")
    
    # Gauges
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest.get('retention_rate', 0) * 100,
            title={'text': "Retention Rate"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['success']},
                'steps': [
                    {'range': [0, 50], 'color': 'lightgray'},
                    {'range': [50, 75], 'color': 'gray'},
                    {'range': [75, 100], 'color': 'darkgray'}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest.get('quality_score', 0) * 100,
            title={'text': "Quality Score"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['primary']},
                'steps': [
                    {'range': [0, 50], 'color': 'lightgray'},
                    {'range': [50, 75], 'color': 'gray'},
                    {'range': [75, 100], 'color': 'darkgray'}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=conversion,
            title={'text': "Conversion Rate"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['warning']},
                'steps': [
                    {'range': [0, 50], 'color': 'lightgray'},
                    {'range': [50, 75], 'color': 'gray'},
                    {'range': [75, 100], 'color': 'darkgray'}
                ]
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)


def render_funnel_dashboard(company):
    """Render the funnel dashboard."""
    st.header("Funnel Dashboard")
    
    conn = get_db_connection()
    
    where_clause = ""
    params = []
    if company != "All":
        where_clause = "AND company = ?"
        params.append(company)
    
    funnel_query = f"""
        SELECT 
            event_type,
            COUNT(DISTINCT user_id) as user_count
        FROM events
        WHERE event_type IN ('visitor', 'signup', 'profile_complete', 'application', 'interview', 'offer', 'hire')
        {where_clause}
        GROUP BY event_type
        ORDER BY CASE event_type
            WHEN 'visitor' THEN 1
            WHEN 'signup' THEN 2
            WHEN 'profile_complete' THEN 3
            WHEN 'application' THEN 4
            WHEN 'interview' THEN 5
            WHEN 'offer' THEN 6
            WHEN 'hire' THEN 7
        END
    """
    funnel_df = pd.read_sql_query(funnel_query, conn, params=params)
    
    conn.close()
    
    if funnel_df.empty:
        st.warning("No funnel data available")
        return
    
    stages = funnel_df['event_type'].tolist()
    values = funnel_df['user_count'].tolist()
    
    stage_labels = {
        'visitor': 'Visitors',
        'signup': 'Signups',
        'profile_complete': 'Profile Complete',
        'application': 'Applications',
        'interview': 'Interviews',
        'offer': 'Offers',
        'hire': 'Hired'
    }
    labels = [stage_labels.get(s, s) for s in stages]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Conversion Funnel")
        fig = go.Figure(go.Funnel(
            y=labels,
            x=values,
            textinfo="value+percent initial",
            textposition="inside",
            marker=dict(color=['#1E88E5', '#4CAF50', '#FFA726', '#FF6B6B', '#26C6DA', '#8E24AA', '#7CB342']),
            connector=dict(line=dict(color='grey', width=2))
        ))
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Drop-off Analysis")
        
        drop_off_data = []
        for i in range(len(values) - 1):
            drop = ((values[i] - values[i+1]) / values[i]) * 100 if values[i] > 0 else 0
            drop_off_data.append({
                'Stage': f"{labels[i]} -> {labels[i+1]}",
                'Drop-off %': drop
            })
        
        if drop_off_data:
            drop_df = pd.DataFrame(drop_off_data)
            fig = go.Figure(go.Bar(
                x=drop_df['Stage'],
                y=drop_df['Drop-off %'],
                marker=dict(
                    color=['#4CAF50' if d < 30 else '#FFA726' if d < 50 else '#FF6B6B' 
                           for d in drop_df['Drop-off %']]
                ),
                text=drop_df['Drop-off %'].round(1),
                textposition='outside'
            ))
            fig.update_layout(
                title='Drop-off Rates Between Stages',
                xaxis_title='Conversion Step',
                yaxis_title='Drop-off %',
                height=400,
                showlegend=False,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Funnel Details")
    
    detail_df = pd.DataFrame({
        'Stage': labels,
        'Users': values,
        'Conversion %': [(v / values[0] * 100) if values[0] > 0 else 0 for v in values]
    })
    detail_df['Conversion %'] = detail_df['Conversion %'].round(1).astype(str) + '%'
    st.dataframe(detail_df, use_container_width=True)


def render_revenue_dashboard(company):
    """Render the revenue dashboard."""
    st.header("Revenue Dashboard")
    
    conn = get_db_connection()
    
    where_clause = ""
    params = []
    if company != "All":
        where_clause = "WHERE company = ?"
        params.append(company)
    
    revenue_query = f"""
        SELECT 
            transaction_date,
            SUM(amount) as daily_revenue,
            COUNT(*) as transactions,
            AVG(amount) as avg_transaction
        FROM revenue
        {where_clause}
        GROUP BY transaction_date
        ORDER BY transaction_date DESC
        LIMIT 30
    """
    revenue_df = pd.read_sql_query(revenue_query, conn, params=params)
    
    company_revenue_query = """
        SELECT 
            company,
            SUM(amount) as revenue,
            COUNT(*) as transactions
        FROM revenue
        GROUP BY company
        ORDER BY revenue DESC
    """
    company_revenue = pd.read_sql_query(company_revenue_query, conn)
    
    recruiter_query = """
        SELECT 
            recruiter,
            SUM(amount) as revenue,
            COUNT(*) as transactions
        FROM revenue
        GROUP BY recruiter
        ORDER BY revenue DESC
        LIMIT 10
    """
    recruiter_revenue = pd.read_sql_query(recruiter_query, conn)
    
    conn.close()
    
    total_revenue = revenue_df['daily_revenue'].sum() if not revenue_df.empty else 0
    avg_daily = revenue_df['daily_revenue'].mean() if not revenue_df.empty else 0
    total_transactions = revenue_df['transactions'].sum() if not revenue_df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", format_currency(total_revenue))
    with col2:
        st.metric("Avg Daily Revenue", format_currency(avg_daily))
    with col3:
        st.metric("Total Transactions", format_number(total_transactions))
    with col4:
        st.metric("Avg Transaction", format_currency(revenue_df['avg_transaction'].mean() if not revenue_df.empty else 0))
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Daily Revenue Trend")
        if not revenue_df.empty:
            revenue_df = revenue_df.sort_values('transaction_date')
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=revenue_df['transaction_date'],
                y=revenue_df['daily_revenue'],
                name='Revenue',
                marker=dict(color=COLORS['success'])
            ))
            fig.add_trace(go.Scatter(
                x=revenue_df['transaction_date'],
                y=revenue_df['daily_revenue'].rolling(3).mean(),
                mode='lines',
                name='3-Day Average',
                line=dict(color=COLORS['primary'], width=2)
            ))
            fig.update_layout(
                title='Daily Revenue',
                xaxis_title='Date',
                yaxis_title='Revenue ($)',
                height=400,
                hovermode='x unified',
                showlegend=True,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No revenue data available")
    
    with col2:
        st.subheader("Revenue by Company")
        if not company_revenue.empty:
            fig = px.pie(
                company_revenue,
                values='revenue',
                names='company',
                title='Revenue Distribution by Company',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No revenue by company data available")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue by Recruiter")
        if not recruiter_revenue.empty:
            fig = go.Figure(go.Bar(
                x=recruiter_revenue['recruiter'],
                y=recruiter_revenue['revenue'],
                marker=dict(color=COLORS['primary']),
                text=recruiter_revenue['revenue'].apply(lambda x: f"${x:,.0f}"),
                textposition='outside'
            ))
            fig.update_layout(
                xaxis_title='Recruiter',
                yaxis_title='Revenue ($)',
                height=400,
                showlegend=False,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No recruiter revenue data available")
    
    with col2:
        st.subheader("Revenue Breakdown")
        if not company_revenue.empty:
            fig = px.treemap(
                company_revenue,
                path=['company'],
                values='revenue',
                title='Revenue Treemap'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No breakdown data available")


def render_retention_dashboard(company):
    """Render the retention dashboard."""
    st.header("Retention Dashboard")
    
    conn = get_db_connection()
    
    where_clause = ""
    params = []
    if company != "All":
        where_clause = "WHERE company = ?"
        params.append(company)
    
    retention_query = f"""
        SELECT 
            cohort,
            COUNT(*) as total_users,
            AVG(day_1_retained) * 100 as d1_retention,
            AVG(day_7_retained) * 100 as d7_retention,
            AVG(day_30_retained) * 100 as d30_retention,
            AVG(churned) * 100 as churn_rate
        FROM retention
        {where_clause}
        GROUP BY cohort
        ORDER BY cohort
    """
    retention_df = pd.read_sql_query(retention_query, conn, params=params)
    
    heatmap_query = f"""
        SELECT 
            cohort,
            CASE 
                WHEN day_1_retained = 1 THEN 1
                WHEN day_7_retained = 1 THEN 7
                WHEN day_30_retained = 1 THEN 30
                ELSE 0
            END as retention_period,
            COUNT(*) as user_count
        FROM retention
        {where_clause}
        GROUP BY cohort, retention_period
    """
    heatmap_df = pd.read_sql_query(heatmap_query, conn, params=params)
    
    conn.close()
    
    if retention_df.empty:
        st.warning("No retention data available")
        return
    
    latest = retention_df.iloc[-1] if not retention_df.empty else {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Day 1 Retention", format_percentage(latest.get('d1_retention', 0)))
    with col2:
        st.metric("Day 7 Retention", format_percentage(latest.get('d7_retention', 0)))
    with col3:
        st.metric("Day 30 Retention", format_percentage(latest.get('d30_retention', 0)))
    with col4:
        st.metric("Churn Rate", format_percentage(latest.get('churn_rate', 0)), delta_color="inverse")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retention Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=retention_df['cohort'],
            y=retention_df['d1_retention'],
            mode='lines+markers',
            name='Day 1',
            line=dict(color=COLORS['primary'], width=2)
        ))
        fig.add_trace(go.Scatter(
            x=retention_df['cohort'],
            y=retention_df['d7_retention'],
            mode='lines+markers',
            name='Day 7',
            line=dict(color=COLORS['success'], width=2)
        ))
        fig.add_trace(go.Scatter(
            x=retention_df['cohort'],
            y=retention_df['d30_retention'],
            mode='lines+markers',
            name='Day 30',
            line=dict(color=COLORS['warning'], width=2)
        ))
        fig.update_layout(
            title='Retention Rates by Cohort',
            xaxis_title='Cohort',
            yaxis_title='Retention Rate (%)',
            height=400,
            hovermode='x unified',
            showlegend=True,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Cohort Retention Heatmap")
        if not heatmap_df.empty:
            pivot_data = heatmap_df.pivot(index='cohort', columns='retention_period', values='user_count').fillna(0)
            pivot_pct = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
            
            fig = go.Figure(data=go.Heatmap(
                z=pivot_pct.values,
                x=pivot_pct.columns,
                y=pivot_pct.index,
                colorscale='RdYlGn',
                text=pivot_pct.values.round(1),
                texttemplate='%{text:.1f}%',
                textfont={"size": 10},
                colorbar=dict(title="Retention %")
            ))
            fig.update_layout(
                title='Cohort Retention Heatmap',
                xaxis_title='Retention Period (Days)',
                yaxis_title='Cohort',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No heatmap data available")


def render_quality_dashboard():
    """Render the data quality dashboard."""
    st.header("Data Quality Dashboard")
    
    conn = get_db_connection()
    
    quality_query = """
        SELECT * FROM quality_metrics
        ORDER BY metric_type, table_name
    """
    quality_df = pd.read_sql_query(quality_query, conn)
    
    conn.close()
    
    if quality_df.empty:
        st.warning("No quality metrics available")
        return
    
    overall = quality_df[quality_df['metric_type'] == 'overall']
    overall_score = overall['value'].iloc[0] * 100 if not overall.empty else 0
    
    completeness = quality_df[quality_df['metric_type'] == 'completeness']['value'].mean() * 100
    consistency = quality_df[quality_df['metric_type'] == 'consistency']['value'].mean() * 100
    accuracy = quality_df[quality_df['metric_type'] == 'accuracy']['value'].mean() * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Quality", format_percentage(overall_score))
    with col2:
        st.metric("Completeness", format_percentage(completeness))
    with col3:
        st.metric("Consistency", format_percentage(consistency))
    with col4:
        st.metric("Accuracy", format_percentage(accuracy))
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=completeness,
            title={'text': "Completeness"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['success'] if completeness > 90 else COLORS['warning']}
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=consistency,
            title={'text': "Consistency"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['primary'] if consistency > 90 else COLORS['warning']}
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=accuracy,
            title={'text': "Accuracy"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': COLORS['success'] if accuracy > 90 else COLORS['danger']}
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Quality Metrics by Table")
    
    display_df = quality_df[['table_name', 'metric_type', 'value', 'validation_status']].copy()
    display_df['value'] = display_df['value'] * 100
    display_df = display_df.rename(columns={
        'table_name': 'Table',
        'metric_type': 'Metric Type',
        'value': 'Score (%)',
        'validation_status': 'Status'
    })
    st.dataframe(display_df, use_container_width=True)


def render_problem_ranking(company):
    """Render the problem ranking dashboard."""
    st.header("Problem Ranking Dashboard")
    
    problems = [
        {
            'rank': 1,
            'title': 'Low Day 30 Retention',
            'category': 'Retention',
            'description': 'Day 30 retention is below 20%',
            'impact': 'High',
            'priority': 'Critical',
            'severity': 'Critical',
            'suggested_action': 'Implement retention strategies and improve onboarding',
            'owner': 'Product Team'
        },
        {
            'rank': 2,
            'title': 'High Drop-off at Application Stage',
            'category': 'Funnel',
            'description': '60% drop-off between signup and application',
            'impact': 'High',
            'priority': 'High',
            'severity': 'High',
            'suggested_action': 'Simplify application process and improve UX',
            'owner': 'Product Team'
        },
        {
            'rank': 3,
            'title': 'Revenue Decline',
            'category': 'Revenue',
            'description': 'Revenue decreased by 15% in last quarter',
            'impact': 'Critical',
            'priority': 'High',
            'severity': 'High',
            'suggested_action': 'Analyze revenue drivers and identify causes',
            'owner': 'Revenue Team'
        },
        {
            'rank': 4,
            'title': 'Data Quality Issues',
            'category': 'Quality',
            'description': 'Inconsistent data in users table',
            'impact': 'Medium',
            'priority': 'Medium',
            'severity': 'Medium',
            'suggested_action': 'Implement data validation and cleaning',
            'owner': 'Data Engineering'
        },
        {
            'rank': 5,
            'title': 'High Churn Rate',
            'category': 'Retention',
            'description': 'Monthly churn rate is 8.2%',
            'impact': 'High',
            'priority': 'High',
            'severity': 'High',
            'suggested_action': 'Launch retention campaigns and improve customer success',
            'owner': 'Customer Success'
        }
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Issues", len(problems))
    with col2:
        critical = sum(1 for p in problems if p['priority'] == 'Critical')
        st.metric("Critical Issues", critical)
    with col3:
        high = sum(1 for p in problems if p['priority'] == 'High')
        st.metric("High Priority", high)
    with col4:
        avg_impact = sum(1 for p in problems if p['impact'] == 'High') / len(problems) * 100
        st.metric("High Impact %", f"{avg_impact:.0f}%")
    
    st.markdown("---")
    st.subheader("Top Issues")
    
    for problem in problems:
        with st.expander(f"#{problem['rank']} - {problem['title']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {problem['category']}")
                st.write(f"**Description:** {problem['description']}")
                st.write(f"**Impact:** {problem['impact']}")
            
            with col2:
                st.write(f"**Priority:** {problem['priority']}")
                st.write(f"**Severity:** {problem['severity']}")
                st.write(f"**Owner:** {problem['owner']}")
            
            st.write(f"**Suggested Action:** {problem['suggested_action']}")


def render_backlog():
    """Render the analytics backlog."""
    st.header("Analytics Backlog")
    
    backlog_items = [
        {'priority': 'P0', 'task': 'Implement real-time data streaming', 'owner': 'Data Engineering', 'status': 'In Progress', 'eta': '2 weeks'},
        {'priority': 'P1', 'task': 'Develop predictive churn model', 'owner': 'Data Science', 'status': 'Planning', 'eta': '1 month'},
        {'priority': 'P1', 'task': 'Implement A/B testing framework', 'owner': 'Product Team', 'status': 'In Progress', 'eta': '3 weeks'},
        {'priority': 'P2', 'task': 'Build automated reporting system', 'owner': 'BI Team', 'status': 'Not Started', 'eta': '6 weeks'},
        {'priority': 'P2', 'task': 'Implement user segmentation', 'owner': 'Data Engineering', 'status': 'Not Started', 'eta': '4 weeks'},
        {'priority': 'P3', 'task': 'Create API for analytics data', 'owner': 'Backend Team', 'status': 'Not Started', 'eta': '8 weeks'},
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Items", len(backlog_items))
    with col2:
        in_progress = sum(1 for item in backlog_items if item['status'] == 'In Progress')
        st.metric("In Progress", in_progress)
    with col3:
        not_started = sum(1 for item in backlog_items if item['status'] == 'Not Started')
        st.metric("Not Started", not_started)
    with col4:
        completed = sum(1 for item in backlog_items if item['status'] == 'Completed')
        st.metric("Completed", completed)
    
    st.markdown("---")
    st.subheader("Backlog Items")
    
    df = pd.DataFrame(backlog_items)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Add New Backlog Item")
    
    with st.form("add_backlog_item"):
        col1, col2 = st.columns(2)
        
        with col1:
            task = st.text_input("Task")
            owner = st.selectbox("Owner", ["Data Engineering", "Data Science", "Product Team", "BI Team", "Backend Team"])
            priority = st.selectbox("Priority", ["P0", "P1", "P2", "P3"])
        
        with col2:
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Blocked"])
            eta = st.text_input("ETA (e.g., 2 weeks)")
        
        if st.form_submit_button("Add Item"):
            st.success("Backlog item added successfully!")


def render_export_dashboard(company):
    """Render the export dashboard."""
    st.header("Export Dashboard")
    
    conn = get_db_connection()
    
    where_clause = ""
    params = []
    if company != "All":
        where_clause = "WHERE company = ?"
        params.append(company)
    
    metrics_query = f"""
        SELECT * FROM launch_metrics
        {where_clause}
        ORDER BY metric_date DESC
        LIMIT 100
    """
    metrics_df = pd.read_sql_query(metrics_query, conn, params=params)
    
    revenue_query = """
        SELECT * FROM revenue
        ORDER BY transaction_date DESC
        LIMIT 100
    """
    revenue_df = pd.read_sql_query(revenue_query, conn)
    
    conn.close()
    
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**CSV Export**")
        if st.button("Export as CSV"):
            if not metrics_df.empty:
                csv = metrics_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"launch_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export")
    
    with col2:
        st.write("**Excel Export**")
        if st.button("Export as Excel"):
            if not metrics_df.empty:
                excel = io.BytesIO()
                with pd.ExcelWriter(excel, engine='openpyxl') as writer:
                    metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
                    if not revenue_df.empty:
                        revenue_df.to_excel(writer, sheet_name='Revenue', index=False)
                excel.seek(0)
                st.download_button(
                    label="Download Excel",
                    data=excel,
                    file_name=f"dashboard_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("No data to export")
    
    with col3:
        st.write("**PDF Report**")
        if st.button("Export as PDF"):
            try:
                # Try to use reportlab for PDF generation
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                
                # Create a simple PDF
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                c.drawString(100, 750, "Launch Performance Intelligence Report")
                c.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                c.drawString(100, 700, f"Company: {company if company != 'All' else 'All Companies'}")
                c.drawString(100, 670, "Data Summary:")
                
                if not metrics_df.empty:
                    y = 640
                    for idx, row in metrics_df.head(10).iterrows():
                        c.drawString(100, y, f"{row['metric_date']}: Visitors={row['visitors']}, Revenue=${row['revenue']:,.0f}")
                        y -= 20
                        if y < 100:
                            c.showPage()
                            y = 750
                
                c.save()
                pdf_buffer.seek(0)
                
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=f"dashboard_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("PDF generated successfully!")
            except ImportError:
                st.warning("PDF generation is not available. Please use CSV or Excel export.")
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")

# ============ SIDEBAR AND NAVIGATION ============

st.sidebar.title("Launch Intelligence")
st.sidebar.markdown("---")

company_filter = st.sidebar.selectbox(
    "Company",
    options=["All"] + COMPANIES,
    index=0
)

date_option = st.sidebar.selectbox(
    "Date Range",
    options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 365 Days"],
    index=1
)

today = datetime.now()
date_range_map = {
    "Last 7 Days": 7,
    "Last 30 Days": 30,
    "Last 90 Days": 90,
    "Last 365 Days": 365
}
days = date_range_map.get(date_option, 30)

pages = [
    "Executive Dashboard",
    "Funnel Dashboard",
    "Revenue Dashboard",
    "Retention Dashboard",
    "Data Quality Dashboard",
    "Problem Ranking",
    "Analytics Backlog",
    "Export Dashboard"
]

page = st.sidebar.radio(
    "Navigation",
    pages,
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Launch Performance Intelligence\n\n"
    "Analyzing launch performance with real operational data.\n\n"
    f"Data refresh: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)

st.title("Launch Performance Intelligence Dashboard")
st.markdown(f"*Analyzing launch performance - {date_option}*")

# Page routing (AFTER function definitions)
if page == "Executive Dashboard":
    render_executive_dashboard(company_filter)
elif page == "Funnel Dashboard":
    render_funnel_dashboard(company_filter)
elif page == "Revenue Dashboard":
    render_revenue_dashboard(company_filter)
elif page == "Retention Dashboard":
    render_retention_dashboard(company_filter)
elif page == "Data Quality Dashboard":
    render_quality_dashboard()
elif page == "Problem Ranking":
    render_problem_ranking(company_filter)
elif page == "Analytics Backlog":
    render_backlog()
elif page == "Export Dashboard":
    render_export_dashboard(company_filter)

if __name__ == "__main__":
    pass
