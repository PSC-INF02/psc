


class adapter:
	"""
	A class that takes an article analyzed by systran and pours elements from it into a workspace
	Use it with
	syntacticParser.parse(filename)
	"""

	def parse(self, filename, workspace):
		"""
		Parses a syntactic tree (systran format) and fills workspace given as argument with new information.
		"""
		f = open(filename, 'r')
		for line in f:
			# Each line is a sentence
			words = line.split(' ')
			for word in words:
				# Spaces serve as a delimiter for words in a sentence
				self.parseWord(word, workspace)

	def parseWord(self, word, workspace):
		"""
		Takes a cursory glance at whatever information is stored in the word (systran format) and adds it to the workspace
		"""
		wordStatus = word.split('-|-')

		# Getting lemma and grammatical class
		lemma = wordStatus.pop(1)
		nature = wordStatus.pop(1)

		'''
		 Now there are two possibilities : either the name is just a name and I can push it in the workspace as is, or it's an adjective / verb or such and I need to make it an attribute or an event and to gather some more information.
		'''
		
		if 'noun' in nature:
			#I'll read doc to see what I can get into a node
			pass

		else:

			# Getting features and relations to other words in the sentence (just in case)

			features=wordStatus.pop(1).split(';')
		
			'''
			For now I'll stay simple and just ignore everything until the relations in the sentence ; there might be some useful info in those features though.
			'''
			while not 'oldtag' in features.pop():
				pass

			if 'adj' in nature:
				#Seek some particular tag that should be useful, add node
				pass

			if 'verb' in nature:
				#Seek some particular tag that should be useful, add node
				pass
