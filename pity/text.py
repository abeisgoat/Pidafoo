import pygame.font
import pygame.color
pygame.font.init()
font = pygame.font.Font("Ubuntu-Regular.ttf", 11)

class Text(object):
	def render(self, text, color=None):
		if color is None:
			color = (0, 200, 0, 0)
		return font.render(text, True, color, (0, 0, 0, 0))
	def size(self, text):
		return font.size(text)

text = Text()