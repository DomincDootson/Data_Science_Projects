from bs4 import BeautifulSoup
import shutil
import requests

from Recipe import Recipe 

NEW_VEGAN_URL = "https://www.theguardian.com/food/series/the-new-vegan"


class Recipe_Book():
	
	def scrape_recipes_from_page(self, first_page = True, page_url = NEW_VEGAN_URL):
		if page_url == None: # this is a way to exit the recurive scraping 
			return None

		source = requests.get(page_url).text
		soup = BeautifulSoup(source, "lxml")

		recipe_urls = [recipe['href'] for recipe in soup.find_all("a", class_ = "u-faux-block-link__overlay js-headline-text")]
		#self.recipes = [Recipe(url) for url in recipe_urls]
		print(recipe_urls)

		self.get_next_page(soup, first_page)


	def get_next_page(self, soup, first_page):
		next_page_url = soup.find_all("a", class_ = "button button--small button--tertiary pagination__action--static")
		if ( (not first_page) and len(next_page_url) == 1): # checks if we are on the final page
			return None

		print(next_page_url[-1]['href'])
		self.scrape_recipes_from_page(False, next_page_url[-1]['href'])
		


recipe_book = Recipe_Book()
recipe_book.scrape_recipes_from_page()
	
		
