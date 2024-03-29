# Grids are like 2D arrays except they have support for sexy operations
import json 

infinity = 'infinity'
class Grid(object):
	def __init__(self, array=None, gridFile=None, width=None, height=None, defaultValue=0):
		# The array is the underlying storage
		if gridFile:
			self.array = json.loads(open(gridFile).read())
			self.width = len(self.array[0])
			self.height = len(self.array)
		elif array:
			self.array = array
			self.width = len(array[0])
			self.height = len(array)
		elif width and height:
			self.array = [[]]
			self.width = 0
			self.height = 0

		if width and height:
			self.width = width
			self.height = height

		self.defaultValue = defaultValue
		self.expandTo(self.width, self.height)

		assert gridFile or len(self.array) or (width and height), 'Expected either array or width and height'

	def __str__(self):
		# Convert grid to string
		string_rows = []
		for row in self.getArray():
			string_row = ""
			for col in row:
				string_row += str(col)
			string_rows.append(string_row)
	
		return '\n'.join(string_rows)

	def set(self, x, y, value):
		try:
			self.array[y][x] = value
		except IndexError:
			raise Exception('Can not set point %ix%i on grid of size %ix%i' % (x, y, len(self.array[0]), len(self.array)))

	def get(self, x, y):
		try:
			return self.array[y][x]
		except:
			return -1

	def getArray(self):
		return self.array

	def getRow(self, y):
		return self.array[y]

	def appendRow(self, row):
		return self.array.append(row)

	def split(self, size):
		# Blocksize is WH
		sections = []
		for sectiony in range(0, len(self.array)):
			if not sectiony % size[0]:
				row = []
				for sectionx in range(0, len(self.array[0])):
					if not sectionx % size[1]:
						location = [sectionx, sectiony]
						block = []
						for y in range(location[1], location[1]+size[1]):
							block.append([])
							for x in range(location[0], location[0]+size[0]):
								block[y-location[1]].append( self.get(x, y) )
						row.append(Grid(block))
				sections.append(row)
							
		return sections

	def expandTo(self, w, h):
		if w != infinity and h != infinity:
			for row in self.getArray():
				if len(row) < w:
					row.extend([self.defaultValue for b in range(0, w-len(row))])

			for r in range(0, h-len(self.getArray())):
				self.appendRow([self.defaultValue for b in range(0, w)])

			return True
		else:
			return False

	def canPaint(self, x, y, w, h):
		# Checks to see
		array 	= self.getArray()
		xWidth	= len(array)
		yWidth 	= len(array[0])

		wGood = False
		hGood = False

		if self.width is infinity:
			wGood = True
		else:
			if xWidth >= x+w or self.width >= x+w:
				wGood = True

		if self.height is infinity:
			hGood = True
		else:
			if yWidth >= y+h or self.height >= y+h:
				hGood = True		

		return all([wGood, hGood])

	def isEmpty(self):
		return not bool(len(self.getArray()))

	def copy(self):
		carray = []
		for row in self.array:
			crow = []
			for x in row:
				crow.append(x)
			carray.append(crow)
		return Grid(carray)

	def paint(self, grid, xoffset=0, yoffset=0):
		# Make sure the grid has content
		assert grid.isEmpty() is False, 'Cannot paint from an empty grid'

		# Pull the array
		array = grid.getArray()
		w = len(array[0])
		h = len(array)

		# Make sure the array can be painted at the location requested
		if self.canPaint(xoffset, yoffset, w, h):
			self.expandTo(xoffset+w, yoffset+h)
			for y, row in enumerate( array ):
				for x,col in enumerate( row ):
					value = grid.get(x, y)
					if value >= 0:	
						self.set(x+xoffset, y+yoffset, value)
			return True
		else:
			return False

# Logic Tests
if __name__ == '__main__':
	g1 = Grid([
		[0, 1, 0],
		[1, 1, 1],
		[0, 1, 0],
		[1, 1, 1]
	], width=6, height=6)
	g2 = Grid([
		[1, 1, 1],
		[1, 0, 1],
		[1, 1, 1],
		[0, 1, 1]
	])
	print g1
	print '---'
	print g2
	print '---'
	g1.paint(g2, 3, 0)
	print g1
	print g1.split([2, 2])