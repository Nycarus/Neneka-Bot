from bs4 import BeautifulSoup
import requests
from datetime import datetime
from src.utils.logger import setup_logger

class WebScraper:
    @staticmethod
    async def scrape_crunchyroll_events():
        logger = setup_logger('bot.utils.webscraper', '/data/discord.log')

        url = "https://got.cr/priconne-update"
        req = requests.get(url)
        if (not req.ok):
            logger.error("Crunchyroll page request failed.")
            return None

        soup = BeautifulSoup(req.content, 'html.parser')
        
        content = soup.select('div.contents > ul')

        if(not content):
            logger.error("crunchyroll page contains no content.")
            return None

        
        events = []
        
        # Iterate through event and create dictionary
        for li in content[-1].find_all('li', recursive=False):
            try:
                event = li.find(text = True).strip()
                
                # Find opening bracket for date
                startingBracket = -1
                for i in range(len(event)-1,-1,-1):
                    if (event[i] == "("):
                        startingBracket = i
                        break
                
                # Split crunchyroll event string into 2 parts
                eventName, date = event[0:startingBracket].lstrip().rstrip(), event[startingBracket:].strip("(").strip(")").split()
                
                # Check if it's a proper date: (MM/DD/YYYY TIME UTC) or (MM/DD TIME UTC)
                if (date and (date[0].count("/") < 1 or len(date) < 3 or date[0].count("/") > 2)):
                    logger.info("Possible new date or web format.")
                    continue

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
                if (len(date) == 7 and date[0].count("/") >= 1 and date[-3].count("/") >= 1):
                    
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
            except Exception as e:
                logger.error(e)
                logger.error("Something went wrong with creating event. Possible new web format.")
        
        return events