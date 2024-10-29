import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_actor_filmography(actor_name):
    """
    Scrapes the actor's filmography from IMDb and returns it as a DataFrame.
    """
    try:
        # Replace spaces with '+' for the URL
        formatted_actor_name = actor_name.replace(" ", "+")
        url = f"https://www.imdb.com/find?q={formatted_actor_name}&s=nm&exact=true&ref_=fn_al_nm_ex"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the first actor's link
        actor_link_element = soup.find("td", class_="result_text").find("a")
        if not actor_link_element:
             print(f"No actor found with the name '{actor_name}'. Please check the spelling or try a different search.")
             return None
        actor_url = "https://www.imdb.com" + actor_link_element["href"]
        
        # Fetch actor's page
        actor_page = requests.get(actor_url)
        actor_page.raise_for_status()
        actor_soup = BeautifulSoup(actor_page.content, "html.parser")

        # Extract filmography
        filmography_section = actor_soup.find("div", id="filmography")
        if not filmography_section:
          print(f"No Filmography section found for {actor_name}")
          return None

        # Extract films from the filmography section
        films = []
        film_list = filmography_section.find_all("div", class_="filmo-row")
        if not film_list:
            print(f"No films found for {actor_name}")
            return None
        for film in film_list:
            title_element = film.find("a", class_="ipc-metadata-list-summary-item__t")
            title = title_element.text.strip() if title_element else ""
            year_element = film.find("span", class_="ipc-metadata-list-summary-item__li")
            year = year_element.text.strip() if year_element else ""
            films.append({"Title": title, "Year": year})
        
        df = pd.DataFrame(films)

        # Convert the 'Year' column to numeric, coercing errors to NaN
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        
        #Sort by year descending
        df = df.sort_values(by="Year", ascending=False, na_position="last")


        return df
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the request: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None



actor_name = input("Enter the actor's name: ")  # Example: "Tom Hanks"
filmography = get_actor_filmography(actor_name)

if filmography is not None:
 filmography