from actor import *
from utils import *

class Interactions(object):
	def get(self, interaction):
		return getattr(self, interaction)

	def touch(self, aA, aB):
		if aA.getAttribute('x') is aB.getAttribute('x') and aA.getAttribute('y') is aB.getAttribute('y'):
			return True
		else:
			return False

	def near(self, aA, aB):
		return True	
		#return self.under(aA, aB, padding=128)
		'''
		dist = 0
		half_dist = dist/2
		# Here we expand the boxes for the actors by half dist in each direction
		# This may very well move the rect up to the left a half_dist
		if isinstance(aA, Actor):
			aAxy = [aA.getAttribute('x')-half_dist, aA.getAttribute('y')-half_dist, aA.getAttribute('w')+half_dist, aA.getAttribute('h')+half_dist]
		else:
			aAxy = [0, 0, 0, 0]
			aAxy[0] = aA[0] - half_dist
			aAxy[1] = aA[1] - half_dist
			aAxy[2] = aA[2] + half_dist
			aAxy[3] = aA[3] + half_dist

		if isinstance(aB, Actor):
			aBxy = [aB.getAttribute('x')-half_dist, aB.getAttribute('y')-half_dist, aB.getAttribute('w')+half_dist, aB.getAttribute('h')+half_dist]
		else:
			aBxy = [0, 0, 0, 0]
			aBxy[0] = aB[0] - half_dist
			aBxy[1] = aB[1] - half_dist
			aBxy[2] = aB[2] + half_dist
			aBxy[3] = aB[3] + half_dist

		aAcenter = [aAxy[0] + (aAxy[2]/2), aAxy[1] + (aAxy[3]/2)]
		aBcenter = [aBxy[0] + (aBxy[2]/2), aBxy[1] + (aBxy[3]/2)]

		aAradius = utils.distance(aAcenter, aBxy)
		aBradius = utils.distance(aBcenter, aBxy)

		maxDistance = aAradius + aBradius
		distance = utils.distance(aAcenter, aBcenter)

		if maxDistance >= distance:
			#print maxDistance, distance, aAcenter, aBcenter
			return True
		else:
			return False
		'''

	def over(self, aA, aB, return_difference=False, aOffset=None, bOffset=None):
		if not aOffset:
			aOffset = [0, 0]
		if not bOffset:
			bOffset = [0, 0]

		near = self.near(aA, aB)
		if not near: 
			return False

		aAxy = utils.actorToList(aA)

		aAxy[0] += aOffset[0]
		aAxy[1] += aOffset[1]

		aBxy = utils.actorToList(aB)

		aBxy[0] += bOffset[0]
		aBxy[1] += bOffset[1]

		aABox = [
				xrange(aAxy[0], aAxy[0]+aAxy[2]),
				xrange(aAxy[1], aAxy[1]+aAxy[3])
		]

		aBBox = [
				xrange(aBxy[0], aBxy[0]+aBxy[2]),
				xrange(aBxy[1], aBxy[1]+aBxy[3])
		]

		xOver = xrange(max(aABox[0][0], aBBox[0][0]), min(aABox[0][-1], aBBox[0][-1])+1)
		yOver = xrange(max(aABox[1][0], aBBox[1][0]), min(aABox[1][-1], aBBox[1][-1])+1)

		is_over = bool(xOver) and bool(yOver)

		if return_difference:
			return is_over, [len(xOver), len(yOver)]
		else:
			return is_over

	def above(self, aA, aB):
		right_inside  	= aA[0]+aA[2] >= aB[0]
		left_inside 	= aA[0] <= aB[0]+aB[2]
		bottom_inside	= aA[1]+aA[3] >= aB[1]
		top_inside 		= aA[1] <= aB[1]+aB[3]

		right_outside  	= aA[0]+aA[2] >= aB[0]+aB[2]
		left_outside 	= aA[0] <= aB[0]
		bottom_outside	= aA[1]+aA[3] >= aB[1]+aB[3]
		top_outside 	= aA[1] <= aB[1]

		horizontal = (right_inside and not right_outside) or (left_inside and not left_outside) or (left_outside and right_outside)
		vertical = (bottom_inside and not bottom_outside) or (top_inside and not top_outside) or (top_outside and bottom_outside)

		return horizontal and vertical

	def under(self, aA, aB, padding=0):
		x_range = range(aA.getAttribute('x')-padding, aA.getAttribute('x')+aA.getAttribute('w')+padding)
		y_range = range(aA.getAttribute('y')-padding, aA.getAttribute('y')+aA.getAttribute('h')+padding)
		b_center = [
			aB.getAttribute('x') + (aB.getAttribute('w')/2),
			aB.getAttribute('y') + (aB.getAttribute('h')/2),
		]
		return b_center[0] in x_range and b_center[1] in y_range

	def see(self, aA, aB):
		aAxy = [aA.getAttribute('x'), aA.getAttribute('y'), aA.getAttribute('w'), aA.getAttribute('h')]
		aBxy = [aB.getAttribute('x'), aB.getAttribute('y'), aB.getAttribute('w'), aB.getAttribute('h')]
		aAcenter = [aAxy[0] + (aAxy[2]/2), aAxy[1] + (aAxy[3]/2)]
		aBcenter = [aBxy[0] + (aBxy[2]/2), aBxy[1] + (aBxy[3]/2)]

		return utils.distance(aAcenter, aBcenter) <= aA.getAttribute('sight-range')

	def reach(self, aA, aB):
		aAxy = [aA.getAttribute('x'), aA.getAttribute('y'), aA.getAttribute('w'), aA.getAttribute('h')]
		aBxy = [aB.getAttribute('x'), aB.getAttribute('y'), aB.getAttribute('w'), aB.getAttribute('h')]
		aAcenter = [aAxy[0] + (aAxy[2]/2), aAxy[1] + (aAxy[3]/2)]
		aBcenter = [aBxy[0] + (aBxy[2]/2), aBxy[1] + (aBxy[3]/2)]

		return utils.distance(aAcenter, aBcenter) <= aA.getAttribute('attack-range')

interactions = Interactions()