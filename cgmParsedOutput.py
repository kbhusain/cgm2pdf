<<<<<<< HEAD

# Python command parser file 
import os,sys , getopt, array, Image
from struct import *
from cgmdesc import *
import math


PIXELS_PER_INCH = 72
# Make your classes here. 

class cgmParsedOutputClass:
	def __init__(self, outfilename): 
		self.filename = outfilename 
		self.outArray = "" 
	
	def saveFile(self):
		print "Save the file here" 
	 
	def addPolyLine(self, polygon=0, stroke='black', strokewidth=1, points=None, fill_style='None', edge_visible = True, 
				color_fill = "none",  strokedasharray=None): 
		print "polyline" 

	def addTextTag(self, x,y,s,anchor='start', color='black', units="in", 
				verticalAlignment='top', fontsize='12', horizontalAlignment='center', matrix=None):
		print "text" , x,y, s

	def addImage(self,imageId,image,x,y,width,height,units="in"): pass
	def addRectangle(self,name,x,y,wd,ht,units="in",
			stroke_color='black',
			strokewidth=2, 
			color_fill='blue', 
			fill_style='solid'):
		return	


htmlPreamble="""<!DOCTYPE html> 
<html> 
<head> <title> ... from the parser </title> 

<script type="text/javascript">  

function myLoad() { 
var myCanvas = document.getElementById("htmlCanvas"); 
var ctx = myCanvas.getContext("2d");
/*
ctx.lineWidth   = 2; 
ctx.beginPath(); 
ctx.moveTo(10,10); 
ctx.lineTo(10,50); 
ctx.lineTo(50,50); 
ctx.lineTo(50,10); 
alert("Help");
ctx.closePath(); 
ctx.stroke(); 
*/


"""

htmlPostamble =""" 
} 
</script>
</head>
<body onload=myLoad() >
Help <canvas id="htmlCanvas" width="%d" height="%d"> </canvas>
</body>
</html>
"""


##
# 
class cgmToHTML(cgmParsedOutputClass):
	def __init__(self, filename): 
		self.filename = filename   # The file I will write tow 
		self.outArray = [] 
		self.outArray.append(htmlPreamble)   # Starts script block
		self.maxY    = 0
		self.maxX    = 0 
		self.minY    = 0 
		self.minX    = 0 

	
	def saveFile(self):
		print "Save the file here" 
		width =  self.maxX - self.minX
		height = self.maxY - self.minY
		self.outArray.append(htmlPostamble % (int(width), int(height)))
		fd = open( self.filename , "w") 
		fd.write("\n".join(self.outArray)) 
		fd.close() 
	 
	def addTextTag(self, x,y,s,anchor='start', color='black', units="in", 
				verticalAlignment='top', fontsize='12', horizontalAlignment='center', matrix=None):
		pass
		#self.outArray.append('ctx.font = " bold 12px sans-serif"' ) 
		#self.outArray.append('ctx.fillText("%s",%s,%s);"' % (s,x,y))
	 
	def addPolyLine(self, polygon=0, stroke=[0,0,0], strokewidth=1, points=[] , fill_style='None', edge_visible = True, 
				color_fill = "none",  strokedasharray=None): 
		
		if len(points) >= 4: 
			self.outArray.append("ctx.beginPath();") 
			self.outArray.append("ctx.lineWidth = %d" % int(float(strokewidth) * PIXELS_PER_INCH + 1))
			# Stroke comes in as '[ d d d ]' - parse it 
			try:
				usecolor = '"#%02x%02x%02x"' % (stroke[0], stroke[1], stroke[2]) 
				self.outArray.append("ctx.strokeStyle = %s" % usecolor)  
			except:	
				print stroke
				self.outArray.append('ctx.strokeStyle = "black"' )  
				pass

			x,y = points[0]*PIXELS_PER_INCH, math.fabs(points[1]*PIXELS_PER_INCH ) 
			self.outArray.append("ctx.moveTo(%f,%f);" % (x,y)) 
			if x < self.minX: self.minX = x 	
			if y < self.minY: self.minY = y 	
			if x > self.maxX: self.maxX = x 	
			if y > self.maxY: self.maxY = y 	
			for pti in range(2,len(points),2):
				x,y = points[pti]*PIXELS_PER_INCH, math.fabs(points[pti+1]*PIXELS_PER_INCH  )
			#self.outArray.append("ctx.lineTo(%f,%f);" % (points[pti]*PIXELS_PER_INCH, math.fabs(points[pti+1]*PIXELS_PER_INCH  ) ))
				if x > self.maxX: self.maxX = x 	
				if y > self.maxY: self.maxY = y 	
				if x < self.minX: self.minX = x 	
				if y < self.minY: self.minY = y 	
				self.outArray.append("ctx.lineTo(%f,%f);" % (x,y))

			self.outArray.append("ctx.closePath();") 
			self.outArray.append("ctx.stroke();") 
