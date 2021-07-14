import sys
import json
import re
import math
from story import *
from TwineParser import *

if __name__ == "__main__":
	if len(sys.argv) == 3 and sys.argv[1] == "-f" and sys.argv[2][-5:] == ".json":
		print "correct"
		filename = sys.argv[2]
		file = open(filename)
		story_json = json.load(file)


		story_passages = {}
		var_names = []

		# create story states and list of variables
		for passage in story_json["passages"]:
			pid = passage["pid"]
			name = passage["name"]
			text = passage["text"]
			story_passage = StoryPassage(pid, name, text)
			story_passages[pid] = story_passage

			look_for_vars = re.findall("\$[a-zA-Z0-9]+", text)
			for found_var in look_for_vars:
				var_name = found_var[1:]
				if not var_name in var_names:
					var_names.append(var_name)

		# update links references
		for passage in story_json["passages"]:
			parent_id = passage["pid"]
			parent = story_passages[parent_id]

			if "links" in passage:
				for link in passage["links"]:
					child_id = link["pid"]
					parent.AddLink(child_id)

			var_values = []
			for var_name in var_names:
				var_values.append(0)


			text = passage["text"]
			TwineCodeParser(text)


		
	else:
		print "--- Unknown command or input file extension."
		print "--- Correct format:"
		print "python interactive-agent.py -f [twine-file.json]"
		