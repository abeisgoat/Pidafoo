from bindable import *
# Should statefulness include actions and interactions too?
class Stateful(object):
	def __init__(self):
		self.states = {
			'default': State('default')
		}
		self.setState('default')

	def addState(self, stateID, state=None):
		if state is None:
			state = State(stateID)
		self.states[stateID] = state

	def removeState(self, stateID):
		self.states.remove(stateID)

	def setState(self, stateID):
		self.currentStateID = stateID
		self.currentState = self.states[stateID]

	def getState(self, stateID=None):
		if stateID is None:
			return self.currentState
		else:
			return self.states[stateID]

	# Reroute all the bindable calls to talk to the current State object
	# not the stateful object itself
	def bind(self, binding, callback):
		return Bindable.bind(self.getState(), binding, callback)

	def unbind(self, func=None, binding=None):
		return Bindable.unbind(self.getState(), func=func, binding=binding)

	def check(self, binding):
		return Bindable.check(self.getState(), binding, selfOverload=self)

	def trigger(self, binding, data=None):
		return Bindable.trigger(self.getState(), binding, data, selfOverload=self)

	def quene(self, binding):
		return Bindable.quene(self.getState(), binding)

	def hasQuene(self):
		return Bindable.hasQuene(self.getState())

	def clearQuene(self):
		return Bindable.clearQuene(self.getState(), selfOverload=self)

class State(Bindable):
	def __init__(self, sid):
		Bindable.__init__(self)
		self.id = sid