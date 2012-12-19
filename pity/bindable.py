from collections import defaultdict
class Bindable(object):
	def __init__(self, bindings=None):
		if not bindings:
			self.__bindings__ = defaultdict(list)
		else:
			self.__bindings__ = bindings
		self.__bindingsQuene__ = []

	def bind(self, binding, callback):
		self.__bindings__[binding].append(callback)
		return self.__bindings__

	def unbind(self, func=None, binding=None):
		if binding and not func:
			if binding in self.__bindings__:
				return self.__bindings__.remove(binding)
			else:
				return False
		elif func and not binding:
			for binding in self.__bindings__:
				if func in self.__bindings__[binding]:
					return self.__bindings__[binding].remove(func)
			return False
		elif func and binding:
			if func in self.__bindings__[binding]:
				return self.__bindings__[binding].remove(func)
			else:
				return False

	def check(self, binding, selfOverload):
		if binding in self.__bindings__Quene__:
			self.__bindingsQuene__.remove(binding)
			return self.trigger(binding, selfOverload)
		else:
			return False

	def trigger(self, binding, data=None, selfOverload=None):
		if data is None:
			data = {}

		if not selfOverload:
			selfOverload = self

		callbacks = self.__bindings__[binding]
		for cb in callbacks:
			cb(selfOverload, data)

	def quene(self, binding):
		if binding in self.__bindings__:
			self.__bindingsQuene__.append(binding)

	def hasQuene(self):
		return bool(self.__bindingsQuene__)

	def clearQuene(self, selfOverload=None):
		for binding in self.__bindingsQuene__:
			self.trigger(binding, selfOverload)