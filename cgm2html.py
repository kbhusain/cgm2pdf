
# Python command parser file 
import os,sys , getopt, array, Image
from struct import *
from cgmdesc import *
from cgmbase import *
from cgmParsedOutput import cgmToHTML 



def usage():
	print "Usage: prog cgmfile [-f outputfile] [-c code] "
	print "code = 0 for Windows origin file"
	print "code = 1 for Unix origin file"
	print "outputfilename is 'tmp.pdf'  if not specified"




##
# 
class cgm2html(cgmFileReader):
	def __init__(self, usedefaults): 
		cgmFileReader.__init__(self,usedefaults) 
		self.outArray = "" 
	

	## 
	#
	def readFile(self,inputfilename,outputfile):
		self.pdfOut = cgmToHTML(outputfile); 
		fd = open (inputfilename,'rb')
		self.myrecords = [ ]
		i = 0
		for i in range(100000): 
			mb = cgmRecord(self.usedefaults,i)      # keep these in an arra
			self.myrecords.append(mb)
			r = xx.readRecord(fd,mb)
			if r == 0: break;
			i += 1;
		self.debugPrint('EOF at ', i, fd.tell())
		self.pdfOut.saveFile() 


				
if __name__ == '__main__':
	try:
		opts, alen = getopt.getopt(sys.argv[2:], 'c:f:') 
	except:
		usage()
		sys.exit(0)
	optin = {} 
	for k,v in opts: optin[k] = v 


	#--------------------------------- how to process 
	os_prelude = ">"
	code = optin.get('-c', '0')
	if code == '0': 
		os_prelude = ">"
	else:
		os_prelude = "<"

	#--------------------------------- where to write 
	outputfilename = optin.get('-f','tmp.html') 
	inputfilename  = sys.argv[1]

	#print "OPTS", opts, alen
	#print "Input  filename", inputfilename 
	#print "Output filename", outputfilename 
	#print "Output prelude ", os_prelude 

	#------------------------------------------------------------------------------
	# THE FOLLOWING ARE RESET WHEN PRECISION IS READ FROM HEADER
	#------------------------------------------------------------------------------
	xx = cgm2html(cgmParameters(os_prelude))
	xx.readFile(inputfilename,outputfilename)
	# ----------------------------------------------------------------
	# Create the tags file 
	# ----------------------------------------------------------------
	b =  xx.textStrings 
	b.sort()
	fd = open(outputfilename+".txt",'w')
	fd.write("\n".join(b)) 
	fd.close() 
	
	# ----------------------------------------------------------------
	# Create the html file 
	# ----------------------------------------------------------------
	
	print "Output filename", outputfilename 
	

