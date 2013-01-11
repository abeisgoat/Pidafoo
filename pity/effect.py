from bindable import *
from actor import *
from pidafoo.da import *
from collections import defaultdict
import copy

class Effects(Bindable):
	def __init__(self, effects=None, baseEffects=None):
		Bindable.__init__(self)
		self.id = id

		if not effects:
			self.effects = defaultdict(list)
		else:
			self.effects = effects

		if not baseEffects:
			self.baseEffects = {}
		else:
			self.baseEffects = baseEffects

	def play(self, effectID, place):
		effect = self.cloneEffect(effectID)

		# Figure out what type of "place" we were passed
		if isinstance(place, Actor):
			# If the place is an actor, we need to do a little more work to ensure 
			# that the actor and effect stay in sync
			point = [
				place.getAttribute('x')+(place.getAttribute('w')/2),
				place.getAttribute('y')+(place.getAttribute('h')/2)
			]

			# Define a hook to update the effect's location when the acotr moves
			def onPointChange(actor, data):
				d = 'w' if data['attribute'] is 'x' else 'h'
				actorCenter = data['valueCurrent']+(actor.getAttribute(d)/2)
				effectCenter = actorCenter-(effect.getAttribute(d)/2)
				effect.setAttribute(data['attribute'], effectCenter)

			# Then we will bind this hook to the place
			place.bind('change x', onPointChange)
			place.bind('change y', onPointChange)

		elif isinstance(place, list):
			# If the place is just a list then rename it to point and carry on
			point = place
		else:
			# If we don't know this type of place, blow up
			raise Exception('Failed to coerse place "%s" to point' % (str(place)))

		# Set the effect to be centered over the point
		effect.setAttribute('x', point[0]-(effect.getAttribute('w')/2))
		effect.setAttribute('y', point[1]-(effect.getAttribute('h')/2))

		# Once the effect has been animated and hidden, we trash it
		def onHidden(effect, data):
			effect.unbind(func=onHidden)
			self.removeEffect(effect)
			del effect

		# Bind the trashing code to the effect
		effect.bind('hide', onHidden)

		# Reset the animation so that if an effect is for some reason mid-play restart it
		effect.resetAnimation()
		return effect

	def getBaseEffect(self, effectID):
		return self.baseEffects[effectID]

	def cloneEffect(self, effectID):
		ce = self.baseEffects[effectID].clone(len(self.effects[effectID]))
		self.addEffect(ce)
		return ce

	def getEffects(self, baseEffectID):
		return self.effects[baseEffectID]

	def addEffect(self, effect):
		self.effects[effect.type].append(effect)

	def removeEffect(self, effect):
		self.effects[effect.type].remove(effect)

	def addBaseEffect(self, effect):
		# An effect is just an actor base who gets cloned a lot
		effect.setHidden(True)
		self.trigger('add effect')
		if not effect.id in self.baseEffects:
			self.baseEffects[effect.id] = effect
		else:
			raise Exception('Effect with id %s already present in existence' % effect.id)

	def removeBaseEffect(self, effect):
		self.trigger('remove effect')
		if effect.id in self.baseEffect:
			self.baseEffects.remove(effect.id)
		else:
			raise Exception('Effect with id %s not present in existence' % effect.id)

	def step(self):
		pass

class Effect(Actor):
	def clone(self, uid):
		c = copy.deepcopy(self)
		c.type = c.id
		c.id += str(uid)
		return c