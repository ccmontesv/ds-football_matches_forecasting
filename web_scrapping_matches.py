import requests
from bs4 import BeautifulSoup
import pandas as pd

def matches_from_scrapping(url_web,league,jornada):

    # Send a GET request to fetch the page content
    response = requests.get(url_web)
    soup = BeautifulSoup(response.content, "html.parser")
    jornada_block = soup.find("div", {"id":jornada})


    if jornada_block:
        # Find all rows within the "jornada x" block
        rows = jornada_block.find_all('tr', id=lambda x: x and x.startswith('sel_'))

        team_names = []

        for row in rows:
            # Get local team
            local_team = row.find('td', class_='col-equipo-local').find('span', class_='nombre-equipo').get_text(strip=True)
            # Get visitor team
            visitor_team = row.find('td', class_='col-equipo-visitante').find('span', class_='nombre-equipo').get_text(strip=True)

            team_names.append((local_team, visitor_team))
    else:
        print(f"{jornada} block not found.")    
    
    df_web = pd.DataFrame(team_names, columns=['LT', 'VT'])
    
    # Load the CSV from the google sheets link into a DataFrame
    df_xlsx = pd.read_excel("teams/teams_web.xlsx", sheet_name=league)
    
    # Create a mapping from 'web' to 'football_data_uk'
    mapping = dict(zip(df_xlsx['as web'], df_xlsx['football-data_uk']))

    # Replace values in both LT and VT columns of table_1 using the mapping
    df_web['LT'] = df_web['LT'].replace(mapping)
    df_web['VT'] = df_web['VT'].replace(mapping)
    
    return df_web
    