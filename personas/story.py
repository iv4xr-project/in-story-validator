class StoryPassage:

	def __init__(self, id, name, text, ending_point):
		self.id = id
		self.name = name 
		self.text = text
		self.isEndingPoint = ending_point
		self.links = []
		self.vars = {}

	def AddLink(self, id):
		self.links.append(id)