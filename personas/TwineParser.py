import re


def TwineCodeParser(text):

	res = re.findall("\(if: .+\)\[\[.+\]\]", text)
	#res = re.findall("\[\[[ a-zA-Z0-9\->\|\?]+\]\]", text)
	print res