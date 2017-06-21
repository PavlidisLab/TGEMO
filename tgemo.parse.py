'''
# Category: Ontology OBO File Parser
# Case: TGEMO (Temporary Gemma Ontology)
# 1. Generates Main Adjacency List, Element Definition and Obsolete Element Collection for R
# Requires: Python 3.5.2
# Revision: 21 June 2017
'''

#
# Library Declarations
#
from collections import Counter
import re

#
# Setup Global Parameters
#
outFolder = 'Output/'
colMap = []
dictDef = dict()
dictObs = dict()

#
# Setup Custom Classes
#
class termObject:
	def __init__(self):
		self.ID = ''
		self.Name = ''
		self.Def = ''
		self.is_a = []
		self.is_obsolete = False

#
# GENERATE: Adjacency Lists and Definitions
#
tempPath = 'TGEMO.OBO'
elementCount = Counter()
processedCount = 0

# Parse Ontology
print('Parsing Ontology...')
with open(file = tempPath, mode = 'rt', encoding = 'utf-8', newline = '\n') as inFile:
	# Initialize Temporary TermObject
	hitFlag = False
	newTerm = termObject()
	
	for everyLine in inFile:
		everyLine = everyLine.strip('\n')
		
		# Sanity Check
		if everyLine.startswith('['):
			elementCount[everyLine] += 1
		if everyLine == '[Term]':
			hitFlag = True
			continue
		
		# Collection of Details
		if hitFlag:
			# ID Parser
			if everyLine.startswith('id:'):
				newTerm.ID = everyLine.partition('id: ')[2].replace(':', '_')
				continue
			
			# Name Parser
			if everyLine.startswith('name:'):
				newTerm.Name = everyLine.partition('name: ')[2]
				continue
			
			if everyLine.startswith('def:'):
				newTerm.Def = everyLine.partition('def: ')[2].strip('" []').replace('\\"', '"')
				continue
			
			# Parental Node Parser
			if everyLine.startswith('is_a:'):
				nodePartition = re.search('TGEMO:[0-9]+', everyLine).group(0).replace(':', '_')
				newTerm.is_a.append(nodePartition)
				continue
			
			# Is Obsolete Parser
			if everyLine == 'is_obsolete: true':
				newTerm.is_obsolete = True
				continue
		
		# Transfer Details to Appropriate Dictionary
		if everyLine == '':
			# Sanity Check
			if newTerm.ID == '':
				continue
			processedCount += 1
			
			if newTerm.is_obsolete:
				dictObs[newTerm.ID] = newTerm.Name
			else:
				if len(newTerm.is_a) != 0:
					for everyParent in newTerm.is_a:
						colMap.append('\t'.join([newTerm.ID, everyParent]))
				dictDef[newTerm.ID] = '\t'.join([newTerm.Name, newTerm.Def])
			
			# Reset TermObject
			hitFlag = False
			newTerm = termObject()
			
# Dump Maps to Files
# 1. Main Adjacency Map
print('Writing Files [1]...')
tempPath = outFolder + 'TGEMO.MAP'
with open(file = tempPath, mode = 'wt', newline = '\n') as outFile:
	for everyElement in colMap:
		print(everyElement, end = '\n', file = outFile)

# 2. Definition Map
print('Writing Files [2]...')
tempPath = outFolder + 'TGEMO.DEFINITION'
with open(file = tempPath, mode = 'wt', newline = '\n') as outFile:
	for everyElement in dictDef:
		print(everyElement, dictDef[everyElement], sep = '\t', end = '\n', file = outFile)

# 3. Obsolete Map
print('Writing Files [3]...')
tempPath = outFolder + 'TGEMO.OBSOLETE'
with open(file = tempPath, mode = 'wt', newline = '\n') as outFile:
	for everyElement in dictObs:
		print(everyElement, dictObs[everyElement], sep = '\t', end = '\n', file = outFile)

# Print Sanity Check Status
print('The following Elements were detected:')
for everyElement in elementCount:
	print(everyElement, ' = ', str(elementCount[everyElement]), ' hits.')
print('-----')
print('The following number of elements were successfully parsed: ', str(processedCount))
print('-----')
print('The following Dictionaries had X elements:')
print('dictDef: ', str(len(dictDef)))
print('dictObs: ', str(len(dictObs)))
print('----- END -----')