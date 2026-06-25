# InvestIQ — Tech Stack

The "Zero-Cost" AI Stack — every component is free, open-source, and Python-native.

| Layer                  | Technology                 | Reason                                      |
| :--------------------- | :------------------------- | :------------------------------------------ |
| **Language**           | Python 3.12                | Industry standard for data & AI.            |
| **Data Source**        | yfinance / duckduckgo      | Free historical market data and live news.  |
| **Data Processing**    | Pandas & NumPy             | Fast, vectorized data manipulation.         |
| **Technical Analysis** | pandas_ta                  | Comprehensive technical indicator library.  |
| **Machine Learning**   | scikit-learn / XGBoost     | Feature-rich regression and boosting.       |
| **Deep Learning**      | TensorFlow / Keras         | LSTM neural networks for time-series.       |
| **NLP Sentiment**      | VADER Sentiment            | Pre-trained lexicon for fast sentiment scoring. |
| **Frontend (UI)**      | Streamlit                  | React-based, fully Python-driven dashboard. |
| **Styling**            | Custom CSS Injection       | Advanced UI, hover effects, dark/light themes. |
| **Database**           | SQLite                     | File-based, zero setup, local multi-user store. |
| **Auth Security**      | passlib (bcrypt)           | Industry-standard password hashing.         |
| **Deployment**         | Streamlit Community Cloud  | Free continuous deployment from GitHub.     |

## Why this stack?
- **No paid APIs** — Leverages public APIs and scraping (yfinance, ddg).
- **No cloud bills** — Streamlit Cloud hosts for free.
- **No DB server** — SQLite runs locally as a single lightweight file.
- **Python-only** — A single, cohesive language for data science, AI, and frontend rendering without context switching to Javascript/React.
