from bindable import *

# Traitful implements stats, reactions, and statuses

class Traitful(object):
	def __init__(self):
		self.stats = {}
		self.statModifiers = {}
		self.events = {}
		self.reactions = {}
		self.statuses = []
		self.bind('change-stat', self.react)

	def setStatus(self, status):
		if not status in self.statuses:
			self.statuses.append(status)

	def getStatus(self, status):
		return status in self.statuses

	def removeStatus(self, status):
		if status in self.statuses:
			self.statuses.remove(status)

	def addStat(self, statID, value=0, max=None, min=None):
		self.trigger('add-stat %s' % statID)
		if not statID in self.stats:
			self.stats[statID] = Stat(current=value, max=max, min=min)
		else:
			raise Exception('Can not add stat "%s", it already exists!' % statID)

	def setStat(self, statID, value):
		data = {'stat': statID, 'current': value, 'previous': self.getStat(statID)}
		result = self.stats[statID].set(value)
		if result:
			self.trigger('change-stat %s' % statID, data)
			self.trigger('change-stat', data)
			return True
		else:
			return False

	def getStat(self, statID):
		stat = self.stats.get(statID, None)
		if not stat is None:
			c = stat.current
			# Apply all modifiers to the stat
			for mod in self.statModifiers:
				mod = self.statModifiers[mod]
				c = mod.ify(statID, c)

			return c
		else:
			return None

	def removeStat(self, statID):
		self.trigger('remove-stat %s' % statID)
		self.stats.remove(statID)

	def addReaction(self, event, action):
		self.events[event.id] = event
		reactions = self.reactions.get(event.id, [])
		reactions.append(action)
		self.reactions[event.id] = reactions

	def addStatModifier(self, mod):
		self.statModifiers[mod.id] = mod

	def removeStatModifier(self, modId):
		self.statModifiers.pop(modId)
 
 	def react(self, traits, data):
 		for eventID in self.events:
			event = self.events[eventID]
			if event.check(self):
				for reaction in self.reactions[event.id]:
					self.act(reaction)

	def step(self):
		self.trigger('step')

class Stat(object):
	def __init__(self, current=0, min=None, max=None):
		self.min = min
		self.max = max
		self.set(current)
	def set(self, value):
		isBelowMax = value == min(value, self.max) or self.max == None
		isAboveMin = value == max(value, self.min) or self.min == None
		if isAboveMin and isBelowMax:
			self.current = value
			return True
		else:
			return False

class StatModifier(object):
	def __init__(self, modId, mods):
		self.id = modId
		self.mods = mods
		self.influences = mods.keys()

	def ify(self, statId, current):
		if statId in self.influences:
			mod = self.mods[statId]
			return current + mod
		else:
			return current

class ReactionEvent(object):
	def __init__(self, eventID, check):
		self.id = eventID
		self.check = check