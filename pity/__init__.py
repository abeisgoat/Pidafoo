#!/usr/bin/env python

# App Name: Pity -> The logical structure of a game
# Author: Abe Haskins
# Date: 26 November, 2012

import os, sys, re
import pygame
from pygame.locals import *

from pidafoo.hoot import *

from actor import *
from bindable import *
from existence import *
from effect import *
from interactions import *
from overlay import *
from physics import *
from stateful import *
from traits import *
from utils import *
from text import *

class Game(Bindable):
	'''
	Events:
	- start (Run called)
	- tick (Clock.tick called)
	- load existence (existence changed)
	- pressed [key] (key pressed)
	'''
	def __init__(self, screenSize):
		Bindable.__init__(self)
		pygame.init()
		pygame.display.set_caption('Template Game')

		self.screen = pygame.display.set_mode(screenSize)
		self.screenSize = screenSize
		self.clock = pygame.time.Clock()
		self.hoot = Hooter()
		self.dataset = None
		self.datasetFallback = 'vanilla'
		self.existence = None
		self.fps = 0

	def setExistence(self, existence):
		self.trigger('change existence')
		self.existence = existence

	def setDataset(self, datasetID):
		self.trigger('change dataset')
		self.dataset = datasetID

	def getBlocksFromSet(self):
		blocksPath = os.path.join('datasets', self.dataset, 'blocks')
		blocksGlob = os.path.join(blocksPath, '*.py')
		sys.path.insert(0, blocksPath)
		blocks = {}

		for blockfile in glob.glob(blocksGlob):
			filename = os.path.split(blockfile)[1]
			module = os.path.splitext(filename)[0]
			block = __import__(module)
			blocks[ block.bId ] = block

		sys.path.remove(blocksPath)
		return blocks

	def getDataFromSet(self, fntype, fileID):
		fntype_exts = {
			'sprites': '.png', 
			'maps': '.grid',
			'sounds': '.ogg'
		}
		filename = fileID + fntype_exts[fntype]
		datasetFn 	= os.path.join('datasets', self.dataset, 		 fntype, filename)
		datasetFnFb = os.path.join('datasets', self.datasetFallback, fntype, filename)

		if os.path.isfile(datasetFn):
			return datasetFn
		elif os.path.isfile(datasetFnFb):
			return datasetFnFb
		else:
			raise Exception('Cannot find "%s" of type "%s" in dataset "%s" or fallback "%s"' % (
				filename,
				fntype,
				self.dataset,
				self.datasetFallback
			))

	def run(self, dfps=60):
		self.trigger('start')
		keysDown = []
		while (1):
			self.clock.tick(dfps)

			keys = pygame.key.get_pressed() # Write down keys
			mods = pygame.key.get_mods() # Write down mods

			for key,pressed in enumerate(keys):
				if pressed:
					if not key in keysDown:
						self.trigger('down ' + str(key))
						keysDown.append(key)
					else:
						self.trigger('held ' + str(key))
				elif key in keysDown:
					self.trigger('up ' + str(key))
					keysDown.remove(key)

			self.trigger('step')
			self.existence.step()

			for event in pygame.event.get():
				if event.type == pygame.QUIT: return
				elif event.type == KEYDOWN and event.key == K_ESCAPE: return

			pygame.display.flip()
			self.fps = self.clock.get_fps()