# psychtoday-web-scraper

### This project uses *Flask* and *BeautifulSoup* to show how to scrape the web for information based on user input.

`webscraper.py` 
<br></br>
This file contains the main scraper work. It routes the user to a form, where they can put in the 
location of the area they would like to scrape for therapists. We read this in from the form with a post request upon submit in `get_data()`. We then
use the `lc` variable as input for `scrape()`. `scrape()` returns all of the collected data and prints it by rendering the `results.html` template. 
