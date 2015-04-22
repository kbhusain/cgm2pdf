
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
		self.pdfOut.setFont("Times-Roman", 10) 
		
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



	def setFloatColor(self,v): return float(v)/256.0 

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
			if directive.dtype == 'IMAGE': 
				x,y,w,h = directive.getParm('dimensions')
				if y < minY: minY = y 
				if y > maxY: maxY = y 
				if x < minX: minX = x 
				if x > maxX: maxX = x 
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
		self.pdfOut.translate(minX * -0.5, 0)   # Fit to page 

		for directive in self.directives: 
			if directive.dtype == 'POLYLINE':
				edge       = directive.getParm('edge_visible') 				
				fill_style = directive.getParm('fill_style') 
				polygon    = directive.getParm('polygon') 
				color_line = directive.getParm('color_line') 
				color_fill = directive.getParm('color_fill') 
				color_edge = directive.getParm('color_edge') 
				strokewidth= directive.getParm('strokewidth') 
				dash_array = directive.getParm('dash_array') 
				#print "STROE " , strokewidth 
				#strokewidth *=  PIXELS_PER_INCH

				self.pdfOut.setLineWidth(strokewidth)
				normalized =  directive.getParm('normalized') 
				ln = len(normalized) 
				if edge != 0: 
					#print color_fill, color_line, color_edge, strokewidth, polygon, edge
					strokeLine = 1	
					if color_edge: self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_edge[0]),self.setFloatColor(color_edge[1]), self.setFloatColor(color_edge[2]) )
					if color_line: self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_line[0]),self.setFloatColor(color_line[1]), self.setFloatColor(color_line[2]) )
				else:
					#print color_fill, color_line, color_edge, strokewidth, polygon, edge
					strokeLine = 0
					self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_line[0]),self.setFloatColor(color_line[1]), self.setFloatColor(color_line[2]) )

				if polygon == 0: 
					fillIt = 0
				else:
					fillIt = 1 
					if color_fill:
						self.pdfOut.setFillColorRGB(self.setFloatColor(color_fill[0]),self.setFloatColor(color_fill[1]), self.setFloatColor(color_fill[2]) )
				#if color_edge:
					#self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_edge[0]),self.setFloatColor(color_edge[1]), self.setFloatColor(color_edge[2]) )
				#if color_line:
					#self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_line[0]),self.setFloatColor(color_line[1]), self.setFloatColor(color_line[2]) )
				self.pdfOut.setDash(dash_array, 0)
				try:
					strokewidth *=  PIXELS_PER_INCH
				except:
					print "EXCEPTION:", strokewidth
				x = 0 
				self.pathPoints = self.pdfOut.beginPath() 
				self.pathPoints.moveTo(normalized[x], self.flipY(normalized[x+1] ))
				for x in range(2,ln,2):
					self.pathPoints.lineTo(normalized[x], self.flipY(normalized[x+1]))
				if polygon == 1: 
					self.pathPoints.lineTo(normalized[0], self.flipY(normalized[1]))
				self.pdfOut.drawPath(self.pathPoints, stroke=1, fill=0) 
				if fillIt: 	
					self.pdfOut.drawPath(self.pathPoints, stroke=0, fill=fillIt) 
				continue 

			if directive.dtype == 'IMAGE':
				filename = directive.getParm('tmpfile') 
				x,y,w,h = directive.getParm('dimensions')
				y1 = self.flipY(y) 
				self.pdfOut.drawImage(filename,x,y1,w,h)    # Arrgh I wish I did not have to go to the disk 
				os.unlink(filename)
				continue

			if directive.dtype == 'RECT':
				fill = directive.getParm('fill') 
				fillIt = 0
				if fill ==  "fill" : fillIt = 1
				color_line = directive.getParm('stroke')
				if color_line != 'none': 
					self.pdfOut.setStrokeColorRGB(self.setFloatColor(color_line[0]),self.setFloatColor(color_line[1]), self.setFloatColor(color_line[2]) )
					border = 1
				else: 
					border = 0 
					
				strokewidth = directive.getParm('strokewidth') 
				normalized =  directive.getParm('normalized') 
				x,y,w,h = directive.getParm('corners')
				y = self.flipY(y) 
				self.pdfOut.setLineWidth(strokewidth) 
				#print "RECT", stroke, x, y, w, h, border, fillIt, strokewidth, letter 
				self.pdfOut.rect(x,y,w,h, stroke=border, fill=fillIt) 
				continue 
			if directive.dtype == 'TEXT':
				dy=0
				rotationStr = "" 
				color  = directive.getParm('stroke')
				x,y    = directive.getParm('point') 
				outstr = directive.getParm('string')
				fontsize = directive.getParm('fontsize')  * 1.5
				matrix = directive.getParm('matrix')
				verticalAlignment = directive.getParm('verticalAlignment')
				horizontalAlignment = directive.getParm('horizontalAlignment')
				self.pdfOut.setFont("Helvetica", fontsize ) 
				self.pdfOut.setFillColorRGB(self.setFloatColor(color[0]),self.setFloatColor(color[1]), self.setFloatColor(color[2]) )
				dy = 0 
				dx = 0
 				char_height = fontsize
				if matrix:
					#if verticalAlignment==1: dy=char_height
					#self.pdfOut.saveState() 
					if verticalAlignment==1: dx=char_height * -1
					#if verticalAlignment==5: dx=
					self.pdfOut.saveState()
					y = self.flipY(y) 
					self.pdfOut.translate(x,y) 
					#self.pdfOut.transform(matrix[0],matrix[1],matrix[2],matrix[3],0,0)
					self.pdfOut.rotate(-90) 
					self.pdfOut.translate(-1*x,-1*y) 
					#print "MATRIX: ", matrix , verticalAlignment , dx
					self.pdfOut.drawRightString(x,y+dx,outstr)
					self.pdfOut.restoreState()
					continue	
				else:	
					if verticalAlignment==1: dy=char_height * -1 
					#if verticalAlignment==5: dy=char_height 
					
				y = self.flipY(y+dy) 
				#print "TEXT",  x, y, outstr, 'FONTSIZE=',  fontsize, "DY=", dy , 'VA=', verticalAlignment, horizontalAlignment, color

				if horizontalAlignment == 2: 
					self.pdfOut.drawCentredString(x,y,outstr)
				elif horizontalAlignment == 3: 
					self.pdfOut.drawRightString(x,y,outstr)
				else: 
					self.pdfOut.drawString(x,y,outstr)
				#--------------------------------------------------------------

		#print "Extremes", self.minX, self.minY, self.maxX, self.maxY, self.rangeX , self.rangeY, letter 
	
	def addImage(self,id,img,x,y,w,h,units="",fill_style="none",color_fill=[0,0,0],strokewidth=0.1,stroke_color='none'):
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
			w = w * PIXELS_PER_INCH 
			h = h * PIXELS_PER_INCH 
		directive = pdfDirective('IMAGE') 
		filename = "/tmp/kamran" + str(id) + ".gif"
		img.save(filename) 
		directive.putParm('tmpfile',filename)
		directive.putParm('dimensions',(x,y,w,h))
		directive.putParm('Image',img) 
		#print "Added IMAGE", x,y,w, h
		self.directives.append(directive) 
		return 

	##
	# Adds a line to output buffer. 
	# 	
	def addRectangle(self,id,x,y,w,h,units="",fill_style="none",color_fill=[0,0,0],strokewidth=0.1,stroke_color='none'):
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
	def addTextTag(self,x,y, outstr,defaults,anchor="start",color=[0,0,0],units="",fontsize=6,verticalAlignment=0, horizontalAlignment=0, matrix=None):
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
		self.cgmdefaults = defaults 
		directive = pdfDirective('TEXT') 
		directive.putParm('stroke',color) 
		directive.putParm('point',(x,y))
		directive.putParm('string',outstr)
 		fontsize = self.cgmdefaults.parameters['char_height'] * PIXELS_PER_INCH   # Pixels per inch 
		directive.putParm('fontsize',fontsize)
		directive.putParm('matrix',matrix)
		directive.putParm('verticalAlignment',verticalAlignment)
		directive.putParm('horizontalAlignment',horizontalAlignment)
		self.directives.append(directive) 
		return 	
		
	##
	#
	#  Data must be base64 encoded string. 
	def addPattern(self,patternIndex,width,height,precision=0,data=None): 
		pass	
		
	##
	# Polygon or Polyline - The first parameter specifies how to fill or not to fill - that is the question
	# Units are sent in as inches by defaults - We convert to pixels on the fly for the svg element
	#  
	# polygon = 1 ==> fill the interior with a color. 
	# units   = inches, "in", unless otherwise specified. 
	# 
	def addPolyLine(self,polygon=0,strokewidth=0.1,stroke=[0,0,0],strokedasharray=[],fill_style="none",color_fill=[0,101.0/256,0], edge_visible=1, points=[],patternIndex='1'):
		if (len(points) < 1):
			print "POLYLINE NOT DRAWN", points
			return  	
		directive = pdfDirective('POLYLINE') 
		directive.putParm('edge_visible',edge_visible) 
		directive.putParm('polygon',polygon) 
		directive.putParm('strokewidth',strokewidth) 
		directive.putParm('fill_style',fill_style) 
		directive.putParm('color_fill',color_fill) 
		directive.putParm('color_line',stroke) 
		directive.putParm('dash_array',strokedasharray) 
		normalized = [ PIXELS_PER_INCH * d for d in points ] 
		directive.putParm('normalized',normalized) 
		self.directives.append(directive) 


