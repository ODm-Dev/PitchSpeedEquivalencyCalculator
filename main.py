import html

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from field_controls import field_controls
from ui_state import (
    DEFAULT_STATE,
    REFERENCES,
    equivalent_mph,
    format_mph,
    normalize_state,
    selection_errors,
)
from utils import (
    calculate_equivalent_speeds,
    calculate_reaction_time,
    generate_distance_range,
)

st.set_page_config(page_title="Pitch Speed Equivalency Calculator", layout="wide")

st.markdown(
    """
    <style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    [data-testid="stMainBlockContainer"] { overflow-x: clip; }
    iframe { max-width: 100%; }
    [data-testid="stMarkdownContainer"] .readout {
      margin: 0.15rem 0 0.35rem;
      font-size: 1.05rem;
      line-height: 1.45;
      color: #31333F;
    }
    [data-testid="stMarkdownContainer"] .readout strong {
      font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if (
    "selection" not in st.session_state
    or not isinstance(st.session_state.selection, dict)
    or "distance" not in st.session_state.selection
):
    st.session_state.selection = dict(DEFAULT_STATE)
else:
    st.session_state.selection = normalize_state(st.session_state.selection)

st.title("⚾ Pitch Speed Equivalency Calculator")
st.markdown(
    """
    Calculate equivalent pitch speeds at different distances that produce the same reaction time.
    Enter your initial speed and distance below to see the equivalency chart.
    """
)

reported = field_controls(st.session_state.selection)
if reported is not None:
    normalized = normalize_state(reported)
    if normalized != st.session_state.selection:
        st.session_state.selection = normalized
        st.rerun()

selection = st.session_state.selection
errors = selection_errors(selection)
for error in errors:
    st.error(error)

if not errors:
    speed = selection["speed"]
    distance = selection["distance"]
    reaction_time = calculate_reaction_time(speed, distance)
    distances = generate_distance_range()
    equiv_speeds = calculate_equivalent_speeds(reaction_time, distances)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=equiv_speeds,
            mode="lines",
            name="Eqv. MPH",
            line=dict(color="#1f77b4", width=3),
            hovertemplate="Release %{x} ft<br>%{y:.1f} mph<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[distance],
            y=[speed],
            mode="markers+text",
            name="Your Input",
            text=[f"{speed} mph"],
            textposition="top center",
            marker=dict(
                color="#ff4b4b",
                size=15,
                symbol="star",
                line=dict(color="black", width=2),
            ),
        )
    )

    for ref_distance, ref_name in REFERENCES:
        equiv_speed = float(
            calculate_equivalent_speeds(reaction_time, np.array([ref_distance]))[0]
        )
        if abs(ref_distance - distance) < 1e-6:
            continue
        fig.add_vline(x=ref_distance, line_dash="dot", line_color="gray", opacity=0.5)
        fig.add_trace(
            go.Scatter(
                x=[ref_distance],
                y=[equiv_speed],
                mode="markers+text",
                name=ref_name,
                text=[f"{equiv_speed:.1f} mph"],
                textposition="top center",
                marker=dict(size=8, symbol="circle"),
                showlegend=True,
            )
        )

    fig.add_vline(x=distance, line_dash="dot", line_color="red", opacity=0.5)
    fig.update_layout(
        title=dict(
            text=f"Equivalent Speeds for {speed} mph at {distance} ft",
            x=0.5,
            xanchor="center",
        ),
        xaxis_title="Release Distance (feet)",
        yaxis_title="Speed (mph)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50),
        clickmode="event+select",
    )
    fig.update_xaxes(range=[15, 62], dtick=5, gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key="equiv_chart",
    )

    tapped = None
    points = []
    if event is not None:
        selection_state = event.get("selection", {}) if hasattr(event, "get") else {}
        points = selection_state.get("points", []) if hasattr(selection_state, "get") else []
    if points:
        point = points[-1]
        try:
            tapped = (float(point["x"]), float(point["y"]))
        except (KeyError, TypeError, ValueError):
            tapped = None

    bits = []
    for ref_distance, ref_name in REFERENCES:
        if abs(ref_distance - distance) < 1e-6:
            continue
        ref_speed = equivalent_mph(speed, distance, ref_distance)
        label = ref_name.split(" (")[0]
        bits.append(f"{html.escape(label)} {ref_distance:g} ft: {html.escape(format_mph(ref_speed))} mph")
    tapped_html = ""
    if tapped is not None:
        tapped_html = (
            f"<strong>At {tapped[0]:g} ft: {html.escape(format_mph(tapped[1]))} mph</strong><br>"
        )
    st.markdown(
        f'<p class="readout">{tapped_html}{" · ".join(bits)}</p>',
        unsafe_allow_html=True,
    )
    st.caption("Tap or drag along the curve to read the speed at that release distance.")

    st.info(f"⏱️ Reaction Time: {reaction_time:.3f} seconds")

with st.expander("How to interpret this chart"):
    st.markdown(
        """
        - The blue line shows equivalent speeds at different distances that give the same reaction time
        - The red star shows your initial input point
        - Tap or hover the line to read a distance
        - Distance increments are in 0.5 feet
        - Vertical lines mark common release distances:
          - 20ft: BP (Batting Practice)
          - 42ft: 10U Baseball
          - 46ft: 12U Baseball
          - 54ft: HS (High School) / Pro
        - A preset sets a typical velocity and release distance together
        - Plus and minus move 1 mph or 0.5 ft. Hold them to move 5
        """
    )
