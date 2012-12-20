from bindable import *
from interactions import *
from utils import *
from effect import *
from overlay import *
from maps import *

def interactionKey(i):
	if i[0] is '!':
		return 0
	else:
		return 1

class Existence(Bindable):
	'''
	Events:
	- add actor (actor added to game)
	- remove actor (actor removed from game)
	'''
	def __init__(self, actors=None, effects=None, overlays=None, gridset=None):
		Bindable.__init__(self)

		if not actors:
			self.actors = {}
		else:
			self.actors = actors

		self.effects = Effects(effects)
		self.overlays = Overlays(overlays)
		self.map = Map(gridset)
		self.paused = False
		self.__selectors_cache__ = {}

	def loadActors(self):
		for actorID in self.map.getActors():
			actor = self.map.getActor(actorID)
			if not self.hasActor(actorID):
				self.addActor(actor)
		print 'Loaded actors total (%i)' % len(self.actors)

		self.__selectors_cache__ = {}

	def step(self):
		trashcan = []

		if self.paused:
			return
			
		for actor in self.actors:
			a = self.getActor(actor)

			if not a.trash:
				if not a.prioritizedInteractions:
					a.prioritizedInteractions = sorted(a.interactions, key=interactionKey)

				for interaction in a.prioritizedInteractions:
					ia = utils.parseInteraction(interaction)

					if hasattr(interactions, ia['action']):
						ia_check = interactions.get(ia['action'])

						if 'other' in ia:
							if ia['other'] != '*':
								others = [ia['other']]
							else:
								others = self.actors.keys()

						elif 'selectors' in ia:
							for selector in ia['selectors']:
								value = ia['selectors'][selector]
								selectorKey = "%s:%s" % (selector, value)
								if selectorKey in self.__selectors_cache__:
									#print 'loading selector %s' % selectorKey 
									others = self.__selectors_cache__[selectorKey]
									#print others
								else:
									others = []
									for actor in self.actors:
										a = self.getActor(actor)
										if a.getAttribute(selector) == value:
											others.append(actor)
									self.__selectors_cache__[selectorKey] = others

						for other in others:
							other = self.getActor(other)
							if not other is a:
								if (other.dirty or a.dirty) and (other.active and a.active):
									if ia_check( a, other ):
										a.interact(interaction, other)
										interactionResponse = '%s from %s' % (ia['action'], a.id)
										other.interact(interactionResponse, a)
			else:
				trashcan.append(a)

		for a in trashcan:
			self.removeActor(a)
			self.map.removeActor(a)

		for actor in self.actors:
			a = self.getActor(actor)
			a.step()
		self.effects.step()

	def interactOn(self, actor, action, relative_point):
		point = [actor.getAttribute('x')+relative_point[0], actor.getAttribute('y')+relative_point[1], actor.getAttribute('w'), actor.getAttribute('h')]
		others = []
		for actorID in self.actors:
			other = self.getActor(actorID)
			if not other is actor:
				over = interactions.over(other, point)
				if over:
					interaction 				= '%s %s' % (action, other.id)
					interactionGroup  			= '%s group:%s'  % (action, other.getAttribute('group'))
					interactionResponse 		= '%s from %s' % (action, actor.id) 
					interactionResponseGroup 	= '%s from group:%s' % (action, actor.getAttribute('group'))
					actor.interact(interaction, other)
					actor.interact(interactionGroup, other)
					other.interact(interactionResponse, actor)
					other.interact(interactionResponseGroup, actor)
					others.append(other)
		return others

	def addActor(self, actor):
		self.trigger('add actor')
		if not actor.id in self.actors:
			self.actors[actor.id] = actor
		else:
			raise Exception('Actor with id %s already present in existence' % actor.id)

	def removeActor(self, actor):
		self.trigger('remove actor')
		if actor.id in self.actors:
			self.actors.pop(actor.id)
		else:
			raise Exception('Actor with id %s not resent in existence' % actor.id)

	def getActor(self, actorID):
		try:
			return self.actors[actorID]
		except KeyError:
			raise Exception('Invalid actor with ID "%s"' % actorID)

	def hasActor(self, actorID):
		return actorID in self.actors

	def setBlocks(self, blocks):
		self.blocks = blocks
		self.map.blocks = blocks