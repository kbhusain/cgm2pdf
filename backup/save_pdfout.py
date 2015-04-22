
import os, sys 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm as CM 
from reportlab.lib.units import inch as IN

PIXELS_PER_INCH = IN

class pdfDirective:
	def  __init__(self, mytype=""):
		self.dtype = mytype; 
		self.parms = { } 

	def putParm(self,key,value):
		self.parms[key] = value 

	def getParm(self,key,value=None):
		return self.parms.get(key,value) 


class PDFout: 
	def __init__(self, filename):
		#-------------------------------------------------------------------------------------
		# Elements of style:
		#-------------------------------------------------------------------------------------
		self.filename = filename
		self.stroke = "black"
		self.fill   = "white"
		self.strokewidth = 1
		self.fontsize =    8 
		self.units = ""
		self.width = "100%"
		self.height = "100%"
		self.cgmdefaults = [] 
		#-------------------------------------------------------------------------------------
		# Outputs 
		#-------------------------------------------------------------------------------------

		self.pdfOut = canvas.Canvas(self.filename,pagesize = letter) 
		self.pathPoints = [] 
		self.pdfOut.setFont("Courier", 10) 
		
		self.minY = 1000000.0;
		self.maxY = -100000.0; 
		self.minX = 1000000.0;
		self.maxX = -100000.0; 

		# Filled in the order received. 
		self.directives = [ ] 

	def saveFile(self) :
		self.commitDirectives() 
		self.pdfOut.showPage() 
		self.pdfOut.save() 



	def setStrokeWidth(self,num=1): self.strokewidth = float(num)

	##########################################################################
	# Always sets in pixels, 
	def setLimits(self,wd,ht,units="px"):
		if units == 'in': 
			self.width = str(wd  * PIXELS_PER_INCH) 
			self.height = str(ht * PIXELS_PER_INCH) 
		else:
			self.width = str(wd) + self.units
			self.height = str(ht) + self.units
	
	##
	# Polygon or Polyline - The first parameter specifies how to fill or not to fill - that is the question
	# Units are sent in as inches by defaults - We convert to pixels on the fly for the svg element
	#  
	# polygon = 1 ==> fill the interior with a color. 
	# units   = inches, "in", unless otherwise specified. 
	# 
	def addPolyLine(self,polygon=0,units="in",stroke=[0,0,0],strokewidth=0.1,strokedasharray=None,fill="none",points=[]):
		if (len(points) < 1):return  	
		directive = pdfDirective('POLYLINE') 
		directive.putParm('stroke',stroke) 
		directive.putParm('strokewidth',strokewidth) 
		directive.putParm('fill',fill) 
		normalized = [ PIXELS_PER_INCH * d for d in points ] 
		directive.putParm('normalized',normalized) 
		self.directives.append(directive) 

	##
	# yp = self.rangeY + self.minY - y  
	#
	def flipY (self, y): 
		#---------> FLIPPED IMAGE  return self.rangeY - y + self.minY  
		return  y - self.minY


	def commitDirectives(self):
		# First find the maximum and minimum in inches 
		minY = 1000000.0;
		maxY = -1000000.0; 
		minX = 10000000.0;
		maxX = -1000000.0; 
		for directive in self.directives:  
			if directive.dtype == 'RECT': 
				x,y,w,h = directive.getParm('corners')
				if y < minY: minY = y 
				if y > maxY: maxY = y 
				if x < minX: minX = x 
				if x > maxX: maxX = x 
			if directive.dtype == 'TEXT': 
				x,y = directive.getParm('point')
				if y < minY: minY = y 
				if y > maxY: maxY = y 
				if x < minX: minX = x 
				if x > maxX: maxX = x 
			if directive.dtype == 'POLYLINE':
				normalized =  directive.getParm('normalized') 
				ln = len(normalized) 
				for r in range(0,ln,2):
					x = normalized[r]
					y = normalized[r+1]
					if y < minY: minY = y 
					if y > maxY: maxY = y 
					if x < minX: minX = x 
					if x > maxX: maxX = x 
		self.minY = minY
		self.maxY = maxY 
		self.minX = minX
		self.maxX = maxX 
		self.rangeX = maxX - minX 
		self.rangeY = maxY - minY 

		# =================================================================== 
		# Now swap the Y axis yourself. This is complicated. 
		# =================================================================== 
		scaleX = letter[0] /(self.rangeX)
		scaleY = letter[1] /(self.rangeY) 
		self.pdfOut.scale(scaleX, scaleY)   # Fit to page 

		for directive in self.directives: 
			if directive.dtype == 'POLYLINE':
				fill = directive.getParm('fill') 
				stroke = directive.getParm('stroke') 
				strokewidth = directive.getParm('strokewidth') 
				normalized =  directive.getParm('normalized') 
				
				if fill == 'none' or fill == None: 
					fillIt = 0
					self.pdfOut.setFillColorRGB(stroke[0],stroke[1],stroke[2]) 
					self.pdfOut.setStrokeColorRGB(stroke[0],stroke[1],stroke[2]) 
				else:
					fillIt = 1 
					self.pdfOut.setFillColorRGB(stroke[0],stroke[1],stroke[2]) 
					self.pdfOut.setStrokeColorRGB(0,0,0)
				ln = len(normalized) 
				self.pathPoints = self.pdfOut.beginPath() 
				x = 0 
				self.pdfOut.setLineWidth(strokewidth) 
				self.pathPoints.moveTo(normalized[x], self.flipY(normalized[x+1] ))
				for x in range(2,ln,2):
					self.pathPoints.lineTo(normalized[x], self.flipY(normalized[x+1]))
				if fillIt: 
					self.pathPoints.lineTo(normalized[0], self.flipY(normalized[1]))
				self.pdfOut.drawPath(self.pathPoints, fill=fillIt) 
				continue 
			if directive.dtype == 'RECT':
				fill = directive.getParm('fill') 
				fillIt = 0
				if fill ==  "fill" : fillIt = 1
				stroke = directive.getParm('stroke')
				if stroke != 'none': 
					self.pdfOut.setStrokeColorRGB(stroke[0],stroke[1],stroke[2])
					border = 1
				else: 
					border = 0 
					
				strokewidth = directive.getParm('strokewidth') 
				normalized =  directive.getParm('normalized') 
				x,y,w,h = directive.getParm('corners')
				y = self.flipY(y) 
				self.pdfOut.setLineWidth(strokewidth) 
				if fillIt == 1: print "RECT", stroke, x, y, w, h, border, fillIt, strokewidtk, letter 
				self.pdfOut.rect(x,y,w,h, stroke=border, fill=fillIt) 
				continue 
			if directive.dtype == 'TEXT':
				dy=0
				rotationStr = "" 
				#fontsize =  PIXELS_PER_INCH  * self.cgmdefaults.parameters['char_height']   # Pixels per inch 
				color  = directive.getParm('stroke')
				x,y    = directive.getParm('point') 
				outstr = directive.getParm('string')
				fontsize = directive.getParm('fontsize')
				matrix = directive.getParm('matrix')
				verticalAlignment = directive.getParm('verticalAlignment')
				self.pdfOut.setFont("Courier", fontsize) 
				self.pdfOut.setFillColorRGB(color[0],color[1],color[2]) 
				dy = 0 
 				char_height = self.cgmdefaults.parameters['char_height'] * PIXELS_PER_INCH   # Pixels per inch 
				if matrix:
					#if verticalAlignment==1: dy=char_height
					if verticalAlignment==5: dy=char_height * -1 
				else:	
					if verticalAlignment==1: dy=char_height * -1 
					#if verticalAlignment==5: dy=char_height 
					
				y = self.flipY(y+dy) 
				print "TEXT",  x, y, outstr, 'FONTSIZE=',  fontsize, "DY=", dy , 'VA=', verticalAlignment, matrix, char_height
				self.pdfOut.drawString(x,y,outstr)

		print "Extremes", self.minX, self.minY, self.maxX, self.maxY, self.rangeX , self.rangeY, letter 
	
	##
	# Adds a line to output buffer. 
	# 	
	def addRectangle(self,id,x,y,w,h,units="",fill_style="none",fill_color=[0,0,0],strokewidth=0.1,stroke_color='none'):
		# Accummulate the style. 
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
			w = w * PIXELS_PER_INCH 
			h = h * PIXELS_PER_INCH 
		directive = pdfDirective('RECT') 
		directive.putParm('stroke',stroke_color) 
		directive.putParm('strokewidth',strokewidth) 
		directive.putParm('fill',fill_style) 
		directive.putParm('corners',(x,y,w,h))
		self.directives.append(directive) 
		return 

	
	##
	# defaults.parameters must have set the following items:
	# ['color_line']
	# ['char_height']
	# ['rotate'] to the value of the matrix in c5
	# 
	def addTextTag(self,x,y, outstr,defaults,anchor="start",color=[0,0,0],units="",fontsize=6,verticalAlignment=0,matrix=None):
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
		self.cgmdefaults = defaults 
		directive = pdfDirective('TEXT') 
		directive.putParm('stroke',color) 
		directive.putParm('point',(x,y))
		directive.putParm('string',outstr)
		directive.putParm('fontsize',fontsize)
		directive.putParm('matrix',matrix)
		directive.putParm('verticalAlignment',verticalAlignment)
		self.directives.append(directive) 
		return 	
		


