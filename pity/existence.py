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
		self.dirty = False
		self.__selectors_cache__ = {}

	def loadActors(self):
		self.dirty = True
		print 'Loading Actors'
		for actorID,actor in self.map.getExpiredActors().items():
			if self.hasActor(actorID) and not actor.getAttribute('persistant'):
				actor.trigger('trashed')
				self.removeActor(actor)

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
					a.prioritizedInteractions = sorted(a.getAttribute('interactions'), key=interactionKey)

				for interaction in a.prioritizedInteractions:
					if not interaction in a.parsedInteractions:
						ia = utils.parseInteraction(interaction)
						a.parsedInteractions[interaction] = ia
					else:
						ia = a.parsedInteractions[interaction]

					if hasattr(interactions, ia['action']):
						ia_check = interactions.get(ia['action'])

						if 'other' in ia:
							if ia['other'] != '*':
								others = [self.actors[ia['other']]]
							else:
								others = self.actors.values()

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
											others.append(a)
									self.__selectors_cache__[selectorKey] = others

						for other in others:
							if (other.dirty or a.dirty) and (other.active and a.active):
								if not other is a:
									if ia_check( a, other ):
										a.interact(interaction, other, {'existence': self})
										interactionResponse = '%s from %s' % (ia['action'], a.id)
										other.interact(interactionResponse, a, {'existence': self})
			else:
				trashcan.append(a)

		for a in trashcan:
			self.removeActor(a)
			self.map.removeActor(a)
			a.trigger('trashed')

		for actor in self.actors:
			a = self.getActor(actor)
			a.step()
			for effect in a.emptyEffects():
				self.effects.play(effect, a)

		self.effects.step()

	def interactOn(self, actor, action, relative_point):
		point = [actor.getAttribute('x')+relative_point[0], actor.getAttribute('y')+relative_point[1], 1, 1]
		others = []
		for actorID in self.actors:
			other = self.getActor(actorID)
			if not other is actor:
				over = interactions.over(other, actor, bOffset=relative_point)
				if over:
					interaction 				= '%s %s' % (action, other.id)
					interactionGroup  			= '%s group:%s'  % (action, other.attributes['group'])
					interactionResponse 		= '%s from %s' % (action, actor.id) 
					interactionResponseGroup 	= '%s from group:%s' % (action, actor.attributes['group'])
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
			self.actors.pop(actor.id).id
		else:
			raise Exception('Actor with id %s not present in existence' % actor.id)

	def getActor(self, actorID):
		try:
			return self.actors[actorID]
		except KeyError:
			raise Exception('Invalid actor with ID "%s"' % actorID)

	def getActorsByGroup(self, actorGroup):
		actors = []
		for actorID in self.actors:
			if self.actors[actorID].getAttribute('group') == actorGroup:
				actors.append(self.actors[actorID])
		return actors

	def hasActor(self, actorID):
		return actorID in self.actors

	def setBlocks(self, blocks):
		self.blocks = blocks
		self.map.blocks = blocks