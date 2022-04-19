from bs4 import BeautifulSoup
import shutil
import requests
from datetime import datetime

class Recipe(object):
	
	## Web Scraping and Init ##
	## --------------------- ##
	def __init__(self, address, is_Web_Address = True):
		if is_Web_Address:	
			if "weekly-meal-plan" in address:
				self.title = "DONT USE"
				return None
			if "https://www.theguardian.com/lifeandstyle/2018/jan/27/meera-sodhas-vegan-swede-laksa-recipe" in address:
				self.title = "DONT USE"
				return None

			source = requests.get(address).text
			soup = BeautifulSoup(source, "lxml")

			self.get_title(soup)
			'''self.get_date(soup) 

			holding = soup.find_all('p', class_ = 'dcr-3jlghf')

			self.get_preamble(holding)		
			self.get_info(holding)
			self.get_ingredients_and_steps(holding)''' 

			self.get_image(soup)
		else:
			self.read_recipe_card(address)

		

	def get_title(self, soup):
		self.title = soup.find('h2').text
		print(self.title)

	def get_date(self, soup):
		if soup.find('summary', class_ = 'dcr-12fpzem') != None:
			self.date = soup.find('summary', class_ = 'dcr-12fpzem').text
		if (soup.find('div', class_ = 'dcr-km9fgb') != None):	
			self.date = soup.find('div', class_ = 'dcr-km9fgb').text
		self.convert_str_2_datetime()
	
	def get_preamble(self, soup): 
		self.preamble = ""
		for i, each in enumerate(soup):
			if (not self.contains_strong_tag(each)):
				self.preamble += each.text + '\n'
			else:
				del soup[:i] # Passing a list is really passing a pointer
				break
		self.preamble = self.preamble[:-1] # For formatting reasons, we don't want the file '\n' char

	
	def initialise_info(self):
		self.info = {"Prep" : None, "Cook" : None, "Chill": None, "Rest" : None, "Soak" : None, "Proving" : None, "Freeze" : None, "Serves" : None, "Makes" : None}


	def get_info(self, soup): 
		self.initialise_info()
		text = soup[0].text
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
			
		if not self.is_info_empty():
			del soup[0]

	def image_filepath(self):
		string = "Recipe_Pictures/" +self.title.replace(" ", "_") + ".png"
		string = string.replace("'", '')
		return string.replace('"','')


	def get_image(self, soup):
		image_url = soup.find('img', class_ = "dcr-1989ovb")['src']
		
		r = requests.get(image_url, stream = True)
		r.raw.decode_content = True
		with open(self.image_filepath(),'wb') as f:
			shutil.copyfileobj(r.raw, f)
		
	def get_ingredients_and_steps(self, soups):
		self.ingredients, self.steps = [], []
		for soup in soups:
			if "<strong>" in str(soup): # Each group of ingredience will contain a <strong> tag
				strings = str(soup).split("<br/>")
				self.ingredients.append([self.remove_html_tags(string) for string in strings][:])
			else:
				self.steps.append(self.remove_html_tags(str(soup)))

		if self.steps[-1] == '\n':
			self.steps.remove(-1)

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


	## Datetime formatting ##
	## ------------------- ## 

	def convert_str_2_datetime(self):
		self.date = datetime.strptime(self.date, '%a %d %b %Y %H.%M %Z')	

	def string_from_datetime(self):
		return datetime.strftime(self.date, '%a %d %b %Y %H.%M %Z') + "GMT"

	## Recipe Card Reading & Writing ##
	## ----------------------------- ##

	def list_of_preamble(self):
		return [self.title, self.preamble, self.string_from_datetime()]

	def is_info_empty(self):
		is_empty = True
		for key in self.info:
			if self.info[key] != None:
				is_empty = False
				pass 
		return is_empty

	def recipe_card_filename(self):
		return "Recipe_Cards/" + self.title.replace(" ", "_") + ".txt"

	def save_recipe_card(self, file_path = 'testing.txt'):
		if file_path == 'testing.txt':
			file_path = self.recipe_card_filename()

		with open(file_path, 'w') as f:
			f.writelines('\n\n'.join(self.list_of_preamble()))
			f.write('\n\n')

			if (not self.is_info_empty()):
				for key in self.info:
					if self.info[key] != None:
						f.writelines(key + ": " + self.info[key] + '\n')
				f.writelines('\n')
				
			if len(self.ingredients) == 1: # For the ingrdience and the step we will seperate each element with a '|'
				f.writelines('\n'.join(self.ingredients[0]))
				f.write('\n\n')
			else:
				f.writelines('\n\n'.join(['\n'.join(part) for part in self.ingredients])) 
				f.write('\n\n')

			f.writelines("Steps\n")
			f.writelines('\n'.join(self.steps))
			f.close()

	def read_recipe_card(self, file_path):
		with open(file_path, 'r') as f:
			self.read_title(f)
			self.read_preamble(f)
			self.read_date(f)
			line = self.read_info(f)
			self.read_ingredients(f, line)
			self.read_steps(f)
			f.close()

	def read_title(self, file):
		self.title = file.readline().replace('\n', "")
		print(self.title)
		file.readline()

	def read_preamble(self, file):
		line, self.preamble = file.readline(), ""
		while line != '\n':
			self.preamble += line
			line = file.readline()
		self.preamble = self.preamble[:-1]

	def read_date(self, file):
		self.date = file.readline().replace('\n', "")
		self.convert_str_2_datetime()
		file.readline()

	def read_info(self, file):
		self.initialise_info()
		line = file.readline()
		if not ':' in line:
			return line

		while line != '\n' or (':' in line): # We need the second conditional for those recipes that don't have info
			position_of_colon = line.find(':')
			self.info[line[:position_of_colon]] = line[position_of_colon+2:].replace('\n', "")

			line = file.readline()
		
		return file.readline()

	def read_ingredients(self, file, line):
		self.ingredients = []

		while line != "Steps\n":
			sub_list = []
			while line != '\n':
				sub_list.append(line.replace('\n',""))
				line = file.readline()
			
			(self.ingredients).append(sub_list)
			line = file.readline()

	def read_steps(self, file):
		self.steps, line = [], file.readline()
		while line[-1] == '\n':
			(self.steps).append(line)
			line = file.readline()
			if len(line) == 0:
				break # if a final line is added at the end of the recipe
			
		(self.steps).append(line)

		self.steps = [step.replace('\n',"") for step in self.steps]


	## Recipe tex String ##
	## ----------------- ##

	def get_recipe_tex_string(self, include_fig = True):
		tex_string = self.get_tex_title()

		if include_fig:
			tex_string += self.get_tex_image()

		tex_string += self.get_tex_preamble() + self.get_tex_info() + self.get_tex_ingredients() + self.get_tex_steps() + "\\newpage\n\n"
		return tex_string

	def get_tex_title(self):
		return f"\\section{{{self.title}}}\n" 


	def get_tex_image(self):
		string = "\\begin{figure}\n"
		string += "\\centering"
		string += rf"\includegraphics[width=10cm,height=10cm,keepaspectratio]{{{self.image_filepath()}}}" + '\n'
		string += "\end{figure}\n"
		return string

	def get_tex_preamble(self):
		string = self.preamble.replace('\n', '\\\\ \n')
		return f"\\emph{{{string}}}\\\\\\\\ \n"

	def get_tex_info(self):
		string = ""
		for key in self.info:
			if self.info[key] != None:
				string += f"\\textbf{{{key}}}: " + self.info[key] +'\n' # Use {{}} (double) in f string to output single {}
		return string

	def get_tex_ingredients(self):
		string = "\\subsection*{Ingredients}\n"
		for subset in self.ingredients:
			string += "\\begin{itemize}\n"
			for ingredient in subset:
				string += f"\\item {ingredient}\n"
			string += "\\end{itemize}\n\n"

		return self.replace_unicode_with_tex(string)


	def get_tex_steps(self):
		"\\subsection*{Steps}"
		string = "\\subsection*{Steps}\n\\begin{enumerate}\n"
		for step in self.steps:
			if len(step) != 0:
				string += f"\\item {step}\n"

		string += "\\end{enumerate}\n"
		return self.replace_unicode_with_tex(string)

	def replace_unicode_with_tex(self, string): # there are some characters that latex doesn't like this, replace them with things it does like
		to_replace = {"½" : r"$\frac{1}{4}$", 
		"¼" : r"$\frac{1}{4}$", "¾" : r"$\frac{3}{4}$", 
		"⅓" : r"$\frac{1}{3}$", "⅔" : r"$\frac{2}{3}$", 
		"⅛" : r"$\frac{1}{8}$",
		"%" : r"\%"}
		

		for key in to_replace:
			if key in string:
				string =string.replace(key, to_replace[key])
		
		return string