#!/usr/bin/env python

# App Name: Fool -> I like drawing stuff onto the windows!
# Author: Abe Haskins
# Date: 27 November, 2012
import pygame
from pygame import *
from collections import defaultdict
from pidafoo.pity import interactions

gridLines = True

class Graphics(object):
	def __init__(self, screenSize, centerActor='Player'):
		self.screenSize = screenSize
		self.centerActor = centerActor
		self.viewport = [-64, -64, self.screenSize[0]+128, self.screenSize[1]+128]
		self.borderViewport = [-32, -32, self.screenSize[0]+64, self.screenSize[1]+64]
		self.tightViewport = [0, 0, self.screenSize[0], self.screenSize[1]]
		self.static = pygame.Surface((11*3*32, 11*3*32))

	def sortLayers(self, game):
		# Create a layers dict that defaults to a list (for the actors on that layer)
		layers = defaultdict(list)

		# Loop through all are known actors and put them in the correct layers
		for actorID in game.existence.actors:
			actor = game.existence.getActor(actorID)
			layers[actor.layer].append(actor)

		for baseEffectID in game.existence.effects.baseEffects:
			effects = game.existence.effects.getEffects(baseEffectID)
			for effect in effects:
				layers[effect.layer].append(effect)

		return layers

	def draw(self, game, sprite, rect):
		game.screen.blit(sprite, rect)

	def isActive(self, actorRect, viewport):
		return interactions.above(actorRect, viewport)

	def getSprite(self, actor):
		return actor.getSprite()

	def render(self, game, data):
		# Clear the screen
		game.screen.fill(pygame.Color('#cccccc'))

		# Load up our center actor
		ca = game.existence.getActor(self.centerActor)

		# Sort out how much we need to shift stuff to keep the player centered
		offset = [
			ca.getAttribute('x')-((self.screenSize[0]-ca.getAttribute('w'))/2), 
			ca.getAttribute('y')-((self.screenSize[1]-ca.getAttribute('h'))/2)
		]

		layers = self.sortLayers(game)

		actors = 0
		activeCount = 0

		# Loop through all our actors
		for layer in layers:
			for actor in layers[layer]:
				actors += 1
				# Draw the actors with the offset determined earlier
				actorRect = [
					actor.getAttribute('x')-offset[0], 
					actor.getAttribute('y')-offset[1], 
					actor.getAttribute('w'), 
					actor.getAttribute('h')
				]

				group = actor.getAttribute('group')
				if group == 'npcs':
					# We use the tight viewport for moving peices
					# so that the walls dont despawn while they're 
					# still using them
					viewport = self.tightViewport
				else:
					viewport = self.viewport

				if self.isActive(actorRect, viewport) or actor.fixed:
					activeCount += 1
					sprite = self.getSprite(actor)
					actor.active = True
					actorRect[0] -= actor.getAttribute('xoffset')
					actorRect[1] -= actor.getAttribute('yoffset')
					rect = Rect(*actorRect)
					self.draw(game, sprite, rect)
				else:
					actor.active = False

		game.debug_active = (str(activeCount) + '/' + str(actors))

		for overlayID in game.existence.overlays.getOverlays():
			overlay = game.existence.overlays.getOverlay(overlayID)
			rect = Rect(overlay.getAttribute('x'), overlay.getAttribute('y'), overlay.getAttribute('w'), overlay.getAttribute('h'))
			game.screen.blit(overlay.getSprite(), rect)