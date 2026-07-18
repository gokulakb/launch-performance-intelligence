"""
Heatmap visualizations for cohort analysis and correlation.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Any, List, Optional

from config import COLORS

class HeatmapVisualizer:
    """Heatmap visualization utilities."""
    
    @staticmethod
    def create_cohort_heatmap(df: pd.DataFrame, title: str = "Cohort Retention",
                             x_label: str = "Months Since Signup",
                             y_label: str = "Cohort") -> go.Figure:
        """
        Create a cohort retention heatmap.
        
        Args:
            df: DataFrame with cohort data (index: cohort, columns: months)
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
        
        Returns:
            Plotly figure
        """
        if df.empty:
            return go.Figure()
        
        # Prepare data
        data_matrix = df.values
        cohorts = df.index.tolist()
        months = df.columns.tolist()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=data_matrix,
            x=months,
            y=cohorts,
            colorscale='RdYlGn',
            text=data_matrix.round(1).astype(str) + '%',
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Retention %"),
            hovertemplate='<b>Cohort:</b> %{y}<br>' +
                         '<b>Month:</b> %{x}<br>' +
                         '<b>Retention:</b> %{z:.1f}%<br>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=500,
            xaxis=dict(tickangle=0),
            yaxis=dict(tickfont=dict(size=10))
        )
        
        return fig
    
    @staticmethod
    def render_cohort_heatmap(df: pd.DataFrame, title: str = "Cohort Retention Analysis") -> None:
        """Render a cohort heatmap in Streamlit."""
        if df.empty:
            st.warning("No cohort data available")
            return
        
        fig = HeatmapVisualizer.create_cohort_heatmap(df, title)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_correlation_heatmap(df: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
        """
        Create a correlation heatmap.
        
        Args:
            df: DataFrame with numerical columns
            title: Chart title
        
        Returns:
            Plotly figure
        """
        if df.empty:
            return go.Figure()
        
        # Calculate correlation
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation"),
            zmid=0,
            hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>' +
                         'Correlation: %{z:.2f}<br>'
        ))
        
        fig.update_layout(
            title=title,
            height=500,
            xaxis=dict(tickangle=45),
            yaxis=dict(tickfont=dict(size=10))
        )
        
        return fig
    
    @staticmethod
    def create_engagement_heatmap(df: pd.DataFrame, date_col: str, 
                                  hour_col: str, value_col: str,
                                  title: str = "Engagement Heatmap") -> go.Figure:
        """
        Create an engagement heatmap by day and hour.
        
        Args:
            df: DataFrame with date, hour, and value columns
            date_col: Column name for date
            hour_col: Column name for hour
            value_col: Column name for value
            title: Chart title
        
        Returns:
            Plotly figure
        """
        if df.empty:
            return go.Figure()
        
        # Pivot data
        pivot_df = df.pivot_table(
            index=date_col,
            columns=hour_col,
            values=value_col,
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Viridis',
            colorbar=dict(title="Activity"),
            hovertemplate='<b>Date:</b> %{y}<br>' +
                         '<b>Hour:</b> %{x}<br>' +
                         '<b>Value:</b> %{z:.1f}<br>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Hour of Day",
            yaxis_title="Date",
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_flow_heatmap(from_data: List[str], to_data: List[str],
                           values: List[float], title: str = "Flow Heatmap") -> go.Figure:
        """
        Create a flow heatmap showing transitions between states.
        
        Args:
            from_data: Source states
            to_data: Destination states
            values: Flow values
            title: Chart title
        
        Returns:
            Plotly figure
        """
        # Create matrix
        unique_from = list(set(from_data))
        unique_to = list(set(to_data))
        
        matrix = np.zeros((len(unique_from), len(unique_to)))
        
        for f, t, v in zip(from_data, to_data, values):
            i = unique_from.index(f)
            j = unique_to.index(t)
            matrix[i][j] = v
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=unique_to,
            y=unique_from,
            colorscale='Blues',
            text=matrix.round(0).astype(int),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Flow"),
            hovertemplate='<b>From:</b> %{y}<br>' +
                         '<b>To:</b> %{x}<br>' +
                         '<b>Value:</b> %{z:.0f}<br>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="To",
            yaxis_title="From",
            height=500
        )
        
        return fig
    
    @staticmethod
    def create_metric_heatmap(df: pd.DataFrame, x_col: str, y_col: str,
                             value_col: str, title: str = "Metric Heatmap") -> go.Figure:
        """
        Create a heatmap for any metric.
        
        Args:
            df: DataFrame with data
            x_col: X-axis column
            y_col: Y-axis column
            value_col: Value column
            title: Chart title
        
        Returns:
            Plotly figure
        """
        if df.empty:
            return go.Figure()
        
        # Pivot data
        pivot_df = df.pivot_table(
            index=y_col,
            columns=x_col,
            values=value_col,
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='YlOrRd',
            text=pivot_df.round(1).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title=value_col),
            hovertemplate='<b>%{y}</b> - <b>%{x}</b><br>' +
                         'Value: %{z:.1f}<br>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=500
        )
        
        return fig