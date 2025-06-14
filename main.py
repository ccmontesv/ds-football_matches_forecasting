import web_scrapping_matches
from matches_results import matches_results
from datetime import datetime  # Import datetime at the top of the module
import time
import warnings
warnings.filterwarnings("ignore")

# Start measuring execution time
start_time = time.time()

# Set how many leagues to include in the analysis
n = 3

# Define seasons using their codes (e.g., 2324 = 2023–2024, 2425 = 2024–2025)
last_season = '2324'
present_season = '2425'

# Define leagues, corresponding CSV codes, and the matchday ("jornada") to analyze
# These lists are sliced to include only the first 'n' items
league = ['inglaterra', 'italia', 'primera'][:n]  # Premier League, Serie A, La Liga
fl_web = ['E0.csv', 'I1.csv', 'SP1.csv'][:n]  # CSV codes for football-data.co.uk
jornada = [25, 25, 24][:n]  # Matchday numbers for each league

# Loop over each league with its corresponding CSV file and matchday
for league, fl_web, jornada in zip(league, fl_web, jornada):
    
    # Build jornada identifier for scraping (e.g., "jornada-25")
    jornada_str = "jornada-" + str(jornada)

    # Build URL to scrape the match calendar from AS Colombia
    url_web = f"https://colombia.as.com/resultados/futbol/{league}/calendario/"

    # Scrape the matches for the specified league and jornada
    df_matches = web_scrapping_matches.matches_from_scrapping(url_web, league, jornada_str)

    # Build URLs to CSV data from football-data.co.uk for last and current season
    fl_web_csv_1 = f"https://www.football-data.co.uk/mmz4281/{last_season}/{fl_web}"
    fl_web_csv_2 = f"https://www.football-data.co.uk/mmz4281/{present_season}/{fl_web}"

    # Compare or process the match data using your custom function
    matches_results(league, fl_web_csv_1, fl_web_csv_2, df_matches)

# Stop timer and calculate total execution time in minutes
end_time = time.time()
execution_time = (end_time - start_time) / 60

# Print execution time
print(f"Execution time: {execution_time:.1f} min")