from interactions import *
from utils import *

class Physics(object):
	def applyForces(self, actor, data):
		if actor.active:
		#	print 'Applying forces for', actor.id
			xChange = actor.attributes['forceX']
			yChange = actor.attributes['forceY']
			actor.increaseAttribute('x', xChange)
			actor.increaseAttribute('y', yChange)

	def adjustForces(self, actor, other, data):
		is_over = interactions.over(actor, other, aOffset=[actor.attributes['forceX'], actor.attributes['forceY']])
		if other.getAttribute('solid'):
			if is_over:
				io, diff = interactions.over(actor, other, return_difference=True)

				ctX = utils.closerTo([diff[0], actor.attributes['forceX']], 0)
				ctY = utils.closerTo([diff[1], actor.attributes['forceY']], 0)

				if ctX != actor.attributes['forceX']:
					actor.setAttribute('forceX', ctX)

				if ctY != actor.attributes['forceY']:
					actor.setAttribute('forceY', ctY)

physics = Physics()