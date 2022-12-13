from bs4 import BeautifulSoup
import requests

class WebScraper:
    @staticmethod
    async def scrape_crunchyroll_events():
        print("Webscraping crunchyroll princess connect news website.")

        url = "https://got.cr/priconne-update"
        req = requests.get(url)
        if (not req.ok):
            print("crunchyroll page request failed.")
            return None

        soup = BeautifulSoup(req.content, 'html.parser')
        
        content = soup.select('div.contents > ul')

        if(not content):
            print("crunchyroll page contains no content.")
            return None

        # Iterate through event and create dictionary
        events = []

        for li in content[-1].find_all('li', recursive=False):
            event = li.find(text = True).strip()
            
            # Find opening bracket for date
            startingBracket = -1
            for i in range(len(event)-1,-1,-1):
                if (event[i] == "("):
                    startingBracket = i
                    break
            
            eventName, date = event[0:startingBracket].lstrip().rstrip(), event[startingBracket:].strip("(").strip(")").split()

            eventDetails = {"event": eventName, "startingDate": date[0:3], "endingDate": date[4:]}

            events.append(eventDetails)
        
        return events