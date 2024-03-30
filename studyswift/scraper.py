from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()


@app.get("/scrape-conferences/")
async def scrape_conferences():
    print("Executing scrape_conferences function...")
    url = "https://www.allconferencealert.com/london.html"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        conference_table = soup.find("table", class_="table")
        if conference_table:
            conferences = []
            for row in conference_table.find_all("tr")[1:]:  # Skip header row
                columns = row.find_all("td")
                conference_date = columns[0].text.strip()
                conference_name = columns[1].text.strip()
                conferences.append({"date": conference_date, "name": conference_name})
            return {"conferences": conferences}
        else:
            return {"error": "Conference table not found"}
    else:
        return {"error": "Failed to fetch data"}
