

import os, sys
from   cgm2pdf import *
from pSVGout import *
				
if __name__ == '__main__':
	if len(sys.argv) < 2: 
		print "Usage: prog dirname outputfilename [code] "
		print "code = 0 for Windows origin file"
		print "code = 1 for Unix origin file"
		sys.exit(0)

	dirname = sys.argv[1]
	try:
		outputfilename = sys.argv[2]; 
	except:
		outputfilename = 'catalog'

	os_prelude = "<"
	if len(sys.argv) > 3: 
		if sys.argv[3] == '0': os_prelude = ">"


	files  = os.listdir(dirname) 
	outstr = []

	for fn in files: 
		f = fn.find(".cgm") 
		if f < 0: continue
		fullname = dirname + os.sep + fn 
		svgOut = SVGout()
		svgOut.reverseYscale() 
		xx = cgmFileReader(cgmParameters(os_prelude))
		print "--------> ", fullname
		xx.readFile(fullname,svgOut,xx)
		# ----------------------------------------------------------------
		# Create the svg file  if you want it 
		# ----------------------------------------------------------------
		ostr =  svgOut.getXMLout()
		#fd = open(outputfilename+".svg",'w')
		#fd.write(outString)
		#fd.close() 

		# ----------------------------------------------------------------
		# Create the tags file 
		# ----------------------------------------------------------------
		outstr.append(fullname) 
		b =  xx.textStrings 
		b.sort()
		outstr.append("\n".join(b))

	fd = open(outputfilename,'w')
	fd.write("\n".join(outstr)) 
	fd.close() 
	
	
