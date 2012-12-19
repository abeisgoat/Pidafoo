import pygame.mixer as mixer
import os, glob

class Hooter(object):
	def __init__(self):
		self.assets = {}
		mixer.init()

	def loadAsset(self, filename):
		path = os.path.splitext(filename)[0]
		audioID = os.path.split(path)[1]

		self.assets[audioID] = mixer.Sound(filename)
		return True

	def loadFolder(self, foldername):
		for asset in glob.glob(os.path.join(foldername, '*.ogg')):
			self.loadAsset(asset)

		print self.assets
		return True

	def play(self, assetID):
		self.assets[assetID].play()