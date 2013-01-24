from actor import *
from grid import *
from utils import *
from traits import *
import sys, os

class Map(object):
	def __init__(self, gridset=None, blocks=None):

		self.chunkRangeActors = {}
		self.expiredChunkRangeActors = {}
		self.nonExpirableActors = {}
		self.allActors = {}
		self.consistentActors = {}
		self.persistantActors = {}
		self.blockSize = 32
		self.chunkSize = 11
		self.activeChunkX = -1
		self.activeChunkY = -1
		self.chunkRange = 1
		self.chunks = None
		self.baseOffset = []

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
		self.chunks = {}
		for layer in gridset:
			if not isinstance(gridset[layer], Grid):
				grid = Grid(gridset[layer])
			else:
				grid = gridset[layer]

			self.chunks[layer] = grid.split([self.chunkSize, self.chunkSize])

			print "Broke map into %s chunks" % len(self.chunks[layer]), 'of size', self.chunkSize

			for r, chunksRow in enumerate(self.chunks[layer]):
				row = self.actors.get(r, {})
				for ch, chunk in enumerate(chunksRow):
					actors = row.get(ch, {})
					# Gross hack to make map draw right
					chunk.appendRow([0 for i in range(0, len(chunk.getArray()[0]))])
					chunkActors = self.gridToActors(chunk.copy(), layer=layer, prefix='Block-Chunk%ix%i' % (r, ch), offset=[ch*chunk.height*self.blockSize, r*chunk.width*self.blockSize])
					actors.update(chunkActors)
					self.allActors.update(chunkActors)
					row[ch] = actors
				self.actors[r] = row

		print 'Map has %i actors' % len(self.actors)
		
	def gridToActors(self, grid, layer=0, prefix='Block', actorType=None, offset=None, gridOffset=None):
		if not offset:
			offset = [0, 0]
		if not gridOffset:
			gridOffset = [0, 0]
		actors = {}
		if not actorType:
			actorType = Actor
		for by, row in enumerate( grid.getArray() ):
			for bx,block in enumerate( row ):
				y = by + gridOffset[1]
				x = bx + gridOffset[0]

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

					interactions 	= self.blocks[block].interactions
					bindings 		= self.blocks[block].bindings
					stats			= self.blocks[block].stats
					actions 		= self.blocks[block].actions
					reactions 		= self.blocks[block].reactions
					attributes 		= self.blocks[block].attributes
					generator 		= getattr(self.blocks[block], 'generator', None)

					if aBlock.id in self.consistentActors:
						aBlock.attributes = self.consistentActors[aBlock.id]
					else:
						aBlock.setAttribute('w', w*self.blockSize)
						aBlock.setAttribute('h', h*self.blockSize)
						aBlock.setAttribute('x', (x*self.blockSize)+ offset[0])
						aBlock.setAttribute('y', (y*self.blockSize)+ offset[1])

						aBlock.setAttribute('solid', self.blocks[block].solid)
						aBlock.setAttribute('color', self.blocks[block].color)
						aBlock.setAttribute('group', self.blocks[block].group)
						aBlock.setAttribute('type', block)
						aBlock.setAttribute('consistent', self.blocks[block].consistent)

						for attribute in attributes:
							aBlock.setAttribute(attribute, attributes[attribute])

						for stat in stats:
							s = stats[stat]
							value = s['value'] if 'value' in s else 0
							mi = s['min'] if 'min' in s else None
							ma = s['max'] if 'max' in s else None
							aBlock.addStat(stat, value=value, min=mi, max=ma)

						if hasattr(self.blocks[block], 'animationMaps'):
							animationMaps = self.blocks[block].animationMaps
							aBlock.setAnimationMaps(animationMaps)
							
							currentMapID = aBlock.attributes['currentMapID']
							if currentMapID:
								print 'setting cmap', currentMapID
								aBlock.setAnimation(currentMapID)
							else:
								aBlock.setAnimation('default')

						for interaction in interactions:
							aBlock.addInteraction(interaction, interactions[interaction])


					persistant = False
					if aBlock.attributes.get('persistant', False):
						pl = self.persistantActors.get(str(layer), {})
						persistant = aBlock.id in pl
						pl[aBlock.id] = aBlock
						self.persistantActors[str(layer)] = pl

					if not aBlock.attributes.get('expirable', False):
						self.nonExpirableActors[aBlock.id] = aBlock

					l = aBlock.attributes.get('layer', False)
					if l:
						aBlock.setLayer(l)
					else:
						aBlock.setLayer(int(layer))

					aBlock.dirty = True

					aID = aBlock.attributes.get('id', False)
					if aID:
						print 'setting aID', aid
						aBlock.id = aID

					for binding in bindings:
						b = bindings[binding]
						if isinstance(b, list):
							for bb in b:
								aBlock.bind(binding, bb)
						else:
							aBlock.bind(binding, b)

					for reaction in reactions:
						react = ReactionEvent(reaction, reactions[reaction])
						aBlock.addReaction(react, reaction)

					for attribute in attributes:
						aBlock.setAttribute(attribute, attributes[attribute])

					aBlock.setActions(actions)

					if not persistant:
						actors[aBlock.id] = aBlock

					if aBlock.getAttribute('consistent'):
						if not aBlock.id in self.consistentActors and generator:
							aBlock = generator(aBlock)
						self.consistentActors[aBlock.id] = aBlock.attributes
					else:
						if generator:
							aBlock = generator(aBlock)

		return actors

	def getActors(self):
		return self.chunkRangeActors

	def setActiveChunk(self, x=0, y=0):
		self.activeChunkX = x
		self.activeChunkY = y
		self.updateChunkRangeActors()

	def updateChunkRangeActors(self):
		print 'Expiring chunk range actors'
		self.expiredChunkRangeActors = dict(**self.chunkRangeActors)
		for actor in self.expiredChunkRangeActors:
			a = self.expiredChunkRangeActors[actor]
			if a.id in self.consistentActors:
				self.consistentActors[a.id] = a.attributes

		print 'Preparing new map segment'
		chunkRange = len(range(self.activeChunkX-self.chunkRange, self.activeChunkX+self.chunkRange+1))
		segment = Grid(width=(chunkRange*self.chunkSize)+11, height=(chunkRange*self.chunkSize)+12)
		self.chunkRangeActors = {}

		print 'Setting up segment'
		baseX = self.activeChunkX
		baseY = self.activeChunkY
		for layer in range(0, len(self.chunks)):
			layer = str(layer)
			x_range = range(self.activeChunkX-self.chunkRange, self.activeChunkX+self.chunkRange+1)
			y_range = range(self.activeChunkY-self.chunkRange, self.activeChunkY+self.chunkRange+1)
			x_diff = -(self.activeChunkX-self.chunkRange)
			y_diff = -(self.activeChunkY-self.chunkRange)
			xplus = 0
			yplus = 0
			print x_range, y_range, x_diff, y_diff
			for x in x_range:
				for y in y_range:
					if x >= 0 and y >= 0 and x < len(self.actors[0].keys()) and y < len(self.actors):
						grid = self.chunks[layer][y][x]
						#segment.paint(grid, (x+x_diff)*self.chunkSize, (y+y_diff)*self.chunkSize)
						if x-baseX < 0 and xplus == 0: xplus = -(x-baseX)
						if y-baseY < 0 and yplus == 0: yplus = -(y-baseY)
						print 'Painting chunk at %ix%i' % (x-baseX+xplus, y-baseY+yplus)
						segment.paint(grid, (x-baseX+xplus)*self.chunkSize, (y-baseY+yplus)*self.chunkSize)

			print 'Generating new actors for layer %s' % layer
			if layer is '0': print segment
			baseOffset = [((baseX-xplus)*self.chunkSize*self.blockSize), ((baseY-yplus)*self.chunkSize*self.blockSize)]
			actors = self.gridToActors(segment, layer=int(layer), offset=baseOffset)#, gridOffset=[-x_diff, -y_diff])
			self.chunkRangeActors.update(actors)
		return True

	def getAllActors(self):
		return self.allActors

	def removeActor(self, actor, chunkX=None, chunkY=None):
		if not chunkX: chunkX = self.activeChunkX
		if not chunkY: chunkY = self.activeChunkY
		# This errors out when the player is on the edge of a chunk passing onto an item pickup
		# Does it still? Idk
		self.chunkRangeActors.pop(actor.id)
		#self.actors[chunkY][chunkX].pop(actor.id)

	def getActor(self, actorID, chunkX=None, chunkY=None):
		if not chunkX: chunkX = self.activeChunkX
		if not chunkY: chunkY = self.activeChunkY
		return self.chunkRangeActors[actorID]

	def getFixedActors(self, fixed, actorID):
		return self.actorsFixed[fixed][actorID]

	def getExpiredActors(self):
		return self.expiredChunkRangeActors