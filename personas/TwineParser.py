import re

SET_STATEMENT = "\(set: [^\(]+\)"
SET_REPLACE_MATCH = "\(set: \$(\w+) to ([\-0-9]+)\)"
SET_INCREMENT_MATCH = "\(set: \$(\w+) \+= ([\-0-9]+)\)"
SET_DECREMENT_MATCH = "\(set: \$(\w+) \-= ([\-0-9]+)\)"

COND_LINK_STATEMENT = "\(if: .+\) *\[\[.+\]\]"
COND_LINK_LEQ_MATCH = "\(if: \$(\w+) <= ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"
COND_LINK_L_MATCH = "\(if: \$(\w+) < ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"
COND_LINK_EQ_MATCH = "\(if: \$(\w+) is ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"
COND_LINK_GEQ_MATCH = "\(if: \$(\w+) >= ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"
COND_LINK_G_MATCH = "\(if: \$(\w+) > ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"
COND_LINK_G_AND_L_MATCH = "\(if: \$(\w+) > ([\-0-9]+) and < ([\-0-9]+)\) *\[\[(.+)\-\>(.+)\]\]"

LINK_STATEMENT = "\[\[.+\]\]"
RENAMED_LINK_BAR_MATCH = "\[\[(.+)\|(.+)\]\]"
RENAMED_LINK_ARR_MATCH = "\[\[(.+)->(.+)\]\]"
LINK_MATCH = "\[\[(.+)\]\]"

LINK_START = "\[\["
SET_START = "\(set:"
COND_START = "\(if:"



def UpdateVariables(text, variables):
	for set_statement in re.findall(SET_STATEMENT, text):
		if re.match(SET_REPLACE_MATCH, set_statement) != None:
			variable = re.match(SET_REPLACE_MATCH, set_statement).group(1)
			value = int(re.match(SET_REPLACE_MATCH, set_statement).group(2))
			variables[variable] = value
		elif re.match(SET_INCREMENT_MATCH, set_statement) != None:
			variable = re.match(SET_INCREMENT_MATCH, set_statement).group(1)
			value = int(re.match(SET_INCREMENT_MATCH, set_statement).group(2))
			variables[variable] += value
		elif re.match(SET_DECREMENT_MATCH, set_statement) != None:
			variable = re.match(SET_DECREMENT_MATCH, set_statement).group(1)
			value = int(re.match(SET_DECREMENT_MATCH, set_statement).group(2))
			variables[variable] -= value
		else:
			print "ERROR: Unknown set statement <" + set_statement + ">"
	return variables


def GetPossibleLinks(text, variables):
	possible_links = []
	#check conditional links first
	for cond_link in re.findall(COND_LINK_STATEMENT, text):
		if re.match(COND_LINK_LEQ_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_LEQ_MATCH, cond_link).group(1)
			value = int(re.match(COND_LINK_LEQ_MATCH, cond_link).group(2))
			if variables[variable] <= value:
				link = re.match(COND_LINK_LEQ_MATCH, cond_link).group(4)
				possible_links.append(link)
		elif re.match(COND_LINK_L_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_L_MATCH, cond_link).group(1)
			value = int(re.match(COND_LINK_L_MATCH, cond_link).group(2))
			if variables[variable] < value:
				link = re.match(COND_LINK_L_MATCH, cond_link).group(4)
				possible_links.append(link)
		elif re.match(COND_LINK_EQ_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_EQ_MATCH, cond_link).group(1)
			value = int(re.match(COND_LINK_EQ_MATCH, cond_link).group(2))
			if variables[variable] == value:
				link = re.match(COND_LINK_EQ_MATCH, cond_link).group(4)
				possible_links.append(link)
		elif re.match(COND_LINK_GEQ_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_GEQ_MATCH, cond_link).group(1)
			value = int(re.match(COND_LINK_GEQ_MATCH, cond_link).group(2))
			if variables[variable] >= value:
				link = re.match(COND_LINK_GEQ_MATCH, cond_link).group(4)
				possible_links.append(link)
		elif re.match(COND_LINK_G_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_G_MATCH, cond_link).group(1)
			value = int(re.match(COND_LINK_G_MATCH, cond_link).group(2))
			if variables[variable] > value:
				link = re.match(COND_LINK_G_MATCH, cond_link).group(4)
				possible_links.append(link)
		elif re.match(COND_LINK_G_AND_L_MATCH, cond_link) != None:
			variable = re.match(COND_LINK_G_AND_L_MATCH, cond_link).group(1)
			value1 = int(re.match(COND_LINK_G_AND_L_MATCH, cond_link).group(2))
			value2 = int(re.match(COND_LINK_G_AND_L_MATCH, cond_link).group(3))
			if variables[variable] > value1 and variables[variable] < value2:
				link = re.match(COND_LINK_G_AND_L_MATCH, cond_link).group(5)
				possible_links.append(link)
		else:
			print "ERROR: Unknown conditional link statement <" + cond_link + ">"
		text = text.replace(cond_link, "")

	#check links without conditions
	for cond_link in re.findall(LINK_STATEMENT, text):
		if re.match(RENAMED_LINK_BAR_MATCH, cond_link) != None:
			link = re.match(RENAMED_LINK_BAR_MATCH, cond_link).group(2)
			possible_links.append(link)
		elif re.match(RENAMED_LINK_ARR_MATCH, cond_link) != None:
			link = re.match(RENAMED_LINK_ARR_MATCH, cond_link).group(2)
			possible_links.append(link)
		elif re.match(LINK_MATCH, cond_link) != None:
			link = re.match(LINK_MATCH, cond_link).group(1)
			possible_links.append(link)
		else:
			print "ERROR: Unknown link statement <" + cond_link + ">"
	
	return possible_links
		
	

