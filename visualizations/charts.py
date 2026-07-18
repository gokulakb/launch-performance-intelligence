"""
Chart generation and visualization utilities.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from config import COLORS

class ChartFactory:
    """Factory class for creating various chart types."""
    
    @staticmethod
    def line_chart(df: pd.DataFrame, x_col: str, y_col: str, 
                   title: str = "", x_label: str = "", y_label: str = "",
                   color: str = COLORS['primary']) -> go.Figure:
        """Create a line chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers',
            name=y_col,
            line=dict(color=color, width=2),
            marker=dict(size=6, color=color)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label or x_col,
            yaxis_title=y_label or y_col,
            hovermode='x unified',
            showlegend=True,
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def bar_chart(df: pd.DataFrame, x_col: str, y_col: str,
                  title: str = "", x_label: str = "", y_label: str = "",
                  color: str = COLORS['primary']) -> go.Figure:
        """Create a bar chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=y_col,
            marker=dict(color=color, line=dict(color='white', width=1))
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label or x_col,
            yaxis_title=y_label or y_col,
            showlegend=True,
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def pie_chart(df: pd.DataFrame, names_col: str, values_col: str,
                  title: str = "", hole: float = 0.3) -> go.Figure:
        """Create a pie or donut chart."""
        fig = go.Figure(data=[go.Pie(
            labels=df[names_col],
            values=df[values_col],
            hole=hole,
            textinfo='label+percent',
            textposition='outside',
            marker=dict(colors=COLORS['palette'])
        )])
        
        fig.update_layout(
            title=title,
            height=400,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def funnel_chart(stages: List[str], values: List[float],
                     title: str = "") -> go.Figure:
        """Create a funnel chart."""
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            textposition="inside",
            marker=dict(color=COLORS['palette']),
            connector=dict(line=dict(color='grey', width=2))
        ))
        
        fig.update_layout(
            title=title,
            height=500,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def waterfall_chart(categories: List[str], values: List[float],
                        title: str = "") -> go.Figure:
        """Create a waterfall chart."""
        fig = go.Figure(go.Waterfall(
            name="",
            orientation="v",
            measure=["relative"] * len(categories),
            x=categories,
            y=values,
            text=[f"{v:,.0f}" for v in values],
            textposition="outside",
            connector=dict(line=dict(color='grey', width=2)),
            increasing=dict(marker=dict(color=COLORS['success'])),
            decreasing=dict(marker=dict(color=COLORS['danger'])),
            totals=dict(marker=dict(color=COLORS['primary']))
        ))
        
        fig.update_layout(
            title=title,
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def histogram(df: pd.DataFrame, column: str, bins: int = 30,
                  title: str = "") -> go.Figure:
        """Create a histogram."""
        fig = go.Figure(data=[go.Histogram(
            x=df[column],
            nbinsx=bins,
            marker=dict(color=COLORS['primary'])
        )])
        
        fig.update_layout(
            title=title,
            xaxis_title=column,
            yaxis_title='Frequency',
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def scatter_chart(df: pd.DataFrame, x_col: str, y_col: str,
                      color_col: str = None, title: str = "") -> go.Figure:
        """Create a scatter chart."""
        fig = go.Figure()
        
        if color_col and color_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(
                    size=8,
                    color=df[color_col],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=df[color_col] if color_col in df.columns else None
            ))
        else:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=dict(size=8, color=COLORS['primary'])
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def treemap(df: pd.DataFrame, labels_col: str, values_col: str,
                parents_col: str = None, title: str = "") -> go.Figure:
        """Create a treemap chart."""
        fig = go.Figure(go.Treemap(
            labels=df[labels_col],
            values=df[values_col],
            parents=df[parents_col] if parents_col else [""] * len(df),
            marker=dict(colors=COLORS['palette']),
            textinfo="label+value+percent root"
        ))
        
        fig.update_layout(
            title=title,
            height=500
        )
        
        return fig
    
    @staticmethod
    def heatmap(df: pd.DataFrame, title: str = "",
                x_label: str = "", y_label: str = "") -> go.Figure:
        """Create a heatmap."""
        fig = go.Figure(data=go.Heatmap(
            z=df.values,
            x=df.columns,
            y=df.index,
            colorscale='YlOrRd',
            text=df.values,
            texttemplate='%{text:.1f}',
            textfont={"size": 10},
            colorbar=dict(title="Value")
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            height=500
        )
        
        return fig
    
    @staticmethod
    def gauge_chart(value: float, title: str = "", max_value: float = 100,
                    threshold1: float = 60, threshold2: float = 80) -> go.Figure:
        """Create a gauge chart."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, threshold1], 'color': "lightgray"},
                    {'range': [threshold1, threshold2], 'color': "gray"},
                    {'range': [threshold2, max_value], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(height=300)
        
        return fig
    
    @staticmethod
    def kpi_card(value: float, label: str, icon: str = "📊",
                 trend: float = None, format_str: str = "{:,.0f}") -> go.Figure:
        """Create a KPI card indicator."""
        # This returns a figure that can be displayed in streamlit
        fig = go.Figure(go.Indicator(
            mode="number+gauge+delta" if trend is not None else "number+gauge",
            value=value,
            number={'format': format_str},
            title={'text': f"{icon} {label}"},
            delta={'reference': value * (1 - trend/100) if trend is not None else 0},
            gauge={'axis': {'visible': False}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(height=200)
        
        return fig
    
    @staticmethod
    def area_chart(df: pd.DataFrame, x_col: str, y_col: str,
                   title: str = "", fill_color: str = COLORS['primary']) -> go.Figure:
        """Create an area chart."""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            fill='tozeroy',
            line=dict(color=fill_color, width=2),
            fillcolor=fill_color.replace(')', ',0.3)').replace('rgb', 'rgba') if 'rgb' in fill_color else fill_color,
            name=y_col
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='x unified',
            showlegend=True,
            template='plotly_white',
            height=400
        )
        
        return fig