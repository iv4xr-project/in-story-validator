import sys
import json

if __name__ == "__main__":
	if len(sys.argv) == 3 and sys.argv[1] == "-f" and sys.argv[2][-5:] == ".json":
		print "correct"
		filename = sys.argv[2]
		file = open(filename)
		story_json = json.load(file)

		
	else:
		print "--- Unknown command or input file extension."
		print "--- Correct format:"
		print "python interactive-agent.py -f [twine-file.json]"
		