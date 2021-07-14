class StoryPassage:

	def __init__(self, id, name, text):
		self.id = id
		self.name = name 
		self.text = text
		self.links = []
		self.vars = []

	def AddLink(self, id):
		self.links.append(id)