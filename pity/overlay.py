from actor import *
from bindable import *

# The only difference between an overlay and 
# an actor is that an overlay is called an overlay
# and overlays are always drawn on top of everything
# else
class Overlays(Bindable):
	def __init__(self, overlays=None):
		Bindable.__init__(self)
		if overlays:
			self.overlays = overlays
		else:
			self.overlays = {}

	def getOverlays(self):
		return self.overlays

	def addOverlay(self, overlay):
		self.trigger('add overlay')
		self.overlays[overlay.id] = overlay

	def setOverlay(self, overlay):
		self.overlays[overlay.id] = overlay

	def removeOverlay(self, overlayID):
		self.trigger('remove overlay')
		self.overlays.pop(overlayID)

	def getOverlay(self, overlayID):
		return self.overlays[overlayID]

class Overlay(Actor):
	pass