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

st.set_page_config(
    page_title="Pitch Speed Equivalency Calculator",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], section.main, .block-container {
      background: #ffffff !important;
      color: #111111 !important;
      max-width: 100% !important;
    }
    html, body, [data-testid="stAppViewContainer"] {
      overflow-x: hidden !important;
    }
    header[data-testid="stHeader"], footer, [data-testid="stToolbar"],
    #MainMenu { display: none !important; }
    [data-testid="stMain"] .block-container {
      max-width: 720px !important;
      padding-top: 0.75rem !important;
      padding-bottom: 1.5rem !important;
      padding-left: 12px !important;
      padding-right: 12px !important;
    }
    .stApp, .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown li {
      color: #111111 !important;
    }
    iframe { max-width: 100% !important; }
    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div,
    .js-plotly-plot, .plot-container {
      max-width: 100% !important;
    }
    [data-testid="stExpander"] details {
      border: 2px solid #111111 !important;
      border-radius: 10px !important;
      background: #ffffff !important;
    }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] p,
    [data-testid="stExpander"] li {
      color: #111111 !important;
      font-size: 1rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "selection" not in st.session_state:
    st.session_state.selection = dict(DEFAULT_STATE)


def build_result(selection):
    """Hero copy for the current mounds. The number comes from utils.py."""
    errors = selection_errors(selection)
    if errors:
        return {"error": " ".join(errors)}, None
    speed = selection["speed"]
    from_feet = selection["from_feet"]
    to_feet = selection["to_feet"]
    reaction_time = calculate_reaction_time(speed, from_feet)
    equivalent = equivalent_mph(speed, from_feet, to_feet)
    detail = (
        f"{speed} mph from {mound_label(selection['from_preset'], from_feet)}"
        f" · {reaction_time:.3f} seconds to the plate"
    )
    return {
        "kicker": format_feet(to_feet),
        "mph": format_mph(equivalent),
        "detail": detail,
    }, reaction_time


result, reaction_time = build_result(st.session_state.selection)
reported = field_controls(st.session_state.selection, result)
if reported is not None:
    normalized = normalize_state(reported)
    if normalized != st.session_state.selection:
        st.session_state.selection = normalized
        st.rerun()

selection = st.session_state.selection
speed = selection["speed"]
from_feet = selection["from_feet"]
to_feet = selection["to_feet"]
errors = selection_errors(selection)
if errors:
    for error in errors:
        st.error(error)

if not errors:
    distances = generate_distance_range()
    equiv_speeds = calculate_equivalent_speeds(reaction_time, distances)
    to_on_curve = float(
        calculate_equivalent_speeds(reaction_time, np.array([to_feet]))[0]
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=distances,
            y=equiv_speeds,
            mode="lines",
            name="Equivalent speed",
            line=dict(color="#0b3a82", width=3),
            hovertemplate="%{x:.1f} ft<br>%{y:.1f} mph<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[from_feet],
            y=[speed],
            mode="markers",
            name="Radar",
            marker=dict(
                color="#b00020",
                size=16,
                symbol="star",
                line=dict(color="#111111", width=1),
            ),
        )
    )
    if abs(to_feet - from_feet) > 1e-6:
        fig.add_trace(
            go.Scatter(
                x=[to_feet],
                y=[to_on_curve],
                mode="markers",
                name="Target mound",
                marker=dict(
                    color="#111111",
                    size=12,
                    symbol="diamond",
                    line=dict(color="#111111", width=1),
                ),
            )
        )
        fig.add_vline(x=to_feet, line_dash="dot", line_color="#111111", opacity=0.45)

    fig.add_vline(x=from_feet, line_dash="dot", line_color="#b00020", opacity=0.45)
    fig.update_layout(
        title=dict(
            text="Same reaction time at every distance",
            x=0.0,
            xanchor="left",
            font=dict(size=18, color="#111111"),
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#111111", size=15, family="Arial, Helvetica, sans-serif"),
        hovermode="x unified",
        showlegend=False,
        height=340,
        margin=dict(l=48, r=12, t=52, b=48),
        xaxis=dict(
            title="Release distance (feet)",
            range=[15, 62],
            dtick=5,
            gridcolor="#d5d5d5",
            fixedrange=True,
            title_font=dict(size=15, color="#111111"),
            tickfont=dict(size=13, color="#111111"),
        ),
        yaxis=dict(
            title="Speed (mph)",
            gridcolor="#d5d5d5",
            fixedrange=True,
            title_font=dict(size=15, color="#111111"),
            tickfont=dict(size=13, color="#111111"),
        ),
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False, "responsive": True, "scrollZoom": False},
    )

with st.expander("How to read this"):
    st.markdown(
        """
        - The yellow number is the speed at the **To** mound that gives the batter the same time as the radar reading at the **From** mound.
        - Time to the plate is distance divided by speed. 1 mph is 1.467 feet per second.
        - The chart is that same speed at every distance from 15 ft to 60 ft 6 in. The star is the radar reading.
        - **Swap distances** flips the mounds and leaves the radar speed on From.
        - Your last mounds and speed are remembered on this phone.
        - 8U is 40 ft. 9U and 10U are 46 ft. 11U and 12U are 50 ft. 13U is 54 ft. 14U, high school, college, and MLB are 60 ft 6 in. Little League majors is often 46 ft through 12U — use Custom when your league differs.
        """
    )
