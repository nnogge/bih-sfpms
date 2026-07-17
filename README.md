# BIH Solutions Strategic Financial Planning Management System

A Streamlit-based pilot of the Strategic Financial Planning Management System (SFPMS) developed for the DBA applied and action research study at BIH Solutions.

## Features

- Role-based dashboards
- Main, Optimistic and Pessimistic scenario switching
- Dynamic financial, risk and resource analytics
- Research baseline dashboard
- CSV, XLSX and TXT Data Import Centre
- Data validation and import history
- SQLite pilot database
- Risk, stakeholder, resource, workflow and decision-gate modules

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app normally opens at:

```text
http://localhost:8501
```

## Deploy to Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload every file and folder from this repository package.
3. Open Streamlit Community Cloud.
4. Select the repository and the `main` branch.
5. Set the main file path to:

```text
app.py
```

6. Deploy.

## Repository structure

```text
.
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
├── DEPLOYMENT_GUIDE.txt
├── LICENSE
├── .gitignore
├── .streamlit/
│   └── config.toml
└── sample_data/
    ├── BIH_SFPMS_Pilot_Data_Pack.xlsx
    ├── research_baseline.csv
    ├── scenario_assumptions.csv
    ├── monthly_budget.csv
    ├── cash_flow_forecast.csv
    ├── risk_register.csv
    ├── stakeholders.csv
    ├── resources.csv
    ├── workflow_gates.csv
    └── corrective_actions.csv
```

## Data classifications

The repository distinguishes:

- Research baseline
- Actual—pending reconciliation
- Forecast
- Scenario assumption
- Simulated pilot data
- Post-intervention actual

Simulated data and scenario assumptions must not be presented as actual BIH Solutions outcomes.

## Important pilot limitation

SQLite is suitable for a demonstration or limited pilot. Streamlit Community Cloud may restart the application, so operational use should later move to persistent storage such as PostgreSQL, Supabase or another managed database.
