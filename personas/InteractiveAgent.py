import sys
import json
import re
import math
from story import *
from TwineParser import *

def CalculateScore(variables, persona):
	res = 0
	for trait in persona.keys():
		res += persona[trait] * variables[trait]
	return res


if __name__ == "__main__":
	if len(sys.argv) == 3 and sys.argv[1] == "-f" and sys.argv[2][-5:] == ".json":
		print ">>> Loading story..."
		filename = sys.argv[2]
		file = open(filename)
		story_json = json.load(file)


		root = None
		story_passages = {}
		variables = {}

		# create story states and list of variables
		for passage in story_json["passages"]:
			pid = passage["pid"]
			name = passage["name"]
			text = passage["text"]
			ending_point = False
			if "tags" in passage and "ENDING-POINT" in passage["tags"]:
				ending_point = True
			story_passage = StoryPassage(pid, name, text, ending_point)
			if story_passages == {}:
				root = story_passage
			story_passages[name] = story_passage

			look_for_vars = re.findall("\$[a-zA-Z0-9]+", text)
			for found_var in look_for_vars:
				var_name = found_var[1:]
				variables[var_name] = 0
		
		print ">>> Story loaded."

		persona = {}
		persona_text = ">>> Setting Persona with variables "
		variables_text = ""
		i = 0
		for variable in variables:
			if i == 0:
				variables_text += "[" + variable
			else:
				variables_text += "," + variable
			i += 1
		variables_text += "]"
		print persona_text + variables_text + "..."
		for variable in variables:
			persona[variable] =input("--- Set weight of variable " + variable + ": ")
		print ">>> Persona set with the values " + str(persona.values()) + " for variables " + str(variables_text) + "."
		
		print ">>> Starting story..."
		state = root
		while not state.isEndingPoint:
			text = state.text
			new_variables = UpdateVariables(text, variables.copy())
			possible_links = GetPossibleLinks(text, new_variables)
			max_value = -1000
			chosen_link = None
			for link in possible_links:
				child = story_passages[link]
				score = CalculateScore(UpdateVariables(child.text, new_variables.copy()), persona)
				if score > max_value:
					max_value = score
					chosen_link = link
			state = story_passages[chosen_link]
			variables = new_variables
			print ">>> Agent chose [" + chosen_link + "] with variables " + variables_text + " as " + str(new_variables.values()) + "."

		print ">>> Reached story end."

		
	else:
		print "--- Unknown command or input file extension."
		print "--- Correct format:"
		print "python interactive-agent.py -f [twine-file.json]"
		