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

# Search Engine Optimization
st.header = "Pitch Speed Equivalency Calculator"
st.text = "Calculate the equivalent pitch speeds for a given pitch speed and distance range."


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

# Initialize session state for speed and distance
if 'speed' not in st.session_state:
    st.session_state.speed = 90
if 'distance' not in st.session_state:
    st.session_state.distance = 60.5

# Preset definitions
speed_presets = {
    "BP": 40,
    "10U": 45,
    "12U": 55,
    "14U": 65,
    "HS": 80,
    "College": 90,
    "MLB": 95
}

distance_presets = {
    "BP": 18.0,
    "10U": 42.0,
    "12U": 46.0,
    "HS": 55.0,
    "Pro": 54.0
}

# Input form
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Pitch Speed (mph)**")
    speed_cols = st.columns(len(speed_presets))
    for i, (label, preset_speed) in enumerate(speed_presets.items()):
        with speed_cols[i]:
            if st.button(label, key=f"speed_{label}", use_container_width=True):
                st.session_state.speed = preset_speed
    
    speed = st.slider(
        "Pitch speed (mph)",
        min_value=1,
        max_value=110,
        value=st.session_state.speed,
        step=1,
        help="Pitch speed in miles per hour",
        label_visibility="collapsed"
    )
    st.session_state.speed = speed

with col2:
    st.markdown("**Distance (ft)**")
    dist_cols = st.columns(len(distance_presets))
    for i, (label, preset_dist) in enumerate(distance_presets.items()):
        with dist_cols[i]:
            if st.button(label, key=f"dist_{label}", use_container_width=True):
                st.session_state.distance = preset_dist
    
    distance = st.slider(
        "Distance (ft)",
        min_value=15.0,
        max_value=60.5,
        value=st.session_state.distance,
        step=0.5,
        help="Enter the distance from pitcher to batter (15-60.5 feet)",
        label_visibility="collapsed"
    )
    st.session_state.distance = distance

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

    # Create interactive chart
    fig = go.Figure()

    # Add equivalent speed line
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=equiv_speeds,
            mode='lines',
            name='Eqv. MPH',
            line=dict(color='#1f77b4', width=3)
        )
    )

    # Add point for initial input
    fig.add_trace(
        go.Scatter(
            x=[distance],
            y=[speed],
            mode='markers+text',
            name='Your Input',
            text=[f"{speed} mph"],
            textposition="top center",
            marker=dict(
                color='#ff4b4b',
                size=15,
                symbol='star',
                line=dict(
                    color='black',
                    width=2
                )
            )
    
        )
    
    )

    # Add reference distances
    common_distances = [20, 30, 43, 46, 55]
    common_distance_names = ["20ft BP", "30ft BP","46ft (10U)", "50ft (12U)", "60.5ft (MLB)"]     
    
    for dist, name in zip(common_distances, common_distance_names):
        # Calculate equivalent speed at this distance
        equiv_speed = calculate_equivalent_speeds(reaction_time, np.array([dist]))[0]

        # Only add reference line if dist does not equal input distance
        if dist != distance:  
            # Add vertical line with label
            fig.add_vline(
                x=dist,
                line_dash="dot",
                line_color="gray",
                opacity=0.5,
                # annotation_text=f"{name}"
            )
    
            # Add point and label
            fig.add_trace(
                go.Scatter(
                    x=[dist],
                    y=[equiv_speed],
                    mode='markers+text',
                    name=name,
                    text=[f"{equiv_speed:.1f} mph"],
                    textposition="top center",
                    marker=dict(
                        size=8,
                        symbol='circle'
                    ),
                    showlegend=True
                )
            )

    # Customize layout
    fig.update_layout(
        title=dict(
            text=f"Equivalent Speeds for {speed} mph at {distance} ft",
            x=0.5,
            xanchor='center'
        ),
        xaxis_title="Release Distance (feet)",
        yaxis_title="Speed (mph)",
        hovermode='x unified',
        showlegend=False,
        legend=dict(
            yanchor="bottom",
            orientation="h",
            y=-0.30,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Add vertical line for input distance
    fig.add_vline(
        x=distance,
        line_dash="dot",
        line_color="red",
        opacity=0.5

    )
    
    # Configure axes
    fig.update_xaxes(
        range=[15, 62],
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
            - The red dot shows your initial input point
            - Hover over the line to see exact values
            - Distance increments are in 0.5 feet
            - Vertical lines mark common distances from release:
              - 60.5ft: Major League Baseball (MLB), released at 55ft*
              - 50ft: 12U Baseball, released at 46ft
              - 46ft: 10U Baseball, released at 43ft
              - 30ft: BP
              - 20ft: BP
            - * FanGraphs Release Point: https://community.fangraphs.com/estimating-pitcher-release-point-distance-from-pitchfx-data/
        """)