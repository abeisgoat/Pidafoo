# Grids are like 2D arrays except they have support for sexy operations
import json 

infinity = 'infinity'
class Grid(object):
	def __init__(self, array=None, gridFile=None, width=None, height=None):
		# The array is the underlying storage
		if gridFile:
			self.array = json.loads(open(gridFile).read())
			self.width = len(self.array[0])
			self.height = len(self.array)
		elif array:
			self.array = array
			self.width = len(array[0])
			self.height = len(array)
		else:
			self.array = [[]]
			self.width = 0
			self.height = 0

		if width and height:
			self.width = width
			self.height = height

		self.defaultValue = 0

		assert gridFile or len(array) or (width and height), 'Expected either array or width and height'

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
		self.array[y][x] = value

	def get(self, x, y):
		return self.array[y][x]

	def getArray(self):
		return self.array

	def getRow(self, y):
		return self.array[y]

	def appendRow(self, row):
		return self.array.append(row)

	def expandTo(self, w, h):
		for row in self.getArray():
			if len(row) < w:
				row.extend([self.defaultValue for b in range(0, w-len(row))])

		for r in range(0, h-len(self.getArray())):
			self.appendRow([self.defaultValue for b in range(0, w)])

		return True

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
		[0, 1, 0]
	], width=6, height=6)
	g2 = Grid([
		[1, 1, 1],
		[1, 0, 1],
		[1, 1, 1]
	])
	print g1
	print '---'
	print g2
	print '---'
	g1.paint(g2, 3, 0)
	print g1