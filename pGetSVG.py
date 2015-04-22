import os, sys, re
from   cgm2pdf import *
from pSVGout import *


html_svg_Holder="""
<html> 

<head>

</head> 
<body>
	<embed src="%(filename)s" width="199%%" height="199%%" align="center" />
</body>
</html>
"""


				
if __name__ == '__main__':
	if len(sys.argv) < 2: 
		print "Usage: prog inputfile [code] "
		print "code = 0 for Windows origin file"
		print "code = 1 for Unix origin file"
		sys.exit(0)

	filename = sys.argv[1]
	try:
		outputfilename = filename.replace('.cgm','.svg') 
	except:
		outputfilename = filename + ".svg"

	tagsfilename = outputfilename.replace(".svg",".txt") 
	htmlfilename = outputfilename.replace(".svg",".htm") 
	os_prelude = "<"
	if len(sys.argv) > 2: 
		if sys.argv[2] == '0': os_prelude = ">"

	print "SETTING PRELUDE TO %s" % os_prelude

	svgOut = SVGout()
	svgOut.flipY() 
	xx = cgmFileReader(cgmParameters(os_prelude))
	print "--------> ", filename, os_prelude
	xx.readFile(filename,outputfilename,xx,svg=1)  # writes to output file

	# ----------------------------------------------------------------
	# Create the tags file 
	# ----------------------------------------------------------------
	outstr= [filename,]
	b =  xx.textStrings 
	b.sort()
	outstr.append("\n".join(b))

	fd = open(tagsfilename,'w')
	fd.write("\n".join(outstr)) 
	fd.close() 
	
	dict = { 'filename':outputfilename,  } 
	fd = open(htmlfilename,'w')
	fd.write(html_svg_Holder % dict) 
	fd.close() 
	
	
