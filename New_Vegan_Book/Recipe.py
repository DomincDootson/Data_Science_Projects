from bs4 import BeautifulSoup
import shutil
import requests

class Recipe(object):
	
	## Web Scraping and Init ##
	## --------------------- ##
	def __init__(self, web_address):
		source = requests.get(web_address).text
		soup = BeautifulSoup(source, "lxml")

		self.get_title(soup)
		self.get_date(soup) 

		holding = soup.find_all('p', class_ = 'dcr-3jlghf')

		self.get_preamble(holding)		
		self.get_info(holding)
		self.get_ingredients_and_steps(holding)



		'''
		self.image_filepath = "Recipe_Pictures/" +self.title.replace(" ", "_") + ".png"
		self.get_image(soup)'''




	def get_title(self, soup):
		self.title = soup.find('h2').text

	def get_date(self, soup):
		if soup.find('summary', class_ = 'dcr-12fpzem') != None:
			self.date = soup.find('summary', class_ = 'dcr-12fpzem').text
		if (soup.find('div', class_ = 'dcr-km9fgb') != None):	
			self.date = soup.find('div', class_ = 'dcr-km9fgb').text
		print(self.date)
	
	def get_preamble(self, soup): 
		self.preamble = ""
		for i, each in enumerate(soup):
			if (not self.contains_strong_tag(each)):
				self.preamble += each.text + '\n'
			else:
				del soup[:i] # Passing a list is really passing a pointer
				break


	def get_info(self, soup): 
		self.info = {"Prep" : None, "Cook" : None, "Serves" : None, "Chill": None}
		have_we_got_info, text = False, soup[0].text
		positions_of_key_words = []
		for key in self.info:
			positions_of_key_words.append(text.find(key))
			have_we_got_info = True

		positions_of_key_words.sort()
		positions_of_key_words = [x for x in positions_of_key_words if x >= 0]

		for i in range(len(positions_of_key_words)):
			if (positions_of_key_words[i] != positions_of_key_words[-1]):
				positions_of_key_words[i] = [positions_of_key_words[i], positions_of_key_words[i+1]]

			else:
				positions_of_key_words[-1] = [positions_of_key_words[-1], len(text)]


		for pair in positions_of_key_words:
			for key in self.info:
				if key in text[pair[0]:pair[1]]:
					self.info[key] = text[pair[0]:pair[1]].replace(key, "").strip()
			
		if have_we_got_info:
			del soup[0]


	def get_image(self, soup):
		image_url = soup.find('img', class_ = "dcr-1989ovb")['src']
		print(image_url)
		
		r = requests.get(image_url, stream = True)

		r.raw.decode_content = True
		with open(self.image_filepath,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		
	def get_ingredients_and_steps(self, soups):
		self.ingredients, self.steps = [], []

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

	def contains_strong_tag(self, soup):
		if len(soup.findChildren('strong')) == 0:
			return False
		else:
			return True



	## Recipe Card Reading & Writing ##
	## ----------------------------- ##

	def list_of_preamble(self):
		return [self.title, self.preamble, self.date]

	def save_recipe_card(self, file_path = 'testing.txt'):
		if file_path == 'testing.txt':
			file_path = "Recipe_Cards/" + self.title.replace(" ", "_") + ".txt"

		with open(file_path, 'w') as f:
			f.writelines('\n\n'.join(self.list_of_preamble()))
			f.write('\n\n')

			for key in self.info:
				if self.info[key] != None:
					f.writelines(key + ": " + self.info[key] + '\n')
			f.writelines('\n')

			if len(self.ingredients) == 1: # For the ingrdience and the step we will seperate each element with a '|'
				f.writelines('\n'.join(self.ingredients[0]))
				f.write('\n\n')
			else:
				f.writelines('\n\n'.join(['\n'.join(part) for part in self.ingredients])) # Different parts of ingredience will be seperated by '||'
				f.write('\n\n')

			f.writelines('\n'.join(self.steps))
			f.close()

	def read_recipe_card(self, file_path):
		with open(file_path, 'r') as f:
			self.title, self.preamble, self.date, self.prep, self.cook, self.serves = f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', ""), f.readline().replace('\n', "")

			self.ingredients = [part.split('|') for part in (f.readline().replace('\n', "")).split('||')]
			self.steps = (f.readline().replace('\n', "")).split('|')


recipe = Recipe("https://www.theguardian.com/lifeandstyle/2017/aug/05/samphire-potato-chickpea-chaat-recipe-vegan-meera-sodha")
#recipe = Recipe("https://www.theguardian.com/food/2022/mar/19/ixta-belfrages-vegan-recipe-for-curried-caramelised-onion-galette")
recipe.save_recipe_card()