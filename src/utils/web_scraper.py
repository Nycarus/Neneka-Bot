from bs4 import BeautifulSoup
import requests
from datetime import datetime

class WebScraper:
    @staticmethod
    async def scrape_crunchyroll_events():
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
            
            # Split crunchyroll event string into 2 parts
            eventName, date = event[0:startingBracket].lstrip().rstrip(), event[startingBracket:].strip("(").strip(")").split()
            
            # Add seconds to date
            if (date[1].count(":")==1):
                date[1] += ":00"

            # Add current year to date if it does not exist, because it defaults to 1900
            if (date[0].count('/') == 1):
                date[0] += "/" + str(datetime.now().year)

            startDateString = " ".join(date[0:2])

            # Convert date string to datetime format
            startDate = datetime.strptime(startDateString, '%m/%d/%Y %H:%M:%S')


            # Check if there's an end date
            if (len(date) > 5):
                
                # Add seconds to date
                if (date[-2].count(":")==1):
                    date[-2] += ":00"

                # Add current year to date if it does not exist, because it defaults to 1900
                if (date[-3].count("/")==1):
                    date[-3] += "/" + str(datetime.now().year)
                
                endDateString = " ".join(date[4:-1])

                # Convert date string to datetime format
                endDate = datetime.strptime(endDateString, '%m/%d/%Y %H:%M:%S')
            else:
                endDate = None

            eventDetails = {"event": eventName, "startDate": startDate, "endDate": endDate}
            events.append(eventDetails)
        
        return events