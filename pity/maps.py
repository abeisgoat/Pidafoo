from actor import *
from grid import *
from utils import *
from traits import *
import sys, os

class Map(object):
	def __init__(self, gridset=None, blocks=None):

		self.chunkRangeActors = {}
		self.expiredChunkRangeActors = {}
		self.allActors = {}
		self.blockSize = 32
		self.chunkSize = 11
		self.activeChunkX = -1
		self.activeChunkY = -1
		self.chunkRange = 1

		if gridset:
			self.loadGridset(gridset)
		else:
			self.gridset = {}
		self.actors = {}
		self.actorsFixed = {}

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

			chunks = grid.split([self.chunkSize, self.chunkSize])

			print "Broke map into %s chunks" % len(chunks)

			for r, chunksRow in enumerate(chunks):
				row = self.actors.get(r, {})
				for ch,chunk in enumerate(chunksRow):
					actors = row.get(ch, {})
					# Gross hack to make map draw right
					chunk.appendRow([0 for i in range(0, len(grid.getArray()[0]))])
					chunkActors = self.gridToActors(chunk, layer=layer, prefix='Block-Chunk%ix%i' % (r, ch), offset=[ch*chunk.height*self.blockSize, r*chunk.width*self.blockSize])
					actors.update(chunkActors)
					self.allActors.update(chunkActors)
					row[ch] = actors
				self.actors[r] = row

		print 'Map has %i actors' % len(self.actors)
		
	def gridToActors(self, grid, layer=0, prefix='Block', actorType=None, offset=None):
		if not offset:
			offset = [0, 0]
		actors = {}
		if not actorType:
			actorType = Actor
		for y, row in enumerate( grid.getArray() ):
			for x,block in enumerate( row ):
				aid = prefix + '-%ix%ix%i' % (x, y, int(layer))

				#if block in self.actors:
				#	self.actors.pop(block)

				if block > 0:
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
					aBlock.setAttribute('x', x*self.blockSize+ offset[0])
					aBlock.setAttribute('y', y*self.blockSize+ offset[1])

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
		return self.chunkRangeActors

	def setActiveChunk(self, x=0, y=0):
		self.activeChunkX = x
		self.activeChunkY = y
		self.updateChunkRangeActors()

	def updateChunkRangeActors(self):
		self.expiredChunkRangeActors = dict(**self.chunkRangeActors)
		actors = {}
		rangeChunks = 0
		for x in range(self.activeChunkX-self.chunkRange, self.activeChunkX+self.chunkRange+1):
			for y in range(self.activeChunkY-self.chunkRange, self.activeChunkY+self.chunkRange+1):
				if x >= 0 and y >= 0 and x < len(self.actors[0].keys()) and y < len(self.actors):
					rangeChunks += 1
					actors.update(self.actors[y][x])
		self.chunkRangeActors = actors

	def getAllActors(self):
		return self.allActors

	def removeActor(self, actor, chunkX=None, chunkY=None):
		if not chunkX: chunkX = self.activeChunkX
		if not chunkY: chunkY = self.activeChunkY
		# This errors out when the player is on the edge of a chunk passing onto an item pickup
		self.chunkRangeActors.pop(actor.id)
		self.actors[chunkY][chunkX].pop(actor.id)

	def getActor(self, actorID, chunkX=None, chunkY=None):
		if not chunkX: chunkX = self.activeChunkX
		if not chunkY: chunkY = self.activeChunkY
		return self.chunkRangeActors[actorID]

	def getFixedActors(self, fixed, actorID):
		return self.actorsFixed[fixed][actorID]

	def getExpiredActors(self):
		return self.expiredChunkRangeActors