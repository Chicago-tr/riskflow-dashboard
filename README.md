# Futures Risk Monitor

A replay driven dashboard for monitoring futures exposure, P&L, alerts, and latency in a workflow similar to that of a trading desk; designed to simulate a trading support environment.

## Highlights

- Real time monitoring with replayed market data.
- Position, exposure, and P&L tracking.
- Risk checks and alerting.
- Latency aware event handling.
- A separate research notebook for microstructure exploration and signal testing.

## Overview

This project was built to demonstrate tools similar to those used in a trading/risk monitoring environment. The main app focuses on visibility, control, and clear decision support, whilst the notebook provides a smaller research sandbox for testing ideas and exploring feature behavior.

## Project Structure

- app.py: streamlit dashboard used for monitoring.
- notebooks/: jupyter notebook for exploratory analysis and signal testing.
- src/: synthetic data generation (replay.py), features analysis (microstructure.py), risk monitoring (config.py, risk.py), signal processing (pipeline.py)

## How It Works

1. Market and position data are loaded or replayed.
2. The system computes exposure, P&L, and basic risk metrics.
3. Rule checks flag unusual conditions or limit breaches.
4. The dashboard surfaces the most important information for quick review.
5. The notebook can be used separately to inspect research questions and test signals.

 ## Setup

```bash
git clone https://github.com/Chicago-tr/riskflow-dashboard.git
cd riskflow-dashboard
pip install -r requirements.txt
```

## Run the Project
To view in browser:
```bash
streamlit run app.py
```

## Future Work

- Add richer alerting and notification options.
- Improve the UI with more granular views.
- Expand the research notebook with more feature engineering.
- Add testing, logging, and configuration management.
- Demo with live market data.

