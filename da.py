#!/usr/bin/env python

# App Name: Da -> Digital Animator
# Author: Abe Haskins
# Date: 27 November, 2012
import pygame

class Animated(object):
	def __init__(self, maps=None, default=None, framerate=30, hidden=False):
		if maps is None:
			self.maps = {}
		else:
			self.maps = maps

		if not default is None:
			self.setAnimation(default)
		else:
			self.currentMapID = None

		self.assets = {}

		self.layer = 0
		self.framerate = 30
		self.frame = 0
		self.quenedMapID = None
		self.currentTransition = None
		self.children = {}
		self.setHidden(hidden)

	def requestAnimation(self, animation):
		if 'priority' in self.maps[self.currentMapID]:
			cPriority = self.maps[self.currentMapID]['priority']
		else:
			cPriority = 0

		if 'priority' in self.maps[animation]:
			rPriority = self.maps[animation]['priority']
		else:
			rPriority = 0

		if rPriority >= cPriority and not animation in [self.getAnimation(), self.getQuenedAnimation()]:
			self.setAnimation(animation)
			return True
		else:
			return False	

	def setAnimation(self, animation):
		currentMapID = self.currentMapID
		transition = '%s > %s' % (currentMapID, animation)

		if not self.getAnimation() is animation:
			self.frame = 0

			if transition in self.maps:
				self.quenedMapID = animation
				self.currentMapID = transition
				self.trigger('transition-set', {'transition': self.currentMapID})
			else:
				self.quenedMapID = None
				self.currentMapID = animation
				self.trigger('animation-set', {'animation': self.currentMapID})

	def setHidden(self, hidden):
		if hidden and not self.getAttribute('hidden'):
			self.trigger('hide')
		elif not hidden and self.getAttribute('hidden'):
			self.trigger('show')
		self.setAttribute('hidden', hidden)

	def getAnimation(self):
		return self.currentMapID

	def resetAnimation(self):
		self.frame = 0
		self.setHidden(False)

	def getQuenedAnimation(self):
		return self.quenedMapID

	def setAnimationMaps(self, maps):
		self.maps = maps

	def loadAsset(self, mapID, childID=None):
		if childID is None:
			cMap = self.maps[mapID]
		else:
			cMap = self.maps[mapID]['children'][childID]

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

		sprites = []
		sprites_flipped = []
		for r in range(0, rows):
			for c in range(0, columns):
				sprite = pygame.Surface(spriteSize, flags=pygame.SRCALPHA)
				sprite.blit(surface, (0, 0), [c*spriteWidth, r*spriteHeight, (c+1)*spriteWidth, (r+1)*spriteHeight])
				spriteSize = [
					spriteWidth, 
					spriteHeight
				]
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
		if mapID in self.maps:
			return self.maps[self.currentMapID]
		else:
			raise Exception('No animation map with name "%s"' % mapID)

	def setLayer(self, layer):
		self.layer = layer

	def getLayer(self):
		return self.layer

	def addChildMaps(self, xy, aChild, type=None):
		if not type:
			type = aChild.id
		self.children[type] = {'actor': aChild, 'x': xy[0], 'y': xy[1]}
		for mapID in self.maps:
			if mapID in aChild.maps:
				children = self.maps[mapID].get('children', {})
				children[mapID] = aChild.maps[mapID]
				children[mapID]['x'] = xy[0]
				children[mapID]['y'] = xy[1]
				self.maps[mapID]['children'] = children
				if mapID in self.assets:
					self.renderSprite(mapID)

	def renderSprite(self, mapID):
		for frame in range(0, len(self.assets[mapID])):
			surface 		= self.assets[mapID][frame]
			surfaceFlipped 	= self.assets[mapID + '_flipped'][frame]
			for childID in self.maps[mapID]['children']:
				childMap = self.maps[mapID]['children'][childID]
				self.loadAsset(mapID, childID) # This should be replaced with a reference to a standard resource bank
				alignment = 'none' if not 'align' in childMap else childMap['align']

				mapSizeDiff = [
					self.maps[mapID]['width']-childMap['width'], 
					self.maps[mapID]['height']-childMap['height']
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
		elif not self.currentMapID is None:
			cMap = self.getMap(self.currentMapID)
			cAssets, cAssetsFlipped = self.getAssets(self.currentMapID)
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
				self.trigger('animation-end', {'animation': self.currentMapID})
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