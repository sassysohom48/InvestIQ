# OpenTrade Analytics — Tech Stack

The "Zero-Cost" Stack — every component is free and open-source.

| Layer                  | Technology                 | Reason                                      |
| :--------------------- | :------------------------- | :------------------------------------------ |
| **Language**           | Python 3.x                 | Open-source industry standard.              |
| **Data Source**        | yfinance                   | Free Yahoo Finance scraper (supports NSE).  |
| **Data Processing**    | Pandas & NumPy             | Open-source data manipulation.              |
| **Technical Analysis** | pandas_ta                  | Open-source indicator library.              |
| **Machine Learning**   | scikit-learn / Prophet     | Open-source forecasting & regression.       |
| **Backend/API**        | FastAPI                    | Lightweight, async, free.                   |
| **Frontend (UI)**      | Streamlit                  | Turns Python scripts into web apps for free.|
| **Database**           | SQLite                     | File-based, zero setup, zero cost.          |
| **Deployment**         | Streamlit Cloud            | Free hosting from GitHub.                   |

## Why this stack?
- **No paid APIs** — yfinance scrapes public data.
- **No cloud bills** — Streamlit Cloud hosts for free.
- **No DB server** — SQLite is a single file.
- **Python-only** — one language for both backend and frontend logic.
