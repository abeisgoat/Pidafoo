from interactions import *
from utils import *

class Physics(object):
	def applyForces(self, actor, data):
		if actor.active:
			xChange = actor.getAttribute('forceX')
			yChange = actor.getAttribute('forceY')
			actor.increaseAttribute('x', xChange)
			actor.increaseAttribute('y', yChange)

	def adjustForces(self, actor, other, data):
		aBoxF = [actor.getAttribute('x')+actor.getAttribute('forceX'), actor.getAttribute('y')+actor.getAttribute('forceY'), actor.getAttribute('w'), actor.getAttribute('h')]
		aBox = [actor.getAttribute('x'), actor.getAttribute('y'), actor.getAttribute('w'), actor.getAttribute('h')]
		oBox = [other.getAttribute('x'), other.getAttribute('y'), other.getAttribute('w'), other.getAttribute('h')]
		is_over = interactions.over(aBoxF, oBox)
		if other.getAttribute('solid'):
			if is_over:
				io, diff = interactions.over(aBox, oBox, return_difference=True)

				ctX = utils.closerTo([diff[0], actor.getAttribute('forceX')], 0)
				ctY = utils.closerTo([diff[1], actor.getAttribute('forceY')], 0)

				if ctX != actor.getAttribute('forceX'):
					actor.setAttribute('forceX', ctX)

				if ctY != actor.getAttribute('forceY'):
					actor.setAttribute('forceY', ctY)

physics = Physics()