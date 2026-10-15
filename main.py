import html

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from field_controls import field_controls
from ui_state import (
    DEFAULT_STATE,
    equivalent_mph,
    format_feet,
    format_mph,
    mound_label,
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
    .equiv { margin: 0.15rem 0 0.55rem; }
    .equiv-label,
    .equiv-value,
    .equiv-detail { margin: 0; }
    [data-testid="stMarkdownContainer"] .equiv-label {
      font-size: 14px;
      line-height: 1.4;
      color: rgba(49, 51, 63, 0.6);
    }
    [data-testid="stMarkdownContainer"] .equiv-value {
      font-size: 3rem;
      line-height: 1.1;
      font-weight: 600;
      letter-spacing: -0.03em;
      color: #31333F;
      font-variant-numeric: tabular-nums;
    }
    [data-testid="stMarkdownContainer"] .equiv-value span {
      font-size: 1.05rem;
      font-weight: 400;
      letter-spacing: 0;
      margin-left: 0.28rem;
      color: rgba(49, 51, 63, 0.55);
    }
    [data-testid="stMarkdownContainer"] .equiv-detail {
      margin-top: 0.2rem;
      font-size: 1rem;
      line-height: 1.45;
      color: rgba(49, 51, 63, 0.8);
    }
    [data-testid="stMainBlockContainer"] { overflow-x: clip; }
    iframe { max-width: 100%; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "selection" not in st.session_state:
    st.session_state.selection = dict(DEFAULT_STATE)

st.title("⚾ Pitch Speed Equivalency Calculator")
st.markdown(
    """
    Calculate equivalent pitch speeds at different distances that produce the same reaction time.
    """
)

result_slot = st.container()
reported = field_controls(st.session_state.selection)
if reported is not None:
    normalized = normalize_state(reported)
    if normalized != st.session_state.selection:
        st.session_state.selection = normalized
        st.rerun()

selection = st.session_state.selection
errors = selection_errors(selection)

with result_slot:
    if errors:
        for error in errors:
            st.error(error)
    else:
        speed = selection["speed"]
        from_feet = selection["from_feet"]
        to_feet = selection["to_feet"]
        reaction_time = calculate_reaction_time(speed, from_feet)
        equivalent = equivalent_mph(speed, from_feet, to_feet)
        detail = (
            f"{speed} mph from {mound_label(selection['from_preset'], from_feet)}"
            f" · {reaction_time:.3f} seconds to the plate"
        )
        st.markdown(
            f"""
            <div class="equiv" role="status" aria-live="polite" aria-atomic="true">
              <div class="equiv-label">Equivalent at {html.escape(format_feet(to_feet))}</div>
              <div class="equiv-value">{html.escape(format_mph(equivalent))} <span>mph</span></div>
              <div class="equiv-detail">{html.escape(detail)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "8U is 40 ft. 9U and 10U are 46 ft. 11U and 12U are 50 ft. 13U is 54 ft. "
    "14U, high school, college, and MLB are 60 ft 6 in. "
    "Little League majors often stays at 46 ft through 12U — use Custom if yours differs."
)

if not errors:
    distances = generate_distance_range()
    equiv_speeds = calculate_equivalent_speeds(reaction_time, distances)
    to_speed = float(calculate_equivalent_speeds(reaction_time, np.array([to_feet]))[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=equiv_speeds,
            mode="lines",
            name="Eqv. MPH",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[from_feet],
            y=[speed],
            mode="markers+text",
            name="Your input",
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
    if abs(to_feet - from_feet) > 1e-6:
        fig.add_vline(x=to_feet, line_dash="dot", line_color="gray", opacity=0.5)
        fig.add_trace(
            go.Scatter(
                x=[to_feet],
                y=[to_speed],
                mode="markers+text",
                name=format_feet(to_feet),
                text=[f"{to_speed:.1f} mph"],
                textposition="top center",
                marker=dict(size=8, symbol="circle"),
            )
        )
    fig.add_vline(x=from_feet, line_dash="dot", line_color="red", opacity=0.5)
    fig.update_layout(
        title=dict(
            text=f"Equivalent Speeds for {speed} mph at {format_feet(from_feet)}",
            x=0.5,
            xanchor="center",
        ),
        xaxis_title="Release Distance (feet)",
        yaxis_title="Speed (mph)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50),
    )
    fig.update_xaxes(range=[15, 62], dtick=5, gridcolor="lightgray")
    fig.update_yaxes(gridcolor="lightgray")
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"⏱️ Reaction Time: {reaction_time:.3f} seconds")

with st.expander("How to interpret this chart"):
    st.markdown(
        """
        - The blue line shows equivalent speeds at different distances that give the same reaction time
        - The red star is the radar reading at the From mound
        - The number above the chart is that same reaction time at the To mound
        - Swipe a row to move through levels, then tap a chip to select it
        - Plus and minus next to pitch velo change the speed by 1 mph
        - 1 mph is 1.467 feet per second
        - 8U is 40 ft, 9U and 10U are 46 ft, 11U and 12U are 50 ft, 13U is 54 ft, and 14U through MLB are 60 ft 6 in. Little League majors is often 46 ft through 12U — Custom is at the end of each distance row
        """
    )
