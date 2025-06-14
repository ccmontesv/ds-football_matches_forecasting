# Football Matches Forecasting

This project predicts outcomes of football (soccer) matches using web scraping and a statistical model based on the **Dixon-Coles Poisson model**. It scrapes upcoming fixtures from [AS Colombia](https://colombia.as.com), fetches past results from [football-data.co.uk](https://www.football-data.co.uk), and forecasts the probability of a **home win**, **away win**, or **draw**.

---

## Project Features

- Web scraping of upcoming fixtures (team names and matchdays)
- Team name normalization using an Excel mapping table
- Collection of historical match data (goals, shots on target)
- Custom Poisson model with time-decay weighting (Dixon-Coles)
- Match simulation with outcome probability matrices
- Output stored in timestamped `.txt` files
- Modular Python design and ready-to-use Conda/Pip environment

---

## Project Structure

```
football_matches_forecasting/
├── main.py                         # Main entry point: scraping + forecasting
├── matches_results.py              # Statistical modeling & match simulation logic
├── web_scrapping_matches.py        # Web scraping logic (AS Colombia)
├── requirements.txt                # pip-compatible dependencies
├── environment.yml                 # Conda environment definition (recommended)
├── teams/
│   └── teams_web.xlsx              # Team name mapping (AS site → football-data.co.uk)
├── results/                        # Output predictions (e.g., Results_2025-06-14_15.txt)
├── notebooks/                          # (Optional) Unit test scripts
└── README.md                       # Project documentation
└── .gitignore.yml                  # files not to send to Github repo
```

---

## How to Get Started

### 2. Set Up the Environment

#### Option A: Use Conda (recommended)
```bash
conda env create -f environment.yml
conda activate matches_forecasting
```

#### Option B: Use pip (if you don't use Conda)
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3. Run the Project

Make sure the mapping file `teams/teams_web.xlsx` exists and includes the correct sheet names (`inglaterra`, `italia`, `primera`), then:

```bash
python main.py
```

This will:
- Scrape the upcoming jornada from AS Colombia for England, Italy, and Spain
- Fetch match result CSVs from [football-data.co.uk](https://www.football-data.co.uk)
- Fit the model using time-weighted historical performance
- Output probabilities for each upcoming match in a `.txt` file inside `results/`

---

## Output Format

Each prediction file (e.g., `results/Results_2025-06-14_15.txt`) includes:

```
*** inglaterra ***

Arsenal: 48.23%,     Avg Shots: 5.4
Manchester Utd: 22.15%,     Avg Shots: 3.7
Draw: 29.62%,        Shot Diff: 1.7
```

---

## How It Works

- `web_scrapping_matches.py`:
  - Extracts home/away teams from jornada pages on AS Colombia
  - Normalizes names using `teams_web.xlsx`

- `matches_results.py`:
  - Loads historical CSVs from football-data.co.uk
  - Applies time-decay to weight recent matches more
  - Fits team-specific attack/defense strengths with `scipy.optimize.minimize`
  - Uses a Dixon-Coles adjusted Poisson model to simulate outcomes
  - Calculates outcome probabilities and average shots on target

---


## Dependencies

Key libraries:
- `pandas`, `numpy`, `scipy`, `openpyxl`
- `requests`, `beautifulsoup4`, `lxml`
- `matplotlib`, `seaborn` (optional for visualizations)

Install with:

```bash
pip install -r requirements.txt
```
or

```bash
conda env create -f environment.yml
```

---

## Environment

The environment is tracked in two formats:

- `environment.yml` – for full Conda environment with exact specs
- `requirements.txt` – for pip users

You can regenerate the lock-free environment file by running:
```bash
pip freeze > requirements.txt
```

