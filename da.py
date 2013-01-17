#!/usr/bin/env python

# App Name: Da -> Digital Animator
# Author: Abe Haskins
# Date: 27 November, 2012
import pygame

class Animated(object):
	def __init__(self, maps=None, default=None, framerate=30, hidden=False):
		if maps is None:
			self.setAttribute('maps', {})
		else:
			self.setAttribute('maps', maps)

		if not default is None:
			self.setAnimation(default)
		else:
			self.setAttribute('currentMapID', None)

		self.assets = {}

		self.layer = 0
		self.framerate = 30
		self.frame = 0
		self.quenedMapID = None
		self.currentTransition = None
		self.children = {}
		self.setHidden(hidden)

	def requestAnimation(self, animation):
		maps = self.getAttribute('maps')
		currentMapID = self.getAttribute('currentMapID')
		if 'priority' in maps[currentMapID]:
			cPriority = maps[currentMapID]['priority']
		else:
			cPriority = 0

		if 'priority' in maps[animation]:
			rPriority = maps[animation]['priority']
		else:
			rPriority = 0

		if rPriority >= cPriority and not animation in [self.getAnimation(), self.getQuenedAnimation()]:
			self.setAnimation(animation)
			return True
		else:
			return False	

	def setAnimation(self, animation):
		currentMapID = self.getAttribute('currentMapID')
		transition = '%s > %s' % (currentMapID, animation)
		maps = self.getAttribute('maps')

		if not self.getAnimation() is animation:
			self.frame = 0

			if transition in maps:
				self.quenedMapID = animation
				self.setAttribute('currentMapID', transition)
				self.trigger('transition-set', {'transition': currentMapID})
			else:
				self.quenedMapID = None
				self.setAttribute('currentMapID', animation)
				self.trigger('animation-set', {'animation': currentMapID})

	def setHidden(self, hidden):
		if hidden and not self.getAttribute('hidden'):
			self.trigger('hide')
		elif not hidden and self.getAttribute('hidden'):
			self.trigger('show')
		self.setAttribute('hidden', hidden)

	def getAnimation(self):
		return self.getAttribute('currentMapID')

	def resetAnimation(self):
		self.frame = 0
		self.setHidden(False)

	def getQuenedAnimation(self):
		return self.quenedMapID

	def setAnimationMaps(self, maps):
		self.setAttribute('maps', maps)

	def loadAsset(self, mapID, childID=None):
		maps = self.getAttribute('maps')
		if childID is None:
			cMap = maps[mapID]
		else:
			cMap = maps[mapID]['children'][childID]

		spriteWidth = cMap['width']
		spriteHeight = cMap['height']

		spriteSize = [
			spriteWidth, 
			spriteHeight
		]

		if 'sprite' in cMap:
			surface =  pygame.image.load(cMap['sprite'])
		elif 'sprite_func' in cMap:
			surface = cMap['sprite_func'](cMap)
		else:
			raise Exception('Map is lacking either sprite or sprite_func')

		columns = surface.get_width()/cMap['width']
		rows = surface.get_height()/cMap['height']
		repeat = cMap['spriteRepeat'] if 'spriteRepeat' in cMap else False

		sprites = []
		sprites_flipped = []
		for r in range(0, rows):
			for c in range(0, columns):
				if not repeat:
					sprite = pygame.Surface(spriteSize, flags=pygame.SRCALPHA)
					sprite.blit(surface, (0, 0), [c*spriteWidth, r*spriteHeight, (c+1)*spriteWidth, (r+1)*spriteHeight])
				else:
					try:
						sprite = pygame.Surface([self.getAttribute('w'), self.getAttribute('h')], flags=pygame.SRCALPHA)
					except pygame.error:
						raise Exception("%s has invalid size of %ix%i" % (self.id, self.getAttribute('w'), self.getAttribute('h')))

					for xrp in range(0, self.getAttribute('w')/spriteWidth):
						for yrp in range(0, self.getAttribute('h')/spriteHeight):
							sprite.blit(surface, (spriteWidth*xrp, spriteHeight*yrp), [c*spriteWidth, r*spriteHeight, (c+1)*spriteWidth, (r+1)*spriteHeight])


				sprites.append(sprite)
				sprites_flipped.append(pygame.transform.flip(sprite, True, False))

		if cMap.get('reverse', False):
			sprites.reverse()

		store = True
		if 'sprite_store' in cMap:
			store = cMap['sprite_store']

		if store:
			if childID is None:
				self.assets[mapID] = sprites
				self.assets[mapID + '_flipped'] = sprites_flipped
			else:
				self.assets[mapID + '.' + childID] = sprites
				self.assets[mapID + '.' + childID + '_flipped'] = sprites_flipped
		return sprites, sprites_flipped

	def getAssets(self, mapID):
		if not mapID in self.assets:
			return self.loadAsset(mapID)
		else:
			return self.assets[mapID], self.assets[mapID + '_flipped']

	def getMap(self, mapID):
		maps = self.getAttribute('maps')
		if mapID in maps:
			return maps[self.getAttribute('currentMapID')]
		else:
			raise Exception('No animation map with name "%s" on actor of type %i' % (mapID, self.getAttribute('type')))

	def setLayer(self, layer):
		self.layer = layer

	def getLayer(self):
		return self.layer

	def addChildMaps(self, xy, aChild, type=None):
		if not type:
			type = aChild.id
		self.children[type] = {'actor': aChild, 'x': xy[0], 'y': xy[1]}
		maps = self.getAttribute('maps')
		for mapID in maps:
			childMaps = aChild.getAttribute('maps')
			if mapID in childMaps:
				children = maps[mapID].get('children', {})
				children[mapID] = childMaps[mapID]
				children[mapID]['x'] = xy[0]
				children[mapID]['y'] = xy[1]
				maps[mapID]['children'] = children
				if mapID in self.assets:
					self.renderSprite(mapID)

	def renderSprite(self, mapID):
		maps = self.getAttribute('maps')
		for frame in range(0, len(self.assets[mapID])):
			surface 		= self.assets[mapID][frame]
			surfaceFlipped 	= self.assets[mapID + '_flipped'][frame]
			for childID in maps[mapID]['children']:
				childMap = maps[mapID]['children'][childID]
				self.loadAsset(mapID, childID) # This should be replaced with a reference to a standard resource bank
				alignment = 'none' if not 'align' in childMap else childMap['align']

				mapSizeDiff = [
					maps[mapID]['width']-childMap['width'], 
					maps[mapID]['height']-childMap['height']
				]

				# Draw normal
				childSurface = self.assets['%s.%s' % (mapID, childID)]
				childFrame = frame % len(childSurface)
				if alignment is 'right':
					adjustmentX = mapSizeDiff[0]
					adjustmentY = mapSizeDiff[1]
				else:
					adjustmentX = 0
					adjustmentY = 0
				surface.blit(childSurface[childFrame], [childMap['x']+adjustmentX, childMap['y']+adjustmentY])

				# Draw flipped
				childSurface = self.assets['%s.%s' % (mapID, childID + '_flipped')]
				childFrame = frame % len(childSurface)
				if alignment is 'left':
					adjustmentX = mapSizeDiff[0]
					adjustmentY = mapSizeDiff[1]
				else:
					adjustmentX = 0
					adjustmentY = 0
				surfaceFlipped.blit(childSurface[childFrame], [-childMap['x']+adjustmentX, childMap['y']+adjustmentY])


	def getSprite(self):
		if self.getAttribute('hidden'):
			return pygame.Surface((0,0))
		elif not self.getAttribute('currentMapID') is None:
			cMap = self.getMap(self.getAttribute('currentMapID'))
			cAssets, cAssetsFlipped = self.getAssets(self.getAttribute('currentMapID'))
			width = self.getAttribute('w')
			height = self.getAttribute('h')
			flipped = self.getAttribute('flipped')

			if flipped:
				cAssets = cAssetsFlipped
				# Set the offset to make up for any differences in sprite width
				self.setAttribute('xoffset', cMap['width']-width)

			if 'speed' in cMap:
				speed = cMap['speed']
			else:
				speed = 1

			frame = int(self.frame/speed)
			if len(cAssets)-1 >= frame:
				sprite = cAssets[frame]
				self.frame += 1
				return sprite
			else:
				self.trigger('animation-end', {'animation': self.getAttribute('currentMapID')})
				if cMap['end'] == 'loop':
					self.frame = 0
				elif cMap['end'] == 'quened':
					self.setAnimation(self.quenedMapID)
				elif cMap['end'] == 'stay':
					self.frame -= 1
				elif cMap['end'] == 'hide':
					self.setHidden(True)
				elif cMap['end'][:5] == 'goto:':
					animation = cMap['end'].split(':')[1]
					self.setAnimation(animation)
				return self.getSprite()
		else:
			#print 'No animation set for actor "%s"' % (self.id)
			if self.hasAttribute('color'):
				color = self.getAttribute('color')
			else:
				color = 'red'

			if self.hasAttribute('w'):
				w = self.getAttribute('w')
			else:
				w = 32

			if self.hasAttribute('h'):
				h = self.getAttribute('h')
			else:
				h = 32

			assetKey = 'default'
			
			if not assetKey in self.assets:
				temporarySpriteSurface = pygame.Surface((w, h))

				pygame.draw.rect(
					temporarySpriteSurface, 
					pygame.Color(color), 
					pygame.Rect(0, 0, w, h)
				)
				self.assets[assetKey] = temporarySpriteSurface

			return self.assets[assetKey]