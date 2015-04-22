
import re , sys, os
def re_show(pat, s):
	print re.compile(pat,re.M).sub('{\g<0>}',s.rstrip()),'\n'

def re_grabword(pat,s): 
	return  re.compile(pat,re.M).match(s.rstrip())

pattern = '[A-Z][A-Z][A-Z][A-Z]_[0-9]+_[0-9]+' 

if __name__ == '__main__':
	xlines = open(sys.argv[1],'r').readlines() 
	for xl in xlines: 
		r = re_grabword(pattern,xl)  
		if r : print r.group(0)
		#re_show(pattern,xl)  
