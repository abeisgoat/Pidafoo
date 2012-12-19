import re, math
class Utils(object):
	interaction_re = re.compile('([^ ]+) (.+)')
	def wrap_exact(self, func, args, kwargs):
		def wfunc(*args, **kwargs):
			return func(*args, **kwargs)
		return wfunc

	def parseInteraction(self, interaction):
		parsed = self.interaction_re.findall(interaction)
		if len(parsed):
			parsed = parsed[0]
			if parsed[0][0] is '!':
				action = parsed[0][1:]
			else:
				action = parsed[0]

			if parsed[1].split(':') != [parsed[1]]:
				constraint,value = parsed[1].split(':')
				selectors = {}
				selectors[constraint] = value
				i = {'action': action, 'selectors': selectors}
			else:
				i = {'action': action, 'other': parsed[1]}
			return i
		else:
			raise Exception('Can not parse interaction string "%s"' % interaction)

	def closerTo(self, values, goal):
		winner = None
		for value in values:
			if winner is None:
				winner = value
			else:
				if abs(value-goal) < abs(winner-goal):
					winner = value
		return winner

	def distance(self, pointA, pointB):
		xdiff = pointA[0] - pointB[0]
		ydiff = pointA[1] - pointB[1]
		xSq = xdiff*xdiff
		ySq = ydiff*ydiff
		distance = math.sqrt(xSq + ySq)
		return distance

	def actorToList(self, actor):
		return [actor.getAttribute('x'), actor.getAttribute('y'), actor.getAttribute('w'), actor.getAttribute('h')]

utils = Utils()