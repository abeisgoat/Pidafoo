from actor import *
from grid import *
from utils import *
from traits import *
import sys, os

class Map(object):
	def __init__(self, gridset=None, blocks=None):
		if gridset:
			self.loadGridset(gridset)
		else:
			self.gridset = {}
		self.actors = {}
		self.actorsFixed = {}

		self.blockSize = 32
		if blocks:
			self.blocks = blocks
		else:
			self.blocks = {}

	def loadGridset(self, gridset):
		for layer in gridset:
			if not isinstance(gridset[layer], Grid):
				grid = Grid(gridset[layer])
			else:
				grid = gridset[layer]
			# Gross hack to make map draw right
			grid.appendRow([0 for i in range(0, len(grid.getArray()[0]))])
			self.actors.update(self.gridToActors(grid, layer=layer))

		print 'Map has %i actors' % len(self.actors)
		
	def gridToActors(self, grid, layer=0, prefix='Block', actorType=None):
		actors = {}
		if not actorType:
			actorType = Actor
		for y, row in enumerate( grid.getArray() ):
			for x,block in enumerate( row ):
				aid = prefix + '-%ix%ix%i' % (x, y, int(layer))

				if block in self.actors:
					self.actors.pop(block)

				if block:
					aBlock = actorType(aid)

					w = 0
					
					for w in range(0, len(row)-x):
						if grid.get(x+w, y) is block:
							grid.set(x+w, y, 0)
							w += 1
						elif not w is 0:
							break

					if not w:
						w = 1

					h = 0
					for h in range(0, len(grid.getArray())-y):
						if all(sb is block for sb in grid.getArray()[y+h][x:x+w]):
							ps = range(x, x+w)
							for p in ps:
								grid.set(p, y+h, 0)
						elif not h is 0:
							break

					if not h:
						h = 1

					aBlock.setAttribute('w', w*self.blockSize)
					aBlock.setAttribute('h', h*self.blockSize)
					aBlock.setAttribute('x', x*self.blockSize)
					aBlock.setAttribute('y', y*self.blockSize)
					aBlock.setAttribute('solid', self.blocks[block].solid)
					aBlock.setAttribute('color', self.blocks[block].color)
					aBlock.setAttribute('group', self.blocks[block].group)
					aBlock.setLayer(int(layer))

					interactions 	= self.blocks[block].interactions
					bindings 		= self.blocks[block].bindings
					traits 			= self.blocks[block].traits
					actions 		= self.blocks[block].actions
					reactions 		= self.blocks[block].reactions
					attributes 		= self.blocks[block].attributes

					if hasattr(self.blocks[block], 'animationMaps'):
						animationMaps = self.blocks[block].animationMaps
						aBlock.setAnimationMaps(animationMaps)
						aBlock.setAnimation('default')

					for interaction in interactions:
						aBlock.addInteraction(interaction, interactions[interaction])

					for binding in bindings:
						aBlock.bind(binding, bindings[binding])

					for trait in traits:
						aBlock.addStat(trait, traits[trait])

					for reaction in reactions:
						react = ReactionEvent(reaction, reactions[reaction])
						aBlock.addReaction(react, reaction)

					for attribute in attributes:
						aBlock.setAttribute(attribute, attributes[attribute])

					aBlock.setActions(actions)

					actors[aid] = aBlock
		return actors

	def getActors(self):
		return self.actors

	def removeActor(self, actor):
		self.actors.pop(actor.id)

	def getActor(self, actorID):
		return self.actors[actorID]

	def getActorFixed(self, fixed, actorID):
		return self.actorsFixed[fixed][actorID]