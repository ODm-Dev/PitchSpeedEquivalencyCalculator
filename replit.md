# Pitch Speed Equivalency Calculator

## Overview

A Streamlit-based web application that calculates equivalent pitch speeds at different distances to produce the same reaction time. The tool helps baseball players and coaches understand how pitch speeds translate across various practice distances (15-60.5 feet), enabling more effective training setups.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Framework
- **Streamlit** serves as the complete web framework, handling both UI rendering and application logic
- Single-page application architecture with interactive widgets for user input
- Plotly integration for data visualization (speed equivalency charts)

### Application Structure
- **main.py**: Entry point containing Streamlit UI components, page configuration, and visualization logic
- **utils.py**: Pure utility functions for physics calculations and input validation

### Core Calculations
- Physics-based reaction time calculations converting between speed (mph) and distance (ft)
- Conversion factor: 1 mph = 1.467 ft/s
- Distance range: 15ft to 60.5ft in 0.5ft increments

### State Management
- Streamlit session state for persisting user inputs (speed, distance)
- Preset system for common speed values (partially implemented)

## External Dependencies

### Python Packages
- **streamlit**: Web application framework and UI
- **plotly**: Interactive charting library (graph_objects)
- **numpy**: Numerical calculations and array operations

### No External Services
- No database connections
- No external APIs
- No authentication required
- Purely client-side calculations