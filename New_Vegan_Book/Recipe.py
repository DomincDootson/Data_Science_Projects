from bs4 import BeautifulSoup
import shutil
import requests

class Recipe(object):
	
	## Web Scraping and Init ##
	## --------------------- ##
	def __init__(self, web_address):
		source = requests.get(web_address).text
		soup = BeautifulSoup(source, "lxml")

		self.title = self.get_title(soup)
		print("Title ", self.title)

		holding = soup.find_all('p', class_ = 'dcr-3jlghf')

		
		self.date = soup.find('summary', class_ = 'dcr-12fpzem').text
		print(self.date)

		self.preamble = holding[0].text
		print(self.preamble)
		self.prep, self.cook, self.serves = self.get_info(holding[1])


		

		self.ingredients, self.steps = [], [] # Ingredience will be a list of lists. if more than one, the second will have title for the list
		self.split_ingredients_and_recipe(holding[2:])

		self.image_filepath = "Recipe_Pictures/" +self.title.replace(" ", "_") + ".png"
		self.get_image(soup)




	def get_title(self, soup):
		return soup.find('h2').text

	def get_info(self, soup):
		return soup.text.split("Cook")[0].strip(), "Prep " + (soup.text.split("Cook"))[1].split("Serves")[0].strip(), "Serves " +(soup.text.split("Cook"))[1].split("Serves")[1].strip()

	def get_image(self, soup):
		image_url = soup.find('img', class_ = "dcr-1989ovb")['src']
		print(image_url)
		
		r = requests.get(image_url, stream = True)

		r.raw.decode_content = True
		with open(self.image_filepath,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		
	def split_ingredients_and_recipe(self, soups):
		ingredients, recipe = [], []

		for soup in soups:
			if "<strong>" in str(soup): # Each group of ingredience will contain a <strong> tag
				strings = str(soup).split("<br/>")
				self.ingredients.append([self.remove_html_tags(string) for string in strings][:])

			else:
				self.steps.append(self.remove_html_tags(str(soup)))

	def remove_html_tags(self, string):
		split_string, string =  [char for char in string], '' # you don't need to split it 
		is_in_tag = False

		for char in split_string:
		
			if (char == '<' or is_in_tag):
				is_in_tag = True 
				if char == '>':
					is_in_tag = False
			else:
				string += char

		return string


	## Recipe Card Reading & Writing ##
	## ----------------------------- ##

	def list_of_preamble(self):
		return [self.title, self.preamble, self.date, self.prep, self.cook, self.serves]

	def save_recipe_card(self, file_path = 'testing.txt'):
		if file_path == 'testing.txt':
			file_path = "Recipe_Cards/" + self.title.replace(" ", "_") + ".txt"

		with open(file_path, 'w') as f:
			f.writelines('\n'.join(self.list_of_preamble()))
			f.write('\n')
			if len(self.ingredients) == 1: # For the ingrdience and the step we will seperate each element with a '|'
				f.writelines('|'.join(self.ingredients))
				f.write('\n')
			else:
				f.writelines('||'.join(['|'.join(part) for part in self.ingredients])) # Different parts of ingredience will be seperated by '||'
				f.write('\n')

			f.writelines('|'.join(self.steps))
			f.close()

	def read_recipe_card(self, file_path):
		with open(file_path, 'r') as f:
			self.title, self.preamble, self.date, self.prep, self.cook, self.serves = f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', "")

			self.ingredients = [part.split('|') for part in (f.readline().replace('\n', "")).split('||')]
			self.steps = (f.readline().replace('\n', "")).split('|')


#recipe = Recipe("https://www.theguardian.com/food/2022/jan/15/meera-sodhas-vegan-recipe-miso-coconut-winter-greens-laing")