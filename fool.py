#!/usr/bin/env python

# App Name: Fool -> I like drawing stuff onto the windows!
# Author: Abe Haskins
# Date: 27 November, 2012
from pygame import *
from collections import defaultdict
from pidafoo.pity import interactions

class Graphics(object):
	def __init__(self, screenSize, centerActor='Player'):
		self.screenSize = screenSize
		self.centerActor = centerActor
		self.viewport = [-64, -64, self.screenSize[0]+128, self.screenSize[1]+128]
		self.tightViewport = [0, 0, self.screenSize[0], self.screenSize[1]]

	def render(self, game, data):
		# Clear the screen
		draw.rect(game.screen, Color('#cccccc'), Rect(0, 0, self.screenSize[0], self.screenSize[1]))

		# Load up our center actor
		ca = game.existence.getActor(self.centerActor)

		# Sort out how much we need to shift stuff to keep the player centered
		offset = [
			ca.getAttribute('x')-((self.screenSize[0]-ca.getAttribute('w'))/2), 
			ca.getAttribute('y')-((self.screenSize[1]-ca.getAttribute('h'))/2)
		]

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

		for actorID in game.existence.map.getActors():
			actor = game.existence.map.getActor(actorID)
			layers[actor.layer].append(actor)


		# Loop through all our actors
		for layer in layers:
			for actor in layers[layer]:
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

				if interactions.over(actorRect, viewport) or actor.fixed:
					sprite = actor.getSprite()
					actor.active = True
					actorRect[0] -= actor.getAttribute('xoffset')
					actorRect[1] -= actor.getAttribute('yoffset')
					rect = Rect(*actorRect)
					game.screen.blit(sprite, rect)
				else:
					actor.active = False

		for overlayID in game.existence.overlays.getOverlays():
			overlay = game.existence.overlays.getOverlay(overlayID)
			rect = Rect(overlay.getAttribute('x'), overlay.getAttribute('y'), overlay.getAttribute('w'), overlay.getAttribute('h'))
			game.screen.blit(overlay.getSprite(), rect)