import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils import (
    calculate_reaction_time,
    calculate_equivalent_speeds,
    generate_distance_range,
    validate_inputs
)

# Page configuration
st.set_page_config(
    page_title="Pitch Speed Equivalency Calculator",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .st-emotion-cache-16idsys p {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("⚾ Pitch Speed Equivalency Calculator")
st.markdown("""
    Calculate equivalent pitch speeds at different distances that produce the same reaction time.
    Enter your initial speed and distance below to see the equivalency chart.
""")

# Input form
col1, col2 = st.columns(2)
with col1:
    speed = st.number_input(
        "Enter pitch speed (mph)",
        min_value=1,
        max_value=200,
        value=90,
        step=1,
        help="Enter the initial pitch speed in miles per hour"
    )

with col2:
    distance = st.number_input(
        "Enter distance (ft)",
        min_value=15.0,
        max_value=60.5,
        value=60.5,
        step=0.5,
        help="Enter the distance from pitcher to batter (15-60.5 feet)"
    )

# Validate inputs
errors = validate_inputs(speed, distance)
if errors:
    for error in errors:
        st.error(error)
else:
    # Calculate initial reaction time
    reaction_time = calculate_reaction_time(speed, distance)
    
    # Generate distance range and calculate equivalent speeds
    distances = generate_distance_range()
    equiv_speeds = calculate_equivalent_speeds(reaction_time, distances)
    
    # Round speeds to whole numbers
    equiv_speeds = np.round(equiv_speeds)
    
    # Create interactive chart
    fig = go.Figure()
    
    # Add equivalent speed line
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=equiv_speeds,
            mode='lines',
            name='Equivalent Speeds',
            line=dict(color='#1f77b4', width=3)
        )
    )
    
    # Add point for initial input
    fig.add_trace(
        go.Scatter(
            x=[distance],
            y=[speed],
            mode='markers',
            name='Initial Point',
            marker=dict(
                color='red',
                size=12,
                symbol='star'
            )
        )
    )
    
    # Customize layout
    fig.update_layout(
        title=dict(
            text=f"Equivalent Speeds for {speed} mph at {distance} ft",
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Distance (feet)",
        yaxis_title="Speed (mph)",
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Configure axes
    fig.update_xaxes(
        range=[15, 61],
        dtick=5,
        gridcolor='lightgray'
    )
    fig.update_yaxes(
        gridcolor='lightgray'
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display reaction time
    st.info(f"⏱️ Reaction Time: {reaction_time:.3f} seconds")
    
    # Additional information
    with st.expander("How to interpret this chart"):
        st.markdown("""
            - The blue line shows equivalent speeds at different distances that give the same reaction time
            - The red star shows your initial input point
            - Hover over the line to see exact values
            - All speeds are rounded to whole numbers
            - Distance increments are in 0.5 feet
        """)