=======

# Python command parser file 
import os,sys , getopt, array, Image
from struct import *
from cgmdesc import *
import math


PIXELS_PER_INCH = 72
# Make your classes here. 

class cgmParsedOutputClass:
	def __init__(self, outfilename): 
		self.filename = outfilename 
		self.outArray = "" 
	
	def saveFile(self):
		print "Save the file here" 
	 
	def addPolyLine(self, polygon=0, stroke='black', strokewidth=1, points=None, fill_style='None', edge_visible = True, 
				color_fill = "none",  strokedasharray=None): 
		print "polyline" 

	def addTextTag(self, x,y,s,anchor='start', color='black', units="in", 
				verticalAlignment='top', fontsize='12', horizontalAlignment='center', matrix=None):
		print "text" , x,y, s

	def addImage(self,imageId,image,x,y,width,height,units="in"): pass
	def addRectangle(self,name,x,y,wd,ht,units="in",
			stroke_color='black',
			strokewidth=2, 
			color_fill='blue', 
			fill_style='solid'):
		return	


htmlPreamble="""<!DOCTYPE html> 
<html> 
<head> <title> ... from the parser </title> 

<script type="text/javascript">  

function myLoad() { 
var myCanvas = document.getElementById("htmlCanvas"); 
var ctx = myCanvas.getContext("2d");
/*
ctx.lineWidth   = 2; 
ctx.beginPath(); 
ctx.moveTo(10,10); 
ctx.lineTo(10,50); 
ctx.lineTo(50,50); 
ctx.lineTo(50,10); 
alert("Help");
ctx.closePath(); 
ctx.stroke(); 
*/


"""

htmlPostamble =""" 
} 
</script>
</head>
<body onload=myLoad() >
Help <canvas id="htmlCanvas" width="%d" height="%d"> </canvas>
</body>
</html>
"""


##
# 
class cgmToHTML(cgmParsedOutputClass):
	def __init__(self, filename): 
		self.filename = filename   # The file I will write tow 
		self.outArray = [] 
		self.outArray.append(htmlPreamble)   # Starts script block
		self.maxY    = 0
		self.maxX    = 0 
		self.minY    = 0 
		self.minX    = 0 

	
	def saveFile(self):
		print "Save the file here" 
		width =  self.maxX - self.minX
		height = self.maxY - self.minY
		self.outArray.append(htmlPostamble % (int(width), int(height)))
		fd = open( self.filename , "w") 
		fd.write("\n".join(self.outArray)) 
		fd.close() 
	 
	def addTextTag(self, x,y,s,anchor='start', color='black', units="in", 
				verticalAlignment='top', fontsize='12', horizontalAlignment='center', matrix=None):
		pass
		#self.outArray.append('ctx.font = " bold 12px sans-serif"' ) 
		#self.outArray.append('ctx.fillText("%s",%s,%s);"' % (s,x,y))
	 
	def addPolyLine(self, polygon=0, stroke=[0,0,0], strokewidth=1, points=[] , fill_style='None', edge_visible = True, 
				color_fill = "none",  strokedasharray=None): 
		
		if len(points) >= 4: 
			self.outArray.append("ctx.beginPath();") 
			self.outArray.append("ctx.lineWidth = %d" % int(float(strokewidth) * PIXELS_PER_INCH + 1))
			# Stroke comes in as '[ d d d ]' - parse it 
			try:
				usecolor = '"#%02x%02x%02x"' % (stroke[0], stroke[1], stroke[2]) 
				self.outArray.append("ctx.strokeStyle = %s" % usecolor)  
			except:	
				print stroke
				self.outArray.append('ctx.strokeStyle = "black"' )  
				pass

			x,y = points[0]*PIXELS_PER_INCH, math.fabs(points[1]*PIXELS_PER_INCH ) 
			self.outArray.append("ctx.moveTo(%f,%f);" % (x,y)) 
			if x < self.minX: self.minX = x 	
			if y < self.minY: self.minY = y 	
			if x > self.maxX: self.maxX = x 	
			if y > self.maxY: self.maxY = y 	
			for pti in range(2,len(points),2):
				x,y = points[pti]*PIXELS_PER_INCH, math.fabs(points[pti+1]*PIXELS_PER_INCH  )
			#self.outArray.append("ctx.lineTo(%f,%f);" % (points[pti]*PIXELS_PER_INCH, math.fabs(points[pti+1]*PIXELS_PER_INCH  ) ))
				if x > self.maxX: self.maxX = x 	
				if y > self.maxY: self.maxY = y 	
				if x < self.minX: self.minX = x 	
				if y < self.minY: self.minY = y 	
				self.outArray.append("ctx.lineTo(%f,%f);" % (x,y))

			self.outArray.append("ctx.closePath();") 
			self.outArray.append("ctx.stroke();") 
>>>>>>> 1ea121057ce441ebcc5eda14b3ac6324de2ef8b4
