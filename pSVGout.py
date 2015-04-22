
import os, sys 


svgPreamble = """<?xml version="1.0" standalone="no"?>
<svg  xmlns="http://www.w3.org/2000/svg"      xmlns:xlink="http://www.w3.org/1999/xlink"
viewBox="%d %d %d %d" preserveAspectRatio="xMinYMax" version="1.1">

"""
# viewBox="%d %d %d %d" preserveAspectRatio="none" version="1.1">

svgTerminator = """</svg>"""

svgStyles = """
<style type="text/css"> 
<![CDATA[
	.FontTextAnchorMiddle{text-anchor:middle;}
	.FontTextAnchorLeft{text-anchor:left;}
	.FontTextAnchorRight{text-anchor:right;}
	%s 

  ]]>
</style> 
"""

html_svg_Holder="""
<html> 

<head>

</head> 
<body>
	<embed src="%(filename)s" width="199%%" height="199%%" align="center" />
</body>
</html>
"""


PIXELS_PER_INCH = 90.0; 


class SVGout: 
	def __init__(self, filename=None):
		self.filename = filename
		#-------------------------------------------------------------------------------------
		# Elements of style:
		#-------------------------------------------------------------------------------------
		self.stroke = "black"
		self.fill = "white"
		self.strokewidth = 1
		self.fontsize = 11 
		self.style = "stroke:%s;stroke-width:%f;fill:%s" % (self.stroke,self.strokewidth,self.fill)
		self.units = ""
		self.width = "100%"
		self.height = "100%"
		#-------------------------------------------------------------------------------------
		# Outputs 
		#-------------------------------------------------------------------------------------
		self.preamble = svgPreamble ; # % (self.width, self.height)
		self.xmlLines = [] 
		self.terminator = svgTerminator
		self.minY = 1000000.0;
		self.maxY = -100000.0; 
		self.minX = 1000000.0;
		self.maxX = -100000.0; 
		self.Yscale = -1
	
	def flipY(self) : self.Yscale = -1; 
	def reverseYscale(self) : self.Yscale = -1; 
	def setStrokeWidth(self,num=1): self.strokewidth = float(num)


	def countXlimits(self,x):
		if x < self.minX: self.minX = x 
		if x > self.maxX: self.maxX = x 

	def countYlimits(self,y):
		if y < self.minY: self.minY = y 
		if y > self.maxY: self.maxY = y 

	##########################################################################
	# Always sets in pixels, 
	##########################################################################
	def setLimits(self,wd,ht,units="px"):
		if units == 'in': 
			self.width = str(wd  * PIXELS_PER_INCH) 
			self.height = str(ht * PIXELS_PER_INCH) 
		else:
			self.width = str(wd) + self.units
			self.height = str(ht) + self.units
	
	def getXMLout(self): 
		# outstr = [svgPreamble % (self.width, self.height),] 

		print self.minX, self.maxX, self.minY, self.maxY	
		pstr = svgPreamble % (int(self.minX), int(self.minY), int(self.maxX - self.minX) , int(self.maxY - self.minY))
		outstr = [pstr , ] 
		for xl in self.xmlLines: outstr.append(xl)
		outstr.append(self.terminator)
		return "\n".join(outstr)
	
	def addSVG(self,rawSVG) : self.xmlLines.append(rawSVG) 

	def addImage(self,id, imageData,x1,y1,wd,ht,units=""):
		return 
		self.xmlLines.append('<image xlink:href="%s"  x="%f%s" y="%f%s" width="%f%s" height="%f%s" />' \
			% ( xfilename,x1,units,y1,units,wd,units,ht,units) ) 

	def addHeaderImage(self,xfilename,x1,y1,wd,ht,units=""):
		return 
		self.xmlLines.append('<image xlink:href="%s"  x="%f%s" y="%f%s" width="%f%s" height="%f%s" />' \
			% ( xfilename,x1,units,y1,units,wd,units,ht,units) ) 


	def convertColor(self,incoming):
		#print "CONVERTING...incoming ", incoming , incoming[0]
		try:
			return "#%02x%02x%02x" % tuple(map(int,incoming)) 
			# return "#%02x%02x%02x" % (items[0],items[1],items[2])
		except:
			return incoming 
		
	##
	# Adds a line to output buffer. 
	# 	
	def addLine(self,x1,y1,x2,y2,units="",stroke="black",strokewidth=1,id="None", strokedasharray=None):
		if units == "in": 
			x1 = x1 * PIXELS_PER_INCH 
			y1 = y1 * PIXELS_PER_INCH 
			x2 = x2 * PIXELS_PER_INCH 
			y2 = y2 * PIXELS_PER_INCH 
		y1 = y1 * self.Yscale
		y2 = y2 * self.Yscale
		c_stroke = self.convertColor(stroke) 
		style = "stroke:%s;stroke-width:%f%s" % (c_stroke,strokewidth,units)
		if strokedasharray: 
			style += ';stroke-dasharray:%s' % strokedasharray
		self.xmlLines.append('<line x1="%f" y1="%f" x2="%f" y2="%f" style="%s" />\n' \
			% ( x1,y1,x2,y2,style) ) 

	##
	#
	#  Data must be base64 encoded string. 
	def addPattern(self,patternIndex,width,height,precision=0,data=None): 
		if data == None: return ; 
		patternString = '<pattern id="pattern_%s" width="%d" height="%d" patternUnits="userSpaceOnUse" >' % (patternIndex,width,height) 
		self.xmlLines.append(patternString) 
		patternString = '<image width="%d" height="%d" xlink:href="data:image/png;base64,%s" />' % (width,height,data) 
		self.xmlLines.append(patternString) 
		self.xmlLines.append('</pattern>') 


	##
	# Polygon or Polyline - The first parameter specifies how to fill or not to fill - that is the question
	# Units are sent in as inches by defaults - We convert to pixels on the fly for the svg element
	# fill_style is IGNORED for now
	# 
	def addPolyLine(self,polygon=0, stroke="black",    strokewidth=0.1, points=[],  fill_style="none", edge_visible=1, color_fill="none", strokedasharray=None, units="in", patternIndex='1'):
		if (len(points) < 2):return  	
		if units == "in": strokewidth *= PIXELS_PER_INCH 
		#if fill_style != 'none': 
		#	style += ";fill:%s" % color_fill
		#else:
		#	style += ";fill:none"
		c_stroke = self.convertColor(stroke) 
		c_color_fill = self.convertColor(color_fill) 
		
		#print "fill_style", fill_style
		if fill_style == 'pattern':
			pathList = 'stroke="%s" stroke-width="%f" fill="url(#pattern_%s)"' % (c_stroke,strokewidth,patternIndex)  
		else: 
			pathList = 'stroke="%s" stroke-width="%f" fill="%s"' % (c_stroke,strokewidth,c_color_fill)  
		if strokedasharray: pathList += ' stroke-dasharray="%s"' % strokedasharray
		# print "POLYLINE", points, strokewidth
		self.xmlLines.append('<path  ' + pathList) 
		normalized = [ PIXELS_PER_INCH * d for d in points ] 
		self.xmlLines.append('d="M%f,%f ' % (normalized[0], normalized[1] * self.Yscale))
		ln = len(normalized) 
		for x in range(2,ln,2):
			self.xmlLines.append('L%f,%f ' % (normalized[x], normalized[x+1] * self.Yscale))
		if polygon == 1: 
			#self.xmlLines.append('L%f,%f ' % (normalized[-2], normalized[-1] * self.Yscale))
			self.xmlLines.append('Z"/>') 
		else:  
			self.xmlLines.append('"/>') 
	
	##
	# Adds a line to output buffer. 
	# 	
	def addRectangle(self,id,x,y,w,h,units="", stroke_color='black', strokewidth=0, color_fill="none", fill_style="none"):
		if strokewidth == 0 and color_fill == "none": return 
		# Accummulate the style. 
		style = "" 
		#print "COLORS", stroke_color, color_fill
		c_color_fill = self.convertColor(color_fill) 
		#print "COLORS", c_color_fill
		c_stroke_color = self.convertColor(stroke_color) 
		#print "RECTANGLE", x,y,w,h
		if strokewidth > 0: style += "stroke-width:%f" % (strokewidth * PIXELS_PER_INCH) 
		if fill_style != 'none': 
			style += ";fill:%s" % c_color_fill
		else:
			style += ";fill:none"
		style += ";stroke:%s" % c_stroke_color
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
			w = w * PIXELS_PER_INCH 
			h = h * PIXELS_PER_INCH 

		y  = y * self.Yscale 
		y2 = y + h
		#print y, y2, self.Yscale
		y = min(y, y2)
		self.xmlLines.append('<rect id="%s" x="%f" y="%f" width="%f" height="%f" style="%s"/>'  % ( id,x,y,w,h,style) ) 
		#print  '<rect id="%s" x="%f" y="%f" width="%f" height="%f" style="%s"/>'  % ( id,x,y,w,h,style) 
		self.countXlimits(x)
		self.countXlimits(x+w)
		self.countYlimits(h-y)
		self.countYlimits(y)
	
	##
	# defaults.parameters must have set the following items:
	# ['color_line']
	# ['char_height']
	# ['rotate'] to the value of the matrix in c5
	# 
	def addTextTag(self,x,y, outstr,defaults, anchor="start", color='black', units="in", verticalAlignment=0, horizontalAlignment=0, fontsize=10, matrix=None):
		if units == "in": 
			x = x * PIXELS_PER_INCH 
			y = y * PIXELS_PER_INCH 
		y = y * self.Yscale
		dy=0
		rotationStr = "" 
		fontsize = int( PIXELS_PER_INCH  * defaults.parameters['char_height'])   # Pixels per inch 
		c_color = self.convertColor(color) 
		if matrix: 	
			if verticalAlignment==1: dy=fontsize * -1
			if verticalAlignment==5: dy=fontsize 
			rotationStr = ' transform="matrix(%f,%f,%f,%f,%f,%f)" ' % (matrix[1], matrix[0], matrix[3], matrix[2], x + dy, y  ) 
			self.xmlLines.append('<text style="text-anchor:%s" font-size="%f" %s ><tspan fill="%s">%s</tspan></text>' % (anchor,fontsize,rotationStr,c_color,outstr))
		else:	
			#if verticalAlignment==1: dy=fontsize
			#if verticalAlignment==5: dy=fontsize*-0.2                # Usually for the title
			if verticalAlignment==1: dy=fontsize
			if verticalAlignment==5: dy=fontsize * -1
			self.xmlLines.append('<text style="text-anchor:%s" font-size="%f"  ><tspan x="%f" y="%f"  dy="%f" fill="%s">%s</tspan></text>' \
				% (anchor,fontsize,x,y,dy,c_color,outstr))

		self.countXlimits(x)
		self.countYlimits(y)
		

	def saveFile(self):
		if self.filename == None: return
		try:	
			ostr =  self.getXMLout()
			fd = open(self.filename,'w')
			fd.write(ostr)
			fd.close() 
		except:
			return

