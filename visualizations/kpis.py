"""
KPI visualization components for the dashboard.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go

from config import COLORS, KPIS
from visualizations.charts import ChartFactory

class KPIVisualizer:
    """KPI visualization and rendering."""
    
    @staticmethod
    def render_kpi_card(value: float, label: str, icon: str = "📊",
                        trend: Optional[float] = None, 
                        format_str: str = "{:,.0f}",
                        status: str = "success") -> None:
        """
        Render a KPI card in Streamlit.
        
        Args:
            value: KPI value
            label: KPI label
            icon: Icon emoji
            trend: Trend percentage
            format_str: Value format string
            status: Status indicator (success, warning, danger)
        """
        # Determine color based on status
        if status == "success":
            color = COLORS['success']
        elif status == "warning":
            color = COLORS['warning']
        elif status == "danger":
            color = COLORS['danger']
        else:
            color = COLORS['primary']
        
        # Format value
        try:
            formatted_value = format_str.format(value)
        except:
            formatted_value = str(value)
        
        # Create HTML card
        trend_html = ""
        if trend is not None:
            trend_icon = "📈" if trend > 0 else "📉"
            trend_color = COLORS['success'] if trend > 0 else COLORS['danger']
            trend_html = f"""
                <span style="color: {trend_color}; font-size: 14px; margin-left: 10px;">
                    {trend_icon} {trend:+.1f}%
                </span>
            """
        
        st.markdown(f"""
            <div style="
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid {color};
                margin-bottom: 10px;
            ">
                <div style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    {icon} {label}
                </div>
                <div style="display: flex; align-items: baseline;">
                    <span style="font-size: 28px; font-weight: bold; color: {color};">
                        {formatted_value}
                    </span>
                    {trend_html}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_kpi_row(kpis: Dict[str, Dict[str, Any]], cols: int = 4) -> None:
        """
        Render a row of KPI cards.
        
        Args:
            kpis: Dictionary of KPI data
            cols: Number of columns
        """
        # Create columns
        columns = st.columns(min(cols, len(kpis)))
        
        # Distribute KPIs across columns
        for idx, (key, kpi_data) in enumerate(kpis.items()):
            col_idx = idx % len(columns)
            with columns[col_idx]:
                KPIVisualizer.render_kpi_card(
                    value=kpi_data.get('value', 0),
                    label=kpi_data.get('label', key),
                    icon=kpi_data.get('icon', '📊'),
                    trend=kpi_data.get('trend', None),
                    format_str=kpi_data.get('format', '{:,.0f}'),
                    status=kpi_data.get('status', 'success')
                )
    
    @staticmethod
    def render_metric_comparison(metric_name: str, current_value: float,
                                previous_value: float, format_str: str = "{:,.0f}",
                                label: str = None) -> None:
        """
        Render a metric comparison with change indicator.
        
        Args:
            metric_name: Name of the metric
            current_value: Current value
            previous_value: Previous value
            format_str: Value format string
            label: Display label
        """
        change = current_value - previous_value
        change_pct = (change / previous_value * 100) if previous_value != 0 else 0
        
        color = COLORS['success'] if change >= 0 else COLORS['danger']
        arrow = "↑" if change >= 0 else "↓"
        
        display_label = label or metric_name
        
        st.markdown(f"""
            <div style="
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                margin: 5px 0;
            ">
                <div style="font-size: 12px; color: #999; text-transform: uppercase;">
                    {display_label}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 20px; font-weight: bold;">
                        {format_str.format(current_value)}
                    </span>
                    <span style="color: {color}; font-size: 14px;">
                        {arrow} {format_str.format(abs(change))} ({change_pct:+.1f}%)
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_mini_chart(df: pd.DataFrame, x_col: str, y_col: str,
                          height: int = 100, color: str = COLORS['primary']) -> None:
        """
        Render a mini chart for KPI trend.
        
        Args:
            df: DataFrame with data
            x_col: X-axis column
            y_col: Y-axis column
            height: Chart height
            color: Chart color
        """
        if df.empty or x_col not in df.columns or y_col not in df.columns:
            st.write("No data available")
            return
        
        fig = ChartFactory.line_chart(
            df=df,
            x_col=x_col,
            y_col=y_col,
            color=color
        )
        
        fig.update_layout(
            height=height,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)