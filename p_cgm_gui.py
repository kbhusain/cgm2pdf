
import os, sys, re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui 
import guiCnvCGM
import subprocess 
from   cgm2pdf import *
from   pSVGout import *

class myForm(QMainWindow,guiCnvCGM.Ui_MainWindow):
	def __init__(self,parent=None):
		super(myForm,self).__init__(parent)
		self.setupUi(self)
		name =  os.getenv('USER')
		
	def on_pbQuit_released(self): sys.exit() 


	def on_pbGetCGM_released(self):
		self.fileDialog = QtGui.QFileDialog()
		inputfilename  = str(self.txtCGMname.text() ) 
		print "Input is " , inputfilename 
		if len(inputfilename) < 1: 
			dir = os.getenv("HOME")
		else: 
			dir = os.path.dirname(inputfilename) 
		print "Dir is " , dir
                filename = self.fileDialog.getOpenFileName(None,"CGM File", dir, "CGM files (*.cgm);;All (*)")
                if filename: 
			self.txtCGMname.setText(QString(filename))
			sfilename = filename.replace(".cgm",".svg") 
			self.txtSVGname.setText(QString(sfilename))
		self.fileDialog = None

		 
	def on_pbGetSVG_released(self): 
		self.fileDialog = QtGui.QFileDialog()
                dir = os.getenv("HOME")
                filename = self.fileDialog.getSaveFileName(None,"SVG File", dir, "SVG files (*.svg);;All (*)")
                if filename: 
			dir = str(self.fileDialog.directory().dirName()) 
			ifilename = str(filename) 
			f = ifilename.find(".svg")
			if f < 0: ifilename += ".svg" 
			self.txtSVGname.setText(QString(ifilename))
		self.fileDialog = None


	def on_pbConvert_released(self): 
		print "file to read",  
		# fd = subprocess.Popen( '/peasd/geolog/apps/cnvCGM/pGetSVG.py %s 0' % filename,  shell=True, stdout=subprocess.PIPE).stdout
		# qrep = fd.read() 
		inputfilename  = str(self.txtCGMname.text() ) 
		outputfilename = str(self.txtSVGname.text() ) 

		try: 
			fd =  open(outputfilename,'w') 
			close(fd) 
		except:
			outputfilename = os.getenv('HOME') + "/" +  os.path.basename(outputfilename) 
			self.txtSVGname.setText(QString(outputfilename))
		tagsfilename = outputfilename.replace(".svg",".txt") 
		htmlfilename = outputfilename.replace(".svg",".htm") 

		os_prelude = ">"                          # default Unix
		if self.checkBox.isChecked() : 
			os_prelude = "<"                  # Windows 
			print "SETTING PRELUDE TO %s" % os_prelude

		svgOut = SVGout()
		svgOut.flipY() 
		xx = cgmFileReader(cgmParameters(os_prelude))
		print "--------> ", inputfilename, os_prelude
		xx.readFile(inputfilename,outputfilename,xx,svg=1)  # writes to output file

		# ----------------------------------------------------------------
		# Create the tags file 
		# ----------------------------------------------------------------
		outstr= [inputfilename,]
		b =  xx.textStrings 
		b.sort()
		outstr.append("\n".join(b))
        	self.txtKeywords.setText("".join(outstr))

		fd = open(tagsfilename,'w')
		fd.write("\n".join(outstr)) 
		fd.close() 
	
		dict = { 'filename':outputfilename,  } 
		fd = open(htmlfilename,'w')
		fd.write(html_svg_Holder % dict) 
		fd.close() 
	

	def on_pbShowSVG_released(self): 
		of_file = self.txtSVGname.text() 
		print "file to show", of_file
		if os.fork(): 
			os.execle('/peasd/geolog/apps/cnvCGM/showSVG.bash', of_file, of_file, os.environ) 


	def on_pbSaveKeywords_released(self): 
		inputfilename  = str(self.txtCGMname.text() ) 
		try:
			dir = os.path.dirname(inputfilename) 
		except: 
			dir = os.geteng('HOME') 
                self.fileDialog = QtGui.QFileDialog()
                filename = self.fileDialog.getSaveFileName(None,"Save Keywords File",dir, "txt files (*.txt);;All (*)")
		# self.fileDialog = None
                if filename == None: return
                if len(filename)<1: return
                strOut = str(self.txtKeywords.toPlainText())
                fd = open(filename,'w')
                fd.write(strOut)
                fd.close()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	form = myForm()
	form.show()
	app.exec_()
