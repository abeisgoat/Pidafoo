from stateful import *
from bindable import *
from traits import *

from pidafoo.da import *

class Actor(Stateful, Traitful, Animated):
	def __init__(self, aID, attributes=None, actions=None, interactions=None, hidden=None):
		Stateful.__init__(self)

		if not attributes:
			self.attributes = {
				'x': 0,
				'y': 0,
				'w': 10,
				'h': 10,
				'forceX': 0,
				'forceY': 0,
				'flipped': False,
				'hidden': False
			}
		else:
			self.attributes = attributes

		if not interactions:
			self.setAttribute('interactions', {})
		else:
			self.setAttribute('interactions', interactions)

		if not actions:
			self.actions = {}
		else:
			self.actions = actions

		Traitful.__init__(self)
		Animated.__init__(self, hidden=hidden)
			
		self.id = aID 		# Unique ID of this actor
		self.dirty = False	# Has something changed that would require checking interactions?
		self.active = False # Is this actor active?
		self.fixed = False	# Is this fixed to a specific point? (Never used, I dont think)
		self.trash = False	# Set to true to retire this actor and release it's memory to the world
		self.is_child = False
		self.effectsQuene = []

		self.prioritizedInteractions = False
		self.parsedInteractions = {}

	def act(self, action):
		if action in self.actions:
			self.actions[action](self)

	def setActions(self, actions):
		self.actions = actions

	def addAction(self, actionID, action):
		self.actions[actionID] = action

	def removeAction(self, actionID):
		self.actions.remove(actionID)

	def interact(self, interaction, other, data=None):
		interactions = self.attributes['interactions']
		if interaction in interactions:
			self.trigger('interact %s' % (interaction))
			interactions[interaction](self, other, data)
		else:
			return False

	def setInteractions(self, interactions):
		self.setAttribute('interactions', interactions)

	def addInteraction(self, interaction, callback):
		interactions = self.getAttribute('interactions')
		if not interaction in interactions:
			interactions[interaction] = callback
		else:
			raise Exception('Interaction "%s" already exists in actor "%s"' % (interaction, self.id))

	def setAttribute(self, attribute, value):
		data = {
			'attribute': attribute,
			'valueOld': self.attributes.get(attribute, False),
			'valueCurrent': value,
		}
		self.attributes[attribute] = value
		self.trigger('change %s' % attribute, data)

	def hasAttribute(self, attribute):
		return attribute in self.attributes

	def getAttribute(self, attribute):
		return self.attributes.get(attribute, False)

	def increaseAttribute(self, attribute, increment, maxValue=None):
		value = self.attributes.get(attribute, 0) + increment

		if not maxValue is None:
			value = min(value, maxValue)

		self.setAttribute(attribute, value)

	def decreaseAttribute(self, attribute, decrement, minValue=None):
		value = self.attributes.get(attribute, 0) - decrement

		if not minValue is None:
			value = max(value, minValue)
			
		self.setAttribute(attribute, value)

	def pullAttribute(self, attribute, amount, ideal):
		value = self.attributes.get(attribute, 0)

		if value < ideal:
			self.increaseAttribute(attribute, amount)
		elif value > ideal:
			self.decreaseAttribute(attribute, amount)

	# This is kinda crummy, I might get rid of it
	def playEffect(self, effect):
		self.effectsQuene.append(effect)

	def emptyEffects(self):
		effects = self.effectsQuene
		self.effectsQuene = []
		return effects
	# End of Crummy

	def step(self):
		self.trigger('step')