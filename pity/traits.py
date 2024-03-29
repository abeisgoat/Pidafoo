from bindable import *

# Traitful implements stats, reactions, and statuses

class Traitful(object):
	def __init__(self):
		self.setAttribute('stats', {})
		self.statModifiers = {}
		self.events = {}
		self.reactions = {}
		self.statuses = []
		self.bind('change-stat-base', self.react)

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
		stats = self.attributes['stats']
		if not statID in stats:
			stats[statID] = Stat(current=value, max=max, min=min)
		else:
			raise Exception('Can not add stat "%s", it already exists!' % statID)	
		self.setAttribute('stats', stats)

	def setStat(self, statID, value):
		old = self.getStat(statID)
		result = self.attributes['stats'][statID].set(value)
		data = {'stat': statID, 'current': self.getStat(statID), 'previous': old}
		if result:
			self.trigger('change-stat-base %s' % statID, data)
			self.trigger('change-stat-base', data)
			return True
		else:
			return False

	def getStat(self, statID):
		stat = self.attributes['stats'].get(statID, None)
		c = self.getBaseStat(statID)
		# Apply all modifiers to the stat
		for mod in self.statModifiers:
			mod = self.statModifiers[mod]
			c = mod.ify(statID, c)
		return c

	def getBaseStat(self, statID):
		stat = self.attributes['stats'].get(statID, None)
		if not stat is None:
			c = stat.current
			return c
		else:
			return 0


	def getStats(self):
		return self.attributes['stats']

	def removeStat(self, statID):
		self.trigger('remove-stat %s' % statID)
		self.attributes['stats'].remove(statID)

	def addReaction(self, event, action):
		self.events[event.id] = event
		reactions = self.reactions.get(event.id, [])
		reactions.append(action)
		self.reactions[event.id] = reactions

	def addStatModifier(self, mod):
		self.statModifiers[mod.id] = mod
		for influenced in mod.influences:
			data = {'stat': influenced, 'current': self.getStat(influenced)}
			self.trigger('change-stat %s' % influenced, data)

	def hasStatModifierType(self, modType):
		if modType != None:
			for omodKey in self.statModifiers:
				omod = self.statModifiers[omodKey]
				if omod.type == modType:
					return True
		return False

	def removeStatModifierType(self, modType):
		trashed = []
		if modType != None:
			for omodKey in self.statModifiers:
				omod = self.statModifiers[omodKey]
				if omod.type == modType:
					trashed.append(omod)

		for mod in trashed:
			self.removeStatModifier(mod)

	def removeStatModifier(self, modId):
		self.statModifiers.pop(modId.id)
 
 	def react(self, traits, data):
 		for eventID in self.events:
			event = self.events[eventID]
			if event.check(self):
				for reaction in self.reactions[event.id]:
					self.act(reaction)

	def step(self):
		self.trigger('step')

class Stat(object):
	def __init__(self, current=0, min=None, max=None, on_max=None, on_min=None):
		self.min = min
		self.max = max
		self.set(current)
	def set(self, value):
		isBelowMax = value == min(value, self.max) or self.max == None
		isAboveMin = value == max(value, self.min) or self.min == None
		if isAboveMin and isBelowMax:
			self.current = value
			return True
		elif not isAboveMin:
			self.current = self.min
			return True
		elif not isBelowMax:
			self.current = self.max
			return True
		else:
			return False

class StatModifier(object):
	def __init__(self, modId, mods, type=None):
		self.id = modId
		self.mods = mods
		self.type = type
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