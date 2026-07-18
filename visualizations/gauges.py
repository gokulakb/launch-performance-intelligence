"""
Gauge chart visualizations for metrics monitoring.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional

from config import COLORS

class GaugeVisualizer:
    """Gauge chart visualizations."""
    
    @staticmethod
    def create_gauge(value: float, title: str, max_value: float = 100,
                    threshold1: float = 60, threshold2: float = 80,
                    height: int = 250) -> go.Figure:
        """
        Create a gauge chart.
        
        Args:
            value: Current value
            title: Chart title
            max_value: Maximum value
            threshold1: Lower threshold
            threshold2: Upper threshold
            height: Chart height
        
        Returns:
            Plotly figure
        """
        # Determine color
        if value >= threshold2:
            color = COLORS['success']
        elif value >= threshold1:
            color = COLORS['warning']
        else:
            color = COLORS['danger']
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title, 'font': {'size': 14}},
            number={'font': {'size': 28, 'color': color}},
            gauge={
                'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, threshold1], 'color': 'rgba(255, 255, 255, 0.8)'},
                    {'range': [threshold1, threshold2], 'color': 'rgba(255, 255, 255, 0.5)'},
                    {'range': [threshold2, max_value], 'color': 'rgba(255, 255, 255, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(
            height=height,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def render_gauge_grid(gauges: List[Dict[str, Any]], cols: int = 3) -> None:
        """
        Render a grid of gauge charts.
        
        Args:
            gauges: List of gauge configurations
            cols: Number of columns
        """
        columns = st.columns(cols)
        
        for idx, gauge_config in enumerate(gauges):
            col_idx = idx % cols
            with columns[col_idx]:
                fig = GaugeVisualizer.create_gauge(
                    value=gauge_config.get('value', 0),
                    title=gauge_config.get('title', ''),
                    max_value=gauge_config.get('max_value', 100),
                    threshold1=gauge_config.get('threshold1', 60),
                    threshold2=gauge_config.get('threshold2', 80)
                )
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_speedometer(value: float, title: str, max_value: float = 100,
                          labels: Dict[float, str] = None) -> go.Figure:
        """
        Create a speedometer-style gauge.
        
        Args:
            value: Current value
            title: Chart title
            max_value: Maximum value
            labels: Custom labels for segments
        
        Returns:
            Plotly figure
        """
        if labels is None:
            labels = {
                0: 'Poor',
                40: 'Fair',
                60: 'Good',
                80: 'Excellent'
            }
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title, 'font': {'size': 14}},
            delta={'reference': max_value * 0.8, 'position': "bottom"},
            gauge={
                'axis': {'range': [0, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 40], 'color': 'red'},
                    {'range': [40, 60], 'color': 'orange'},
                    {'range': [60, 80], 'color': 'yellow'},
                    {'range': [80, max_value], 'color': 'green'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    @staticmethod
    def render_multi_gauge(values: List[float], titles: List[str],
                          max_values: List[float] = None, cols: int = 3) -> None:
        """
        Render multiple gauges in a grid.
        
        Args:
            values: List of values
            titles: List of titles
            max_values: List of max values
            cols: Number of columns
        """
        if max_values is None:
            max_values = [100] * len(values)
        
        columns = st.columns(cols)
        
        for idx, (value, title, max_value) in enumerate(zip(values, titles, max_values)):
            col_idx = idx % cols
            with columns[col_idx]:
                fig = GaugeVisualizer.create_speedometer(value, title, max_value)
                st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def create_quality_gauges(quality_data: Dict[str, float]) -> go.Figure:
        """
        Create quality score gauges in a single figure.
        
        Args:
            quality_data: Dictionary of quality metrics
        
        Returns:
            Plotly figure
        """
        metrics = ['completeness', 'consistency', 'accuracy', 'overall_score']
        titles = ['Completeness', 'Consistency', 'Accuracy', 'Overall']
        
        fig = make_subplots(
            rows=1, cols=4,
            subplot_titles=titles,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'},
                   {'type': 'indicator'}, {'type': 'indicator'}]]
        )
        
        for i, metric in enumerate(metrics):
            value = quality_data.get(metric, 0) * 100
            
            # Determine color
            if value >= 95:
                color = COLORS['success']
            elif value >= 80:
                color = COLORS['warning']
            else:
                color = COLORS['danger']
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={'font': {'size': 20, 'color': color}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': color},
                        'steps': [
                            {'range': [0, 80], 'color': 'rgba(255,255,255,0.8)'},
                            {'range': [80, 95], 'color': 'rgba(255,255,255,0.5)'},
                            {'range': [95, 100], 'color': 'rgba(255,255,255,0.2)'}
                        ]
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig