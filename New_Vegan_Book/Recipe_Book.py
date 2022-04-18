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
		
		if first_page:
			self.recipes = [Recipe(url) for url in recipe_urls]
		else:
			self.recipes += [Recipe(url) for url in recipe_urls]
		#print(recipe_urls)

		self.get_next_page(soup, first_page)
		self.recipes = [recipe for recipe in self.recipes if recipe != None]



	def get_next_page(self, soup, first_page):
		next_page_url = soup.find_all("a", class_ = "button button--small button--tertiary pagination__action--static")
		if ( (not first_page) and len(next_page_url) == 1): # checks if we are on the final page
			return None

		print(next_page_url[-1]['href'])
		self.scrape_recipes_from_page(False, next_page_url[-1]['href'])

	def read_recipes_from_file(self, file_path_for_Index = "Recipe_Cards/Index.txt"):
		self.recipes = []
		with open(file_path_for_Index, 'r') as f:
			file = f.readline().replace('\n', "")
			
			while file !="":
				self.recipes.append(Recipe(file, False))
				file = f.readline().replace('\n',"")
				

			f.close()


	def save_recipe_cards(self, file_path_for_Index = "Recipe_Cards/Index.txt"):
		with open(file_path_for_Index, 'w') as f:
			for recipe in self.recipes:
				if recipe.title != "DONT USE":
					if (recipe != None):
						recipe.save_recipe_card()
						f.writelines(recipe.recipe_card_filename() + '\n')
			f.close()

	def list_of_recipies(self):
		[print(recipe.title) for recipe in self.recipes]
		print(len(self.recipes))
		


recipe_book = Recipe_Book()
#recipe_book.scrape_recipes_from_page()
#recipe_book.save_recipe_cards()
# function to order the recipies 
recipe_book.read_recipes_from_file()
recipe_book.list_of_recipies()
#recipe_book.list_of_recipies()


#recipe = Recipe("Recipe_Cards/Tomato_and_blood_orange_salad_with_ginger_tahini_sauce.txt", False)
#recipe = Recipe("https://www.theguardian.com/food/2022/mar/19/ixta-belfrages-vegan-recipe-for-curried-caramelised-onion-galette")
#recipe.save_recipe_card()
#print(recipe.preamble)