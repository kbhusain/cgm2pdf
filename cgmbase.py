<<<<<<< HEAD

# Python command parser file 
import os,sys , getopt, array, Image
from struct import *
from cgmdesc import *

PIXELS_PER_INCH = 72

from cgmParsedOutput import cgmParsedOutputClass

class cgmParameters:
	def __init__(self,os_prelude):
		self.parameters = { }  
		self.os_prelude = os_prelude
		self.fmt_byteString  = "%sB" % (os_prelude)
		self.fmt_wordString  = "%sH" % (os_prelude)
		self.fmt_3i          = "%s3h" % (os_prelude)
		self.fmt_shortString = "%sh" % (os_prelude)
		self.fmt_floatString = "%sf" % (os_prelude)
		self.fmt_doubleString = "%sd" % (os_prelude)
		self.fmt_longString = "%sI" % (os_prelude)
		self.fmt_vbpString  = "ff" 
		self.fmt_bpString  = "f" 

		self.parameters['line_type'] = 0 
		self.parameters['rotate'] =  [0,0,0,0]
		self.parameters['stroke_dasharray'] = []
		self.parameters['scale_factor']     = 1.0;
		self.parameters['color_mode']       = 0;
		self.parameters['line_width_mode']  = 0;
		self.parameters['marker_size_mode'] = 0;
		self.parameters['edge_width_mode']  = 0;
		self.parameters['color_background'] = [ 255,255,255 ]
		self.parameters['color_fill']       = [ 255,255,255 ] 
		self.parameters['color_edge']       = [ 0,0,0]
 		self.parameters['color_line']       = [0,0,100] 
		self.parameters['color_text']       = [8,8,8]
		self.parameters['line_width']       = 0.01 
		self.parameters['char_height']      = 0.1 
		self.parameters['precision_integer']  = 0; 
		self.parameters['precision_of_index']  = 0; 
		self.parameters['precision_of_color']  = 0; 
		self.parameters['precision_of_color_index']  = 0; 
		self.parameters['max_color_index']  = 255; 
		self.parameters['char_set_list'] =  ''
		self.parameters['precision_of_name'] = 8
		self.parameters['char_coding']  = 1 
		self.parameters['vdc_integer']  = 0 
		self.parameters['vdc_realprec'] = 4
		self.parameters['vdc_p1']       = 0   
		self.parameters['vdc_p2']       = 9   
		self.parameters['vdc_p3']       = 23   
		self.parameters['vdc_intprec']  = 2
		self.parameters['enum_prec']    = 2;
		self.parameters['rgb_p1']       = 0;   
		self.parameters['rgb_p2']       = 16;   
		self.parameters['rgb_p3']       = 16;   
		self.parameters['fonts_list']   = ''
		self.parameters['clip_indicator'] = 0
		self.parameters['vdc_type'] = 0
		self.parameters['font_size'] = 10;
		self.parameters['font_style'] = 'normal';
		self.parameters['font_weight'] = 'normal';
		self.parameters['text_anchor'] = "start"
		self.parameters['horizontal_alignment'] = 0
		self.parameters['vertical_alignment'] = 0
		self.parameters['edge_width']   = 1
		self.parameters['fill_style']   = "none"
		self.parameters['edge_visible'] =  1
		self.parameters['pattern_index'] =  0


class cgmRecord: 
	def __init__(self,usedefaults,id=0,os_prelude = '>'):
		self.cmd = None
		self.ID =id
		self.elementClass = None
		self.elementID=None
		self.parameters = ''
		self.parmslen = 0
		self.morePartitions = 0
		self.padding  = 0
		self.opcodes = None # Could include drawing primitives, etc. 
		self.usedefaults = usedefaults 
		self.debugOn = 0

	def debugPrint(self,*args): 
		if self.debugOn == 1: print args 	

	def rawdebugPrint(self,*args): 
		if self.debugOn == 2: print args 	


	def readCommand(self,fd):
		#self.debugPrint( "At [ %04x ] " %  fd.tell())
		buf = fd.read(2)                      # At location!
		cmd = unpack(self.usedefaults.fmt_wordString,buf)[0]   # I am using a global, yuck.
		self.cmd = cmd                        # Copy of the local 
		self.elementClass = (cmd >> 12) & 0xF;       # Get CLASS 
		self.elementID    = (cmd >> 5) & 0x7f;       # Element 
		self.parmslen 	  = cmd & 0x1f;              # Length of parameters.
		if self.parmslen == 31:
			p   = self.readInt(fd)           # -------------------------------------------
			self.padding  = p & 0x0001 
			self.parmslen = p & 0x7FFF
			self.morePartitions = p & 0x8000
		if self.morePartitions == 0: 
			self.padding = self.parmslen & 1;
		else:
			self.padding = 0


	def readNextPartition(self,fd):
		p   = self.readInt(fd)           # -------------------------------------------
		parmslen = p & 0x7FFF
		#self.debugPrint("READING NEXT PARTITION LENGTH %04x" % p, "%04x" % fd.tell())
		#self.debugPrint("READING PADDING    >>>>>", self.padding  )
		#self.debugPrint("READING LEN    >>>>>", parmslen )
		morePartitions = p & 0x8000
		#self.debugPrint("READING MORE?    >>>>>", morePartitions  )
		b = fd.read(parmslen)
		self.buffer += b
		if self.morePartitions == 0: 
			self.padding = fd.tell() & 1;
		return morePartitions;


	def readParameters(self,fd):
		#self.debugPrint("Reading [", self.parmslen, "]" )
		self.parameters = fd.read(self.parmslen)
		
	def readCGMstring(self,fd,ilen=0):
		if ilen == 0: 
			buf = fd.read(1)                     # Get segment length
			slen = unpack(self.usedefaults.fmt_byteString,buf)[0] # 
		else:
			slen = ilen
		#self.debugPrint("-->Reading ", slen, " bytes", ilen  )
		self.buffer = fd.read(slen)
		if (self.morePartitions): 
			while 1:
				more = self.readNextPartition(fd)   
				if more == 0: break

	def readFloat(self,fd): 
		#self.debugPrint("READING FLOAT at", fd.tell())
		if (self.usedefaults.parameters['vdc_p3'] == 23): 
			buf = fd.read(4)                     # Get segment lengthbb
			return unpack(self.usedefaults.fmt_floatString,buf)[0]
		if (self.usedefaults.parameters['vdc_p3'] == 52): 
			buf = fd.read(8)                     # Get segment lengthbb
			return unpack(self.usedefaults.fmt_doubleString,buf)[0]
		if (self.usedefaults.parameters['vdc_p3'] == 16): 
			buf = fd.read(4)                     # Get segment lengthbb
			i = unpack(self.usedefaults.fmt_longString,buf)[0]
			return float(i) /0x00010000; 
		if (self.usedefaults.parameters['vdc_p3'] == 32): 
			buf = fd.read(8)                     # Get segment lengthbb
			i = unpack(self.usedefaults.fmt_doubleString,buf)[0]
			return double(i) /0x01000000; 
		return 0.0 	

	def readByte(self,fd): 
		buf = fd.read(1)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_byteString,buf)[0]
	
	def readInt(self,fd): 
		buf = fd.read(2)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_wordString,buf)[0]
		
	def readIntTriple(self,fd): 
		buf = fd.read(6)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_3i,buf)
		
	def showInfo(self):
		istr = "CMD:%04x Class:%x ID:%X (%d) LN:%d Pad:%04x Partition:%04x" % (self.cmd,self.elementClass,self.elementID,self.elementID, self.parmslen, self.padding, self.morePartitions)
		self.rawdebugPrint(istr)
		
class cgmFileReader:
	def __init__(self,usedefaults):
		self.usedefaults = usedefaults
		self.cmd   = None
		self.imageId = 1
	
		# These are primitives that you have to translate into drawing 
		# commands for SVG other packages
		#
		# Format:  keyword:  parameters 
		# 
		self.primitives = [] 
		self.textStrings = [] 
		
		# Some defaults:

		#------------------------------------- ONLY STANDARD DEFINITIONS PLEASE 
		self.cgm_class0 = { }
		self.cgm_class0[0]  = self.c0_00
		self.cgm_class0[1]  = self.c0_01
		self.cgm_class0[2]  = self.c0_02
		self.cgm_class0[3]  = self.c0_03
		self.cgm_class0[4]  = self.c0_04
		self.cgm_class0[5]  = self.c0_05
		self.cgm_class0[6]  = self.c0_06
		self.cgm_class0[7]  = self.c0_07
		self.cgm_class0[8]  = self.c0_08
		self.cgm_class0[9]  = self.c0_09
		self.cgm_class0[13]  = self.c0_13
		self.cgm_class0[14]  = self.c0_14
		self.cgm_class0[15]  = self.c0_15
		self.cgm_class0[16]  = self.c0_16
		self.cgm_class0[17]  = self.c0_17
		self.cgm_class0[18]  = self.c0_18
		self.cgm_class0[19]  = self.c0_19
		self.cgm_class0[20]  = self.c0_20
		self.cgm_class0[21]  = self.c0_21
		self.cgm_class0[22]  = self.c0_22
		self.cgm_class0[23]  = self.c0_23
		
		
		self.cgm_class1 = {}
		self.cgm_class1[1] = self.c1_01 
		self.cgm_class1[2] = self.c1_02 
		self.cgm_class1[3] = self.c1_03 
		self.cgm_class1[4] = self.c1_04 
		self.cgm_class1[5] = self.c1_05 
		self.cgm_class1[6] = self.c1_06 
		self.cgm_class1[7] = self.c1_07 
		self.cgm_class1[8] = self.c1_08 
		self.cgm_class1[9] = self.c1_09 
		self.cgm_class1[10] = self.c1_10 
		self.cgm_class1[11] = self.c1_11 
		self.cgm_class1[12] = self.c1_12 
		self.cgm_class1[13] = self.c1_13 
		self.cgm_class1[14] = self.c1_14 
		self.cgm_class1[15] = self.c1_15 
		self.cgm_class1[16] = self.c1_16 
		self.cgm_class1[17] = self.c1_17 
		self.cgm_class1[18] = self.c1_18 
		self.cgm_class1[19] = self.c1_19 
		self.cgm_class1[20] = self.c1_20 
		self.cgm_class1[21] = self.c1_21 
		self.cgm_class1[22] = self.c1_22 
		self.cgm_class1[23] = self.c1_23 
		self.cgm_class1[24] = self.c1_24 
		
		self.cgm_class2 = {}
		self.cgm_class2[1] = self.c2_01_scalingMode
		self.cgm_class2[2] = self.c2_02_colorSelectionMode
		self.cgm_class2[3] = self.c2_03_lineWidthSpecMode
		self.cgm_class2[4] = self.c2_04_markerSizeSpecMode
		self.cgm_class2[5] = self.c2_05_edgeWidthMode
		self.cgm_class2[6] = self.c2_06_vdcExtent
		self.cgm_class2[7] = self.c2_07_backgroundColor
		self.cgm_class2[8] = self.c2_08_deviceViewport
		self.cgm_class2[9] = self.c2_09_deviceViewportSpecMode
		self.cgm_class2[10] = self.c2_10_deviceViewportMapping
		self.cgm_class2[11] = self.c2_11_lineRepresentation
		self.cgm_class2[12] = self.c2_12_markerRepresentation
		self.cgm_class2[13] = self.c2_13_textRepresentation
		self.cgm_class2[14] = self.c2_14_fillRepresentation
		self.cgm_class2[15] = self.c2_15_edgeRepresentation
		self.cgm_class2[16] = self.c2_16_interiorStyleMode
		self.cgm_class2[17] = self.c2_17_lineEdgeType
		self.cgm_class2[18] = self.c2_18_hatchStyle
		self.cgm_class2[19] = self.c2_19_geometricPattern
		self.cgm_class2[20] = self.c2_20_applicationStructure
		self.cgm_class2[81] = self.c2_81
		
		 
		self.cgm_class3 = {}
		self.cgm_class3[1] = self.c3_01 
		self.cgm_class3[2] = self.c3_02 
		self.cgm_class3[3] = self.c3_03 
		self.cgm_class3[4] = self.c3_04 
		self.cgm_class3[5] = self.c3_05 
		self.cgm_class3[6] = self.c3_06 
		self.cgm_class3[7] = self.c3_07 
		self.cgm_class3[8] = self.c3_08 
		self.cgm_class3[9] = self.c3_09 
		self.cgm_class3[10] = self.c3_10 
		self.cgm_class3[11] = self.c3_11 
		self.cgm_class3[12] = self.c3_12 
		self.cgm_class3[13] = self.c3_13 
		self.cgm_class3[14] = self.c3_14 
		self.cgm_class3[15] = self.c3_15 
		self.cgm_class3[16] = self.c3_16 
		self.cgm_class3[17] = self.c3_17 
		self.cgm_class3[18] = self.c3_18 
		self.cgm_class3[19] = self.c3_19 
		self.cgm_class3[20] = self.c3_20 
		self.cgm_class3[21] = self.c3_21 
		self.cgm_class3[22] = self.c3_22 
		self.cgm_class3[74] = self.c3_74 
		self.cgm_class3[78] = self.c3_78 
		self.cgm_class3[83] = self.c3_83 
		self.cgm_class3[115] = self.c3_115 
	
		self.cgm_class4 = {}
		self.cgm_class4[1] = self.c4_01 
		self.cgm_class4[2] = self.c4_02 
		self.cgm_class4[3] = self.c4_03 
		self.cgm_class4[4] = self.c4_04 
		self.cgm_class4[5] = self.c4_05 
		self.cgm_class4[6] = self.c4_06 
		self.cgm_class4[7] = self.c4_07 
		self.cgm_class4[8] = self.c4_08 
		self.cgm_class4[9] = self.c4_09 
		self.cgm_class4[10] = self.c4_10 
		self.cgm_class4[11] = self.c4_11 
		self.cgm_class4[12] = self.c4_12 
		self.cgm_class4[13] = self.c4_13 
		self.cgm_class4[14] = self.c4_14 
		self.cgm_class4[15] = self.c4_15 
		self.cgm_class4[16] = self.c4_16 
		self.cgm_class4[17] = self.c4_17 
		self.cgm_class4[18] = self.c4_18 
		self.cgm_class4[19] = self.c4_19 
		self.cgm_class4[20] = self.c4_20 
		self.cgm_class4[21] = self.c4_21 
		self.cgm_class4[22] = self.c4_22 
		self.cgm_class4[23] = self.c4_23 
		self.cgm_class4[24] = self.c4_24 
		self.cgm_class4[25] = self.c4_25 
		self.cgm_class4[26] = self.c4_26 
		self.cgm_class4[27] = self.c4_27 
		self.cgm_class4[28] = self.c4_28 
		self.cgm_class4[29] = self.c4_29 

		self.cgm_class5 = {}
		self.cgm_class5[1] = self.c5_01 
		self.cgm_class5[2] = self.c5_02 
		self.cgm_class5[3] = self.c5_03 
		self.cgm_class5[4] = self.c5_04 
		self.cgm_class5[5] = self.c5_05 
		self.cgm_class5[6] = self.c5_06 
		self.cgm_class5[7] = self.c5_07 
		self.cgm_class5[8] = self.c5_08 
		self.cgm_class5[9] = self.c5_09 
		self.cgm_class5[10] = self.c5_10 
		self.cgm_class5[11] = self.c5_11 
		self.cgm_class5[12] = self.c5_12 
		self.cgm_class5[13] = self.c5_13 
		self.cgm_class5[14] = self.c5_14 
		self.cgm_class5[15] = self.c5_15 
		self.cgm_class5[16] = self.c5_16 
		self.cgm_class5[17] = self.c5_17 
		self.cgm_class5[18] = self.c5_18 
		self.cgm_class5[19] = self.c5_19 
		self.cgm_class5[20] = self.c5_20 
		self.cgm_class5[21] = self.c5_21 
		self.cgm_class5[22] = self.c5_22 
		self.cgm_class5[23] = self.c5_23 
		self.cgm_class5[24] = self.c5_24 
		self.cgm_class5[25] = self.c5_25 
		self.cgm_class5[26] = self.c5_26 
		self.cgm_class5[27] = self.c5_27 
		self.cgm_class5[28] = self.c5_28 
		self.cgm_class5[29] = self.c5_29 
		self.cgm_class5[30] = self.c5_30 
		self.cgm_class5[31] = self.c5_31 
		self.cgm_class5[32] = self.c5_32 
		self.cgm_class5[33] = self.c5_33 
		self.cgm_class5[34] = self.c5_34 
		self.cgm_class5[35] = self.c5_35 
		self.cgm_class5[36] = self.c5_36 
		self.cgm_class5[37] = self.c5_37 
		self.cgm_class5[38] = self.c5_38 
		self.cgm_class5[39] = self.c5_39 
		self.cgm_class5[40] = self.c5_40 
		self.cgm_class5[41] = self.c5_41 
		self.cgm_class5[42] = self.c5_42 
		self.cgm_class5[43] = self.c5_43 
		self.cgm_class5[44] = self.c5_44 
		self.cgm_class5[45] = self.c5_45 
		self.cgm_class5[46] = self.c5_46 
		self.cgm_class5[47] = self.c5_47 
		self.cgm_class5[48] = self.c5_48 
		self.cgm_class5[49] = self.c5_49 
		self.cgm_class5[50] = self.c5_50 
		self.cgm_class5[51] = self.c5_51 
		self.cgm_class5[83] = self.c5_83 
		self.cgm_class5[99] = self.c5_99 
		self.cgm_class5[123] = self.c5_123 

		self.cgm_class6 = {}
		self.cgm_class6[1] = self.c6_01 
		self.cgm_class6[13] = self.c6_13 
                self.cgm_class6[10] = self.c6_10
		self.cgm_class6[43] = self.c6_43 
		self.cgm_class6[48] = self.c6_48 
		self.cgm_class6[59] = self.c6_59 
		self.cgm_class6[67] = self.c6_67 
		self.cgm_class6[72] = self.c6_72 
		self.cgm_class6[75] = self.c6_75 
		self.cgm_class6[99] = self.c6_99 
		self.cgm_class6[112] = self.c6_112 

		self.cgm_class7 = {}
		self.cgm_class7[1] = self.c7_01 
		self.cgm_class7[2] = self.c7_02 
		self.cgm_class7[3] = self.c7_03 
		self.cgm_class7[27] = self.c7_27 
		self.cgm_class7[35] = self.c7_35 
                self.cgm_class7[51] = self.c7_51



		self.cgm_class8 = {}
                self.cgm_class8[25] = self.c8_25

		self.cgm_class8[50] = self.c8_50
		self.cgm_class8[97] = self.c8_97
		self.cgm_class8[108] = self.c8_108

		self.cgm_class9 = {}
                self.cgm_class9[87] = self.c9_87

		self.cgm_class10 = {}
		self.cgm_class10[121] = self.c10_121

		self.cgm_class11 = {}

		self.cgm_class12 = {}
		self.cgm_class12[1] = self.c12_1 
		self.cgm_class12[2] = self.c12_2 
		self.cgm_class12[3] = self.c12_3 
		self.cgm_class12[4] = self.c12_4 
		self.cgm_class12[5] = self.c12_5 

		self.cgm_class13 = {}
                self.cgm_class13[9] = self.c13_9
		self.cgm_class13[97] = self.c13_97

		self.cgm_class14 = {}
		self.cgm_class15 = {}
		self.cgm_class15[78] = self.c15_78 
		self.cgm_class15[105] = self.c15_105
		self.cgm_class15[120] = self.c15_120 

		self.cgm_classes = { }
		self.cgm_classes[0] = self.cgm_class0
		self.cgm_classes[1] = self.cgm_class1
		self.cgm_classes[2] = self.cgm_class2
		self.cgm_classes[3] = self.cgm_class3
		self.cgm_classes[4] = self.cgm_class4
		self.cgm_classes[5] = self.cgm_class5
		self.cgm_classes[6] = self.cgm_class6
		self.cgm_classes[7] = self.cgm_class7
		self.cgm_classes[8] = self.cgm_class8
		self.cgm_classes[9] = self.cgm_class9
		self.cgm_classes[10] = self.cgm_class10
		self.cgm_classes[11] = self.cgm_class11
		self.cgm_classes[12] = self.cgm_class12
		self.cgm_classes[13] = self.cgm_class13
		self.cgm_classes[14] = self.cgm_class14
		self.cgm_classes[15] = self.cgm_class15
		self.pdfOut = None; 
		self.debugLevel = 0

	def debugPrint(self,*args): 
		if self.debugLevel > 0: print args 	

	##
	# You MUST override this function 
	def readFile(self,inputfilename,outputfile):
		self.pdfOut = cgmParsedOutputClass(outputfile); 
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

	# --------------- CLASS 0 Functions --------------------------------
	def c0_00(self,record,fd): pass 
	def c0_01(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_02(self,record,fd): pass
	def c0_03(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
		self.debugPrint("Picture Name:", record.buffer )
	def c0_04(self,record,fd): pass 
	def c0_05(self,record,fd): pass 
	def c0_06(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_07(self,record,fd): pass 
	def c0_08(self,record,fd): pass 
	def c0_09(self,record,fd): pass 
	def c0_13(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
		p1 = record.readInt(fd); 
	def c0_14(self,record,fd): pass 
	def c0_15(self,record,fd): pass 
	def c0_16(self,record,fd): pass 
	def c0_17(self,record,fd): pass 
	def c0_18(self,record,fd): pass 
	def c0_19(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
	 	record.readInt(fd)
	def c0_20(self,record,fd): pass
	def c0_21(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
	def c0_22(self,record,fd): pass
	def c0_23(self,record,fd): pass
	def c0_59(self,record,fd):  self.dummyReader(fd,record)
	
	# --------------- CLASS 1 Functions --------------------------------
	# When you read these definitions, you can try to comprehend how 
	# to read the coordinates. 
	#--------------------------------------------------------------
	def c1_01(self,record,fd): 
		record.readParameters(fd)
	def c1_02(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
		record.readCGMstring(fd)
		self.primitives.append("Description: " + "".join(record.buffer))
	
	def c1_03(self,record,fd): 
		self.usedefaults.parameters['vdc_type'] = record.readInt(fd)
	def c1_04(self,record,fd): self.usedefaults.precision_integer = record.readInt(fd)
	def c1_05(self,record,fd):  
		self.usedefaults.vdc_p1, self.usedefaults.vdc_p2, self.usedefaults.vdc_p3 = record.readIntTriple(fd)   
		self.debugPrint("PRECISION", self.usedefaults.vdc_p1, self.usedefaults.vdc_p2, self.usedefaults.vdc_p3 )
		if self.usedefaults.parameters['vdc_p1'] == 0: 
			if self.usedefaults.parameters['vdc_p2'] == 9  and self.usedefaults.parameters['vdc_p3'] == 23: 
				self.usedefaults.fmt_vbpString  = "ff" 
				self.usedefaults.fmt_bpString  = "f" 
			if self.usedefaults.parameters['vdc_p2'] == 12 and self.usedefaults.parameters['vdc_p3'] == 52: 
				self.usedefaults.fmt_vbpString  = "dd" 
				self.usedefaults.fmt_bpString  = "d" 
		else:
			if self.usedefaults.parameters['vdc_p2'] == 16  and self.usedefaults.parameters['vdc_p3'] == 16: 
				self.usedefaults.fmt_vbpString  = "HH" 
				self.usedefaults.fmt_bpString  = "H" 
			if self.usedefaults.parameters['vdc_p2'] == 32  and self.usedefaults.parameters['vdc_p3'] == 32: 
				self.usedefaults.fmt_vbpString  = "II" 
				self.usedefaults.fmt_bpString  = "I" 
			
	def c1_06(self,record,fd): self.usedefaults.parameters['precision_of_index'] = record.readInt(fd)
	def c1_07 (self,record,fd): self.usedefaults.parameters['precision_of_color'] = record.readInt(fd)
	def c1_08(self,record,fd): self.usedefaults.parameters['precision_of_color_index'] = record.readInt(fd)
	def c1_09 (self,record,fd): 
		self.usedefaults.parameters['max_color_index'] = record.readByte(fd)
		self.debugPrint("Color Index ", self.usedefaults.parameters['max_color_index'] )
	def c1_10 (self,record,fd): 
		if record.parmslen == 6: 
			self.usedefaults.parameters['rgb_p1'], self.usedefaults.parameters['rgb_p2'], self.usedefaults.parameters['rgb_p3'] = record.readIntTriple(fd)   
		if record.parmslen == 4: 
			self.usedefaults.parameters['rgb_p1']  = record.readInt(fd)   
			self.usedefaults.parameters['rgb_p2']  = record.readInt(fd)   
			self.usedefaults.parameters['rgb_p3']  = 0
	def c1_11 (self,record,fd):  # C
		p1,p2,p3 = record.readIntTriple(fd)   
		self.debugPrint("Elements List=", p1,p2,p3)
	def c1_12(self,record,fd):  # D
		#self.debugPrint("metaFileElements", record.elementClass,record.elementID, record.parmslen
		itemCounts = record.parmslen/2 
		for x in range(itemCounts): 
			p1  = record.readInt(fd)   
			self.debugPrint("%04x" % p1,)
			self.debugPrint(" " )
	
	def c1_13(self,record,fd): 
		self.debugPrint("Font list", record.elementClass,record.elementID, record.parmslen)
		self.usedefaults.parameters['fonts_list'] = record.readCGMstring(fd,record.parmslen)
	def c1_14(self,record,fd): 
		self.usedefaults.parameters['char_set_list'] = record.readCGMstring(fd,record.parmslen)
	def c1_15(self,record,fd): self.usedefaults.parameters['char_coding']  = record.readInt(fd)   
	def c1_16(self,record,fd): self.usedefaults.parameters['precision_of_name']  = record.readInt(fd)   
	def c1_17(self,record,fd): 
		#self.primitives.append("max_vdc_extent: "+ record.elementClass,record.elementID + " " +  record.parmslen)
		pass
	def c1_18(self,record,fd):
		self.debugPrint("seg priority extent", record.elementClass,record.elementID, record.parmslen)
	def c1_19(self,record,fd): 
		self.debugPrint("color model", record.elementClass,record.elementID, record.parmslen)
	def c1_20(self,record,fd):
		self.debugPrint("color calibration", record.elementClass,record.elementID, record.parmslen)
	def c1_21(self,record,fd): 
		self.debugPrint("font properties", record.elementClass,record.elementID, record.parmslen)
	def c1_22(self,record,fd): 
		self.debugPrint("glyph Mappging", record.elementClass,record.elementID, record.parmslen)
	def c1_23(self,record,fd):
		self.debugPrint("symbol library", record.elementClass,record.elementID, record.parmslen)
	def c1_24(self,record,fd): 
		self.debugPrint("picture directory", record.elementClass,record.elementID, record.parmslen)
		
	# --------------- CLASS 2 Functions --------------------------------
	def c2_01_scalingMode(self,record,fd): 
		self.debugPrint("Scaling Mode: "  , record.readInt(fd))    # Actually, read in the points for the VDC 
		self.usedefaults.parameters['scale_factor'] = record.readFloat(fd)    # Actually, read in the points for the VDC 
		self.debugPrint("Scaling Metric: ", self.usedefaults.parameters['scale_factor'] )
	def c2_02_colorSelectionMode(self,record,fd): 
		self.usedefaults.parameters['color_mode'] = record.readInt(fd)   
		self.debugPrint("Color Mode: ", self.usedefaults.parameters['color_mode'] )
	def c2_03_lineWidthSpecMode(self,record,fd): 
		self.usedefaults.parameters['line_width_mode'] = record.readInt(fd)   
		self.debugPrint("Line Width MODE: ", self.usedefaults.parameters['line_width_mode'] )
	def c2_04_markerSizeSpecMode(self,record,fd): 
		self.usedefaults.parameters['marker_size_mode'] = record.readInt(fd)   
		self.debugPrint("Marker Size Mode: ", self.usedefaults.parameters['marker_size_mode'] )
	def c2_05_edgeWidthMode(self,record,fd): 
		self.usedefaults.parameters['edge_width_mode'] = record.readInt(fd)   
		self.debugPrint("Edge Width Mode: ", self.usedefaults.parameters['edge_width_mode'] )
	def c2_06_vdcExtent(self,record,fd):
		self.debugPrint("VDC extent = ", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 4; 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		self.debugPrint("VDC extents, ", x1,y1,x2,y2)

	def c2_07_backgroundColor(self,record,fd): 
		self.debugPrint("Background = ", record.elementClass,record.elementID, record.parmslen)
		r = record.readByte(fd)   
		g = record.readByte(fd)   
		b = record.readByte(fd)   
		self.usedefaults.parameters['color_background'] = [r,g,b]
		self.debugPrint(self.usedefaults.parameters['color_background'])
	def c2_08_deviceViewport(self,record,fd): 
		self.debugPrint("Device ViewPort = ", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 4; 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		self.debugPrint("Viewport extents, ", x1,y1,x2,y2)
		self.usedefaults.parameters['viewport_extents'] = [x1,y1,x2,y2]

	def c2_09_deviceViewportSpecMode(self,record,fd): self.dummyReader(fd,record)
	def c2_10_deviceViewportMapping(self,record,fd): self.dummyReader(fd,record)
	def c2_11_lineRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_12_markerRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_13_textRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_14_fillRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_15_edgeRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_16_interiorStyleMode(self,record,fd): self.dummyReader(fd,record)
	def c2_17_lineEdgeType(self,record,fd): self.dummyReader(fd,record)
	def c2_18_hatchStyle(self,record,fd): self.dummyReader(fd,record)
	def c2_19_geometricPattern(self,record,fd): self.dummyReader(fd,record)
	
	def c2_20_applicationStructure(self,record,fd): 
		self.debugPrint("c2_20", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   

	def c2_81(self,record,fd):  self.dummyReader(fd,record)

	def c3_01(self,record,fd): 
		self.dummyReader(fd,record)
	def c3_02(self,record,fd): 
		self.debugPrint("c3_02", record.elementClass,record.elementID, record.parmslen)
		if record.parmslen > 0: 
			self.usedefaults.parameters['vdc_p1'], self.usedefaults.parameters['vdc_p2'], self.usedefaults.parameters['vdc_p3'] = record.readIntTriple(fd)   
	
	def c3_03(self,record,fd):
		self.dummyReader(fd,record)
	def c3_04(self,record,fd):
		self.dummyReader(fd,record)
	def c3_05(self,record,fd):
		self.debugPrint("c3_05", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   
	def c3_06(self,record,fd): self.clip_indicator =  record.readInt(fd)   
	def c3_07(self,record,fd): self.dummyReader(fd,record)
	def c3_08(self,record,fd): self.dummyReader(fd,record)
	def c3_09(self,record,fd): self.dummyReader(fd,record)
	def c3_10(self,record,fd): self.dummyReader(fd,record)
	def c3_11(self,record,fd): self.dummyReader(fd,record)
	def c3_12(self,record,fd): self.dummyReader(fd,record)
	def c3_13(self,record,fd): self.dummyReader(fd,record)
	def c3_14(self,record,fd): self.dummyReader(fd,record)
	def c3_15(self,record,fd): self.dummyReader(fd,record)
	def c3_16(self,record,fd): self.dummyReader(fd,record)
	def c3_17(self,record,fd): self.dummyReader(fd,record)
	def c3_18(self,record,fd): self.dummyReader(fd,record)
	def c3_19(self,record,fd): self.dummyReader(fd,record)
	def c3_20(self,record,fd): self.dummyReader(fd,record)
	def c3_21(self,record,fd): self.dummyReader(fd,record)
	def c3_22(self,record,fd): 
		self.debugPrint("c3_22", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )
	def c3_74(self,record,fd): 
		self.debugPrint("c3_74", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )
	def c3_78(self,record,fd): 
		self.debugPrint("c3_78", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )

	def c3_83(self,record,fd):  self.dummyReader(fd,record)

	def c3_115(self,record,fd): 
		self.debugPrint("c3_115", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )

	# --------------- CLASS 4 Functions --------------------------------
	def c4_01(self,record,fd): 
		self.dummyReader(fd,record)                  # Read the record.
		sz = len(record.buffer)/4
		usefmt  = "%s%d%s" % (self.usedefaults.os_prelude, sz, self.usedefaults.fmt_bpString)
		upoints = unpack(usefmt,record.buffer[:sz*4])  # Get the length
		if len(upoints) >= 16: 
			self.debugPrint("POLYLINE format", usefmt, sz, sz*4, len(record.buffer), self.usedefaults.parameters['color_line'], )
		#sw        = self.usedefaults.parameters['line_width']
		fill_style    = self.usedefaults.parameters['fill_style']
		sw            = self.usedefaults.parameters['line_width'] 
		color_line    = self.usedefaults.parameters['color_line']
		color_fill=self.usedefaults.parameters['color_fill'] 
		color_edge=self.usedefaults.parameters['color_edge'] 
		edge_visible =self.usedefaults.parameters['edge_visible'] 
		#print "Edge Visible  Mode: ", self.usedefaults.parameters['edge_visible'] 
		self.debugPrint("C4_01 :", sw, color_line, color_fill, color_edge) 
		#if len(upoints) >= 500: print "LONG POLYGON", color_line, color_fill, color_edge, sw, len(upoints) 
		self.debugPrint("C4_01 :", sw, len(upoints), fill_style, color_line, color_fill, color_edge ) 
		self.pdfOut.addPolyLine(polygon=0, stroke=color_line, strokewidth=sw, points=upoints,	edge_visible = edge_visible, 
				color_fill = "none",  strokedasharray=self.usedefaults.parameters['stroke_dasharray']);

	def c4_02(self,record,fd): self.dummyReader(fd,record)
	def c4_03(self,record,fd): self.dummyReader(fd,record)

	def c4_04(self,record,fd): 
		self.dummyReader(fd,record)
		fmt1 = "%s%sHB" % (self.usedefaults.os_prelude,self.usedefaults.fmt_vbpString)
		sz = calcsize(fmt1)  
		usefmt  = "%s%sHB%ds" % (self.usedefaults.os_prelude, self.usedefaults.fmt_vbpString, len(record.buffer) - sz)
		x,y,e,c,s =  unpack(usefmt,record.buffer)  # Get the length
		fsz = int( PIXELS_PER_INCH  * self.usedefaults.parameters['char_height'])   # Pixels per inch  - DEBUG ONLY
		self.debugPrint("CGM TEXT:", x,y,e,c,s)
		ou_s = "%f:%f:%s " % ( x,y,s )
		if not ou_s in self.textStrings: self.textStrings.append(ou_s) 
		#self.debugPrint("Fsz %d " % fsz + " char height " +  str(self.usedefaults.parameters['char_height']))
		# ----------------------------------------------------------------------------------------
		# Determine
		# ----------------------------------------------------------------------------------------
		self.fontsize = fsz * 5   
		self.pdfOut.addTextTag(x,y,s,
				anchor=self.usedefaults.parameters['text_anchor'], 
				color=self.usedefaults.parameters['color_text'],
				units="in", 
				verticalAlignment=self.vertical_alignment,
				fontsize=self.usedefaults.parameters['char_height'],
				horizontalAlignment=self.horizontal_alignment,
				matrix=self.usedefaults.parameters['rotate'])
		
	def c4_05(self,record,fd): self.dummyReader(fd,record)
	def c4_06(self,record,fd): self.dummyReader(fd,record)
	def c4_07(self,record,fd): 
		self.dummyReader(fd,record)                  # Read the record.
		sz = len(record.buffer)/4                    # Get the number of floats 
		usefmt  = "%s%d%s" % (self.usedefaults.os_prelude, sz, self.usedefaults.fmt_bpString) 
		upoints = unpack(usefmt,record.buffer[:sz*4])  # Get the length

		if self.usedefaults.parameters['edge_visible']: 
			sw=self.usedefaults.parameters['edge_width'] 
		else: 
			sw=self.usedefaults.parameters['line_width']

		edge_visible =  self.usedefaults.parameters['edge_visible']
		fill_style=self.usedefaults.parameters['fill_style']
		color_line=self.usedefaults.parameters['color_line']
		color_fill=self.usedefaults.parameters['color_fill'] 
		color_edge=self.usedefaults.parameters['color_edge'] 
		edge_visible=self.usedefaults.parameters['edge_visible'] 
		self.debugPrint("C4_07 :", sw, len(upoints), fill_style, color_line, color_fill, color_edge , edge_visible) 
		# if len(upoints) >= 500: print "FILLED POLYGON", color_line, color_fill, color_edge, sw
		self.pdfOut.addPolyLine(polygon=1, stroke=color_line, strokewidth=sw, points=upoints,
				fill_style=fill_style,edge_visible = edge_visible, 
				color_fill = color_fill,  strokedasharray=self.usedefaults.parameters['stroke_dasharray']);
		#self.pdfOut.addPolyLine(polygon=1,stroke=self.usedefaults.parameters['color_line'],
			#color_fill=self.usedefaults.parameters['color_fill'], strokewidth=sw, points=upoints);

	def c4_08(self,record,fd): self.dummyReader(fd,record)
	def c4_09(self,record,fd): 
		self.dummyReader(fd,record)
		usefmt = "%s6f3H" % self.usedefaults.os_prelude 
		upoints = unpack(usefmt,record.buffer[:30])  # Get the length
		inx  = 32 
		bufferlen = len(record.buffer)
		rlen_fmt = "%sH" % self.usedefaults.os_prelude 
		color_fmt = "%s3B" % self.usedefaults.os_prelude 
		#print "c4_09", len(record.buffer) , upoints
		ncols = upoints[6]                   # Number of columns
		ncols3 = ncols * 3                   # Number of RGB triplets per row
		nrows = upoints[7] 	             # Number of rows 
		row = 0                              # First row.
		imageData = array.array('B')         # Array of integers. ?? 
		rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0]  #  Get the first run length 
		inx += 2 
		for row in xrange(nrows):            # 
			rowdata = [] 
			col     = 0 
			while col < ncols3: 
				#----------------------------------------------------------------
				r,g,b = unpack(color_fmt,record.buffer[inx:inx+3])  # Get the color
				inx += 3 
				rowdata.extend([r,g,b] * rlen)
				#if row < 4: print row, col, "(", r, g, b, ")*", rlen, ncols3, inx, len(rowdata)
				col = len(rowdata)                                  # How many pixels do we have? 
			
				if col >= ncols3:                                   # Enough 
					if col > ncols3:                                   # Enough 
						print "---------------->column exceeed", row, col
						rowdata = rowdata[:ncols3]                  # Truncate the rest. 
					if inx % 2 == 1:                            # Skip to next word boundary if needed.
						inx += 1                            # skip to word boundary at row end
						break
				else:
					if inx >= bufferlen: break
					rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0] # Read next record. 
					inx += 2 
			imageData.fromlist(rowdata)
			#if row < 4: print "Row ", row, " length", len(imageData) , inx
			if inx >= bufferlen: break
			rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0] # Read next record. 
			inx += 2 
		#print "Image length", len(imageData.tostring()) 
		image = Image.fromstring("RGB",(ncols,nrows),imageData.tostring()) 
		# ---------------------- Location on screen. ------------------------------
		x = upoints[0];
		y = upoints[1]; 
		width  = upoints[2] - x; 
		height = upoints[3] - y; 
		self.pdfOut.addImage(self.imageId,image,x,y,width,height,units="in")
		self.imageId += 1
		
	def c4_10(self,record,fd): self.dummyReader(fd,record)
	def c4_11(self,record,fd): 
		#self.dummyReader(fd,record) 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		color_fill = self.usedefaults.parameters['color_fill'] 
		if self.usedefaults.parameters['edge_visible'] != 0:
			color_edge =self.usedefaults.parameters['color_edge']
		else:
			color_edge ="none" 
		self.debugPrint("Rectangle" 	)
		self.pdfOut.addRectangle("Rectangle",x1,y2,x2-x1,y2-y1,units="in",
			stroke_color=color_edge,
			strokewidth=self.usedefaults.parameters['edge_width'], 
			color_fill=color_fill, 
			fill_style=self.usedefaults.parameters['fill_style'])
		return	
		
	def c4_12(self,record,fd): 
		self.debugPrint("CIRCLE" 	)
		self.dummyReader(fd,record)
	def c4_13(self,record,fd): self.dummyReader(fd,record)
	def c4_14(self,record,fd): self.dummyReader(fd,record)
	def c4_15(self,record,fd): self.dummyReader(fd,record)
	def c4_16(self,record,fd): self.dummyReader(fd,record)
	def c4_17(self,record,fd): self.dummyReader(fd,record)
	def c4_18(self,record,fd): self.dummyReader(fd,record)
	def c4_19(self,record,fd): self.dummyReader(fd,record)
	def c4_20(self,record,fd): self.dummyReader(fd,record)
	def c4_21(self,record,fd): self.dummyReader(fd,record)
	def c4_22(self,record,fd): 
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("4_22 %04x" % record.readInt(fd)   )
	def c4_23(self,record,fd): self.dummyReader(fd,record)
	def c4_24(self,record,fd): self.dummyReader(fd,record)
	def c4_25(self,record,fd): self.dummyReader(fd,record)
	def c4_26(self,record,fd): self.dummyReader(fd,record)
	def c4_27(self,record,fd): self.dummyReader(fd,record)
	def c4_28(self,record,fd): self.dummyReader(fd,record)
	def c4_29(self,record,fd): self.dummyReader(fd,record)

	# --------------- CLASS 5 Functions --------------------------------

	def c5_01(self,record,fd): 
		self.dummyReader(fd,record)
	def c5_02(self,record,fd):
		self.usedefaults.parameters['line_type']       =   record.readInt(fd)   
		self.debugPrint("Line Type:%04x" % self.usedefaults.parameters['line_type'] )
		self.usedefaults.parameters['stroke_dasharray'] = []
		if self.usedefaults.parameters['line_type'] == 1: self.usedefaults.parameters['stroke_dasharray'] = []
		if self.usedefaults.parameters['line_type'] == 2: self.usedefaults.parameters['stroke_dasharray'] = [5, 2]
		if self.usedefaults.parameters['line_type'] == 3: self.usedefaults.parameters['stroke_dasharray'] = [1, 1]
		if self.usedefaults.parameters['line_type'] == 4: self.usedefaults.parameters['stroke_dasharray'] = [5, 2]
		if self.usedefaults.parameters['line_type'] == 5: self.usedefaults.parameters['stroke_dasharray'] = [4, 1, 1]
		
	def c5_03(self,record,fd): 
		self.usedefaults.parameters['line_width']       =   record.readFloat(fd) 
		self.debugPrint("Line Width " , self.usedefaults.parameters['line_width']       )
	def c5_04(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_line'] = [r,g,b]
		self.debugPrint("Line color = ", self.usedefaults.parameters['color_line'])
	def c5_05(self,record,fd): self.dummyReader(fd,record)
	def c5_06(self,record,fd): self.dummyReader(fd,record)
	def c5_07(self,record,fd): self.dummyReader(fd,record)
	def c5_08(self,record,fd): self.dummyReader(fd,record)
	def c5_09(self,record,fd): self.dummyReader(fd,record)
	def c5_10(self,record,fd): 
		self.debugPrint("Text Precision Factor")
		self.dummyReader(fd,record)
	def c5_11(self,record,fd): 
		self.debugPrint("Text Precision Factor")
		self.dummyReader(fd,record)
	def c5_12(self,record,fd): 
		self.debugPrint("Character Expansion Factor")
		self.dummyReader(fd,record)
	def c5_13(self,record,fd): 
		self.debugPrint("Character Spacing")
		self.dummyReader(fd,record)
	def c5_14(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_text'] = [r,g,b]
	def c5_15(self,record,fd):
		self.usedefaults.parameters['char_height'] = record.readFloat(fd) 
		self.debugPrint("Character_Height: ", self.usedefaults.parameters['char_height'] )
	def c5_16(self,record,fd): 
		self.debugPrint("Character Orientation")
		#--self.dummyReader(fd,record)
		v1 = record.readFloat(fd)
		v2 = record.readFloat(fd)
		v3 = record.readFloat(fd)
		v4 = record.readFloat(fd)
		self.debugPrint("%f %f %f %f" % (v1,v2,v3,v4))

		self.usedefaults.parameters['rotate'] = None 
		if (v1 == 1) and (v2 == 0) and (v3 == 0.0) and (v4 == -1.0): 
			self.usedefaults.parameters['rotate'] = [v1,v2,v3,v4] 

	def c5_17(self,record,fd): 
		self.debugPrint("Text Path:%04x" % record.readInt(fd)   )
	def c5_18(self,record,fd): 
		hr = record.readInt(fd)   
		if hr == 3 : self.usedefaults.parameters['text_anchor'] = 'end'
		elif hr == 2: self.usedefaults.parameters['text_anchor'] = 'middle'
		else:  self.usedefaults.parameters['text_anchor'] = 'start'
		self.horizontal_alignment =  hr
		self.vertical_alignment = record.readInt(fd)   
		self.horizontal_C_alignment = record.readInt(fd)   
		self.vertical_C_alignment = record.readInt(fd)   
		self.debugPrint("Horizontal_Text_Alignment: %04x" % hr )
		self.debugPrint("Vertical_Text_Alignment: %04x" % self.vertical_alignment )
		self.debugPrint("Horizontal_C_Text_Alignment: %04x" %  self.horizontal_C_alignment) 
		self.debugPrint("Vertical C_Text_Alignment: %04x" %  self.vertical_C_alignment) 
	def c5_19(self,record,fd): self.dummyReader(fd,record)
	def c5_20(self,record,fd): self.dummyReader(fd,record)
	def c5_21(self,record,fd): self.dummyReader(fd,record)
	def c5_22(self,record,fd): 
		f = record.readInt(fd)   
		self.usedefaults.parameters['fill_style'] = "none" 
		if f == 1: self.usedefaults.parameters['fill_style'] = "solid" 
		if f == 2: self.usedefaults.parameters['fill_style'] = "pattern" 
		if f == 3: self.usedefaults.parameters['fill_style'] = "hatched" 
		if f == 4: self.usedefaults.parameters['fill_style'] = "none" 
		#print "c5_22", self.usedefaults.parameters['fill_style'] 
	def c5_23(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_fill'] =  [r,g,b] 
		self.debugPrint("Fill color", self.usedefaults.parameters['color_fill'] )
	def c5_24(self,record,fd): self.dummyReader(fd,record)
	def c5_25(self,record,fd): 
		f = record.readInt(fd)   
		self.usedefaults.parameters['pattern_index'] = f
		#print "c5_25", self.usedefaults.parameters['pattern_index'] 
	def c5_26(self,record,fd): self.debugPrint("Edge Bundle Index"); self.dummyReader(fd,record)
	def c5_27(self,record,fd): self.debugPrint("Edge Type") ; self.dummyReader(fd,record)
	def c5_28(self,record,fd): 
		self.usedefaults.parameters['edge_width'] = record.readFloat(fd)   
	def c5_29(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_edge'] =  [r,g,b] 
		self.debugPrint("Edge color", self.usedefaults.parameters['color_edge'] )
	def c5_30(self,record,fd): 
		self.usedefaults.parameters['edge_visible'] = record.readInt(fd)   
		self.debugPrint("Edge visible" ,  self.usedefaults.parameters['edge_visible'] )
		#print "Edge Visible  Mode: ", self.usedefaults.parameters['edge_visible'] 
	def c5_31(self,record,fd): self.dummyReader(fd,record)
	def c5_32(self,record,fd): 
		self.dummyReader(fd,record)
		usefmt  = "%s%dH" % (self.usedefaults.os_prelude, 4)
		patternIndex,nx,ny,precision = unpack(usefmt,record.buffer[:8]) 
		#print "c5_32 size = ", len(record.buffer) , " as ",  patternIndex,nx,ny,precision 
	def c5_33(self,record,fd): 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		#print "c5_33 items  = ", x1,y1,x2,y2
	def c5_34(self,record,fd): self.dummyReader(fd,record)
	def c5_35(self,record,fd): self.dummyReader(fd,record)
	def c5_36(self,record,fd): self.dummyReader(fd,record)
	def c5_37(self,record,fd): self.dummyReader(fd,record)
	def c5_38(self,record,fd): self.dummyReader(fd,record)
	def c5_39(self,record,fd): self.dummyReader(fd,record)
	def c5_40(self,record,fd): self.dummyReader(fd,record)
	def c5_41(self,record,fd): self.dummyReader(fd,record)
	def c5_42(self,record,fd): self.dummyReader(fd,record)
	def c5_43(self,record,fd): self.dummyReader(fd,record)
	def c5_44(self,record,fd): self.dummyReader(fd,record)
	def c5_45(self,record,fd): self.dummyReader(fd,record)
	def c5_46(self,record,fd): self.dummyReader(fd,record)
	def c5_47(self,record,fd): self.dummyReader(fd,record)
	def c5_48(self,record,fd): self.dummyReader(fd,record)
	def c5_49(self,record,fd): self.dummyReader(fd,record)
	def c5_50(self,record,fd): self.dummyReader(fd,record)
	def c5_51(self,record,fd): self.dummyReader(fd,record)
	def c5_83(self,record,fd): self.dummyReader(fd,record)
	def c5_99(self,record,fd): self.dummyReader(fd,record)
	def c5_123(self,record,fd): self.dummyReader(fd,record)
	
	def c6_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
        def c6_10(self,record,fd): self.dummyReader(fd,record)
 
	def c6_13(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_43(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_48(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_59(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_67(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_72(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_75(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_99(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_112(self,record,fd): record.readCGMstring(fd,record.parmslen)

	def c7_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_02(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_03(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_27(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_35(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_51(self,record,fd):  self.dummyReader(fd,record)

	def c8_25(self,record,fd):  self.dummyReader(fd,record)
	def c8_50(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c8_97(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c8_108(self,record,fd): record.readCGMstring(fd,record.parmslen)

	def c9_87(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c10_121(self,record,fd):  self.dummyReader(fd,record)
	def c12_1(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_2(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_3(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_4(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_5(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c13_9(self,record,fd):  self.dummyReader(fd,record)
	def c13_97(self,record,fd):  self.dummyReader(fd,record)
	def c15_78(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c15_105(self,record,fd):  self.dummyReader(fd,record)
        
	def c15_120(self,record,fd): record.readCGMstring(fd,record.parmslen)
	#----------------------  Functions --------------
	def dummyReader(self,fd,record): record.readCGMstring(fd,record.parmslen)
		#self.debugPrint(record.elementClass,record.elementID, record.parmslen

	#----------------------  Functions --------------
	def readRecord(self,fd,record):
		record.readCommand(fd)      # Sets the padding 
		record.showInfo()                  # DEBUG
		self.processCommand(fd,record)     # The record will read 
		if record.padding == 1:
			## DANGER  #self.debugPrint("Padding at [%04x] " % fd.tell(), "Char = ", record.readByte(fd) )
			#fd.read(1) # Skip the pad bye immediately
			record.readByte(fd) 
			pass
		if record.elementClass == 0 and record.elementID == 2: return 0
		return 1		

	#---------------------- Command processing  --------------
	def processCommand(self,fd,record):
		if 1:
			self.cgm_classes[record.elementClass][record.elementID](record,fd)
			return 
		if 1:
			print "BAD OPCODE", record.elementClass, record.elementID, record.parmslen 
			self.dummyReader(fd,record)
			pass
			

htmlHolder="""
<html> 

<head>

</head> 
<body>
	<embed src="%(filename)s" width="90%%" height="90%%" />
</body>
</html>
"""

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
	#if len(sys.argv) < 2: 
		#usage()
		#sys.exit(0)

	try:
		opts, alen = getopt.getopt(sys.argv[2:], 'c:f:') 
	except:
		usage()
		sys.exit(0)
	optin = {} 

	for k,v in opts: 
		#print k,v
		optin[k] = v 


	#--------------------------------- how to process 
	os_prelude = ">"
	code = optin.get('-c', '0')
	if code == '0': 
		os_prelude = ">"
	else:
		os_prelude = "<"

	#--------------------------------- where to write 
	outputfilename = optin.get('-f','tmp.pdf') 
	inputfilename  = sys.argv[1]

	#print "OPTS", opts, alen
	#print "Input  filename", inputfilename 
	#print "Output filename", outputfilename 
	#print "Output prelude ", os_prelude 

	#------------------------------------------------------------------------------
	# THE FOLLOWING ARE RESET WHEN PRECISION IS READ FROM HEADER
	#------------------------------------------------------------------------------
	xx = cgmFileReader(cgmParameters(os_prelude))
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
	
	dict = { 'filename':outputfilename, } 
	fd = open(outputfilename+".html",'w')
	fd.write(htmlHolder % dict) 
	fd.close() 
	

=======

# Python command parser file 
import os,sys , getopt, array, Image
from struct import *
from cgmdesc import *

PIXELS_PER_INCH = 72

from cgmParsedOutput import cgmParsedOutputClass

class cgmParameters:
	def __init__(self,os_prelude):
		self.parameters = { }  
		self.os_prelude = os_prelude
		self.fmt_byteString  = "%sB" % (os_prelude)
		self.fmt_wordString  = "%sH" % (os_prelude)
		self.fmt_3i          = "%s3h" % (os_prelude)
		self.fmt_shortString = "%sh" % (os_prelude)
		self.fmt_floatString = "%sf" % (os_prelude)
		self.fmt_doubleString = "%sd" % (os_prelude)
		self.fmt_longString = "%sI" % (os_prelude)
		self.fmt_vbpString  = "ff" 
		self.fmt_bpString  = "f" 

		self.parameters['line_type'] = 0 
		self.parameters['rotate'] =  [0,0,0,0]
		self.parameters['stroke_dasharray'] = []
		self.parameters['scale_factor']     = 1.0;
		self.parameters['color_mode']       = 0;
		self.parameters['line_width_mode']  = 0;
		self.parameters['marker_size_mode'] = 0;
		self.parameters['edge_width_mode']  = 0;
		self.parameters['color_background'] = [ 255,255,255 ]
		self.parameters['color_fill']       = [ 255,255,255 ] 
		self.parameters['color_edge']       = [ 0,0,0]
 		self.parameters['color_line']       = [0,0,100] 
		self.parameters['color_text']       = [8,8,8]
		self.parameters['line_width']       = 0.01 
		self.parameters['char_height']      = 0.1 
		self.parameters['precision_integer']  = 0; 
		self.parameters['precision_of_index']  = 0; 
		self.parameters['precision_of_color']  = 0; 
		self.parameters['precision_of_color_index']  = 0; 
		self.parameters['max_color_index']  = 255; 
		self.parameters['char_set_list'] =  ''
		self.parameters['precision_of_name'] = 8
		self.parameters['char_coding']  = 1 
		self.parameters['vdc_integer']  = 0 
		self.parameters['vdc_realprec'] = 4
		self.parameters['vdc_p1']       = 0   
		self.parameters['vdc_p2']       = 9   
		self.parameters['vdc_p3']       = 23   
		self.parameters['vdc_intprec']  = 2
		self.parameters['enum_prec']    = 2;
		self.parameters['rgb_p1']       = 0;   
		self.parameters['rgb_p2']       = 16;   
		self.parameters['rgb_p3']       = 16;   
		self.parameters['fonts_list']   = ''
		self.parameters['clip_indicator'] = 0
		self.parameters['vdc_type'] = 0
		self.parameters['font_size'] = 10;
		self.parameters['font_style'] = 'normal';
		self.parameters['font_weight'] = 'normal';
		self.parameters['text_anchor'] = "start"
		self.parameters['horizontal_alignment'] = 0
		self.parameters['vertical_alignment'] = 0
		self.parameters['edge_width']   = 1
		self.parameters['fill_style']   = "none"
		self.parameters['edge_visible'] =  1
		self.parameters['pattern_index'] =  0


class cgmRecord: 
	def __init__(self,usedefaults,id=0,os_prelude = '>'):
		self.cmd = None
		self.ID =id
		self.elementClass = None
		self.elementID=None
		self.parameters = ''
		self.parmslen = 0
		self.morePartitions = 0
		self.padding  = 0
		self.opcodes = None # Could include drawing primitives, etc. 
		self.usedefaults = usedefaults 
		self.debugOn = 0

	def debugPrint(self,*args): 
		if self.debugOn == 1: print args 	

	def rawdebugPrint(self,*args): 
		if self.debugOn == 2: print args 	


	def readCommand(self,fd):
		#self.debugPrint( "At [ %04x ] " %  fd.tell())
		buf = fd.read(2)                      # At location!
		cmd = unpack(self.usedefaults.fmt_wordString,buf)[0]   # I am using a global, yuck.
		self.cmd = cmd                        # Copy of the local 
		self.elementClass = (cmd >> 12) & 0xF;       # Get CLASS 
		self.elementID    = (cmd >> 5) & 0x7f;       # Element 
		self.parmslen 	  = cmd & 0x1f;              # Length of parameters.
		if self.parmslen == 31:
			p   = self.readInt(fd)           # -------------------------------------------
			self.padding  = p & 0x0001 
			self.parmslen = p & 0x7FFF
			self.morePartitions = p & 0x8000
		if self.morePartitions == 0: 
			self.padding = self.parmslen & 1;
		else:
			self.padding = 0


	def readNextPartition(self,fd):
		p   = self.readInt(fd)           # -------------------------------------------
		parmslen = p & 0x7FFF
		#self.debugPrint("READING NEXT PARTITION LENGTH %04x" % p, "%04x" % fd.tell())
		#self.debugPrint("READING PADDING    >>>>>", self.padding  )
		#self.debugPrint("READING LEN    >>>>>", parmslen )
		morePartitions = p & 0x8000
		#self.debugPrint("READING MORE?    >>>>>", morePartitions  )
		b = fd.read(parmslen)
		self.buffer += b
		if self.morePartitions == 0: 
			self.padding = fd.tell() & 1;
		return morePartitions;


	def readParameters(self,fd):
		#self.debugPrint("Reading [", self.parmslen, "]" )
		self.parameters = fd.read(self.parmslen)
		
	def readCGMstring(self,fd,ilen=0):
		if ilen == 0: 
			buf = fd.read(1)                     # Get segment length
			slen = unpack(self.usedefaults.fmt_byteString,buf)[0] # 
		else:
			slen = ilen
		#self.debugPrint("-->Reading ", slen, " bytes", ilen  )
		self.buffer = fd.read(slen)
		if (self.morePartitions): 
			while 1:
				more = self.readNextPartition(fd)   
				if more == 0: break

	def readFloat(self,fd): 
		#self.debugPrint("READING FLOAT at", fd.tell())
		if (self.usedefaults.parameters['vdc_p3'] == 23): 
			buf = fd.read(4)                     # Get segment lengthbb
			return unpack(self.usedefaults.fmt_floatString,buf)[0]
		if (self.usedefaults.parameters['vdc_p3'] == 52): 
			buf = fd.read(8)                     # Get segment lengthbb
			return unpack(self.usedefaults.fmt_doubleString,buf)[0]
		if (self.usedefaults.parameters['vdc_p3'] == 16): 
			buf = fd.read(4)                     # Get segment lengthbb
			i = unpack(self.usedefaults.fmt_longString,buf)[0]
			return float(i) /0x00010000; 
		if (self.usedefaults.parameters['vdc_p3'] == 32): 
			buf = fd.read(8)                     # Get segment lengthbb
			i = unpack(self.usedefaults.fmt_doubleString,buf)[0]
			return double(i) /0x01000000; 
		return 0.0 	

	def readByte(self,fd): 
		buf = fd.read(1)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_byteString,buf)[0]
	
	def readInt(self,fd): 
		buf = fd.read(2)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_wordString,buf)[0]
		
	def readIntTriple(self,fd): 
		buf = fd.read(6)                     # Get segment lengthbb
		return unpack(self.usedefaults.fmt_3i,buf)
		
	def showInfo(self):
		istr = "CMD:%04x Class:%x ID:%X (%d) LN:%d Pad:%04x Partition:%04x" % (self.cmd,self.elementClass,self.elementID,self.elementID, self.parmslen, self.padding, self.morePartitions)
		self.rawdebugPrint(istr)
		
class cgmFileReader:
	def __init__(self,usedefaults):
		self.usedefaults = usedefaults
		self.cmd   = None
		self.imageId = 1
	
		# These are primitives that you have to translate into drawing 
		# commands for SVG other packages
		#
		# Format:  keyword:  parameters 
		# 
		self.primitives = [] 
		self.textStrings = [] 
		
		# Some defaults:

		#------------------------------------- ONLY STANDARD DEFINITIONS PLEASE 
		self.cgm_class0 = { }
		self.cgm_class0[0]  = self.c0_00
		self.cgm_class0[1]  = self.c0_01
		self.cgm_class0[2]  = self.c0_02
		self.cgm_class0[3]  = self.c0_03
		self.cgm_class0[4]  = self.c0_04
		self.cgm_class0[5]  = self.c0_05
		self.cgm_class0[6]  = self.c0_06
		self.cgm_class0[7]  = self.c0_07
		self.cgm_class0[8]  = self.c0_08
		self.cgm_class0[9]  = self.c0_09
		self.cgm_class0[13]  = self.c0_13
		self.cgm_class0[14]  = self.c0_14
		self.cgm_class0[15]  = self.c0_15
		self.cgm_class0[16]  = self.c0_16
		self.cgm_class0[17]  = self.c0_17
		self.cgm_class0[18]  = self.c0_18
		self.cgm_class0[19]  = self.c0_19
		self.cgm_class0[20]  = self.c0_20
		self.cgm_class0[21]  = self.c0_21
		self.cgm_class0[22]  = self.c0_22
		self.cgm_class0[23]  = self.c0_23
		
		
		self.cgm_class1 = {}
		self.cgm_class1[1] = self.c1_01 
		self.cgm_class1[2] = self.c1_02 
		self.cgm_class1[3] = self.c1_03 
		self.cgm_class1[4] = self.c1_04 
		self.cgm_class1[5] = self.c1_05 
		self.cgm_class1[6] = self.c1_06 
		self.cgm_class1[7] = self.c1_07 
		self.cgm_class1[8] = self.c1_08 
		self.cgm_class1[9] = self.c1_09 
		self.cgm_class1[10] = self.c1_10 
		self.cgm_class1[11] = self.c1_11 
		self.cgm_class1[12] = self.c1_12 
		self.cgm_class1[13] = self.c1_13 
		self.cgm_class1[14] = self.c1_14 
		self.cgm_class1[15] = self.c1_15 
		self.cgm_class1[16] = self.c1_16 
		self.cgm_class1[17] = self.c1_17 
		self.cgm_class1[18] = self.c1_18 
		self.cgm_class1[19] = self.c1_19 
		self.cgm_class1[20] = self.c1_20 
		self.cgm_class1[21] = self.c1_21 
		self.cgm_class1[22] = self.c1_22 
		self.cgm_class1[23] = self.c1_23 
		self.cgm_class1[24] = self.c1_24 
		
		self.cgm_class2 = {}
		self.cgm_class2[1] = self.c2_01_scalingMode
		self.cgm_class2[2] = self.c2_02_colorSelectionMode
		self.cgm_class2[3] = self.c2_03_lineWidthSpecMode
		self.cgm_class2[4] = self.c2_04_markerSizeSpecMode
		self.cgm_class2[5] = self.c2_05_edgeWidthMode
		self.cgm_class2[6] = self.c2_06_vdcExtent
		self.cgm_class2[7] = self.c2_07_backgroundColor
		self.cgm_class2[8] = self.c2_08_deviceViewport
		self.cgm_class2[9] = self.c2_09_deviceViewportSpecMode
		self.cgm_class2[10] = self.c2_10_deviceViewportMapping
		self.cgm_class2[11] = self.c2_11_lineRepresentation
		self.cgm_class2[12] = self.c2_12_markerRepresentation
		self.cgm_class2[13] = self.c2_13_textRepresentation
		self.cgm_class2[14] = self.c2_14_fillRepresentation
		self.cgm_class2[15] = self.c2_15_edgeRepresentation
		self.cgm_class2[16] = self.c2_16_interiorStyleMode
		self.cgm_class2[17] = self.c2_17_lineEdgeType
		self.cgm_class2[18] = self.c2_18_hatchStyle
		self.cgm_class2[19] = self.c2_19_geometricPattern
		self.cgm_class2[20] = self.c2_20_applicationStructure
		self.cgm_class2[81] = self.c2_81
		
		 
		self.cgm_class3 = {}
		self.cgm_class3[1] = self.c3_01 
		self.cgm_class3[2] = self.c3_02 
		self.cgm_class3[3] = self.c3_03 
		self.cgm_class3[4] = self.c3_04 
		self.cgm_class3[5] = self.c3_05 
		self.cgm_class3[6] = self.c3_06 
		self.cgm_class3[7] = self.c3_07 
		self.cgm_class3[8] = self.c3_08 
		self.cgm_class3[9] = self.c3_09 
		self.cgm_class3[10] = self.c3_10 
		self.cgm_class3[11] = self.c3_11 
		self.cgm_class3[12] = self.c3_12 
		self.cgm_class3[13] = self.c3_13 
		self.cgm_class3[14] = self.c3_14 
		self.cgm_class3[15] = self.c3_15 
		self.cgm_class3[16] = self.c3_16 
		self.cgm_class3[17] = self.c3_17 
		self.cgm_class3[18] = self.c3_18 
		self.cgm_class3[19] = self.c3_19 
		self.cgm_class3[20] = self.c3_20 
		self.cgm_class3[21] = self.c3_21 
		self.cgm_class3[22] = self.c3_22 
		self.cgm_class3[74] = self.c3_74 
		self.cgm_class3[78] = self.c3_78 
		self.cgm_class3[83] = self.c3_83 
		self.cgm_class3[115] = self.c3_115 
	
		self.cgm_class4 = {}
		self.cgm_class4[1] = self.c4_01 
		self.cgm_class4[2] = self.c4_02 
		self.cgm_class4[3] = self.c4_03 
		self.cgm_class4[4] = self.c4_04 
		self.cgm_class4[5] = self.c4_05 
		self.cgm_class4[6] = self.c4_06 
		self.cgm_class4[7] = self.c4_07 
		self.cgm_class4[8] = self.c4_08 
		self.cgm_class4[9] = self.c4_09 
		self.cgm_class4[10] = self.c4_10 
		self.cgm_class4[11] = self.c4_11 
		self.cgm_class4[12] = self.c4_12 
		self.cgm_class4[13] = self.c4_13 
		self.cgm_class4[14] = self.c4_14 
		self.cgm_class4[15] = self.c4_15 
		self.cgm_class4[16] = self.c4_16 
		self.cgm_class4[17] = self.c4_17 
		self.cgm_class4[18] = self.c4_18 
		self.cgm_class4[19] = self.c4_19 
		self.cgm_class4[20] = self.c4_20 
		self.cgm_class4[21] = self.c4_21 
		self.cgm_class4[22] = self.c4_22 
		self.cgm_class4[23] = self.c4_23 
		self.cgm_class4[24] = self.c4_24 
		self.cgm_class4[25] = self.c4_25 
		self.cgm_class4[26] = self.c4_26 
		self.cgm_class4[27] = self.c4_27 
		self.cgm_class4[28] = self.c4_28 
		self.cgm_class4[29] = self.c4_29 

		self.cgm_class5 = {}
		self.cgm_class5[1] = self.c5_01 
		self.cgm_class5[2] = self.c5_02 
		self.cgm_class5[3] = self.c5_03 
		self.cgm_class5[4] = self.c5_04 
		self.cgm_class5[5] = self.c5_05 
		self.cgm_class5[6] = self.c5_06 
		self.cgm_class5[7] = self.c5_07 
		self.cgm_class5[8] = self.c5_08 
		self.cgm_class5[9] = self.c5_09 
		self.cgm_class5[10] = self.c5_10 
		self.cgm_class5[11] = self.c5_11 
		self.cgm_class5[12] = self.c5_12 
		self.cgm_class5[13] = self.c5_13 
		self.cgm_class5[14] = self.c5_14 
		self.cgm_class5[15] = self.c5_15 
		self.cgm_class5[16] = self.c5_16 
		self.cgm_class5[17] = self.c5_17 
		self.cgm_class5[18] = self.c5_18 
		self.cgm_class5[19] = self.c5_19 
		self.cgm_class5[20] = self.c5_20 
		self.cgm_class5[21] = self.c5_21 
		self.cgm_class5[22] = self.c5_22 
		self.cgm_class5[23] = self.c5_23 
		self.cgm_class5[24] = self.c5_24 
		self.cgm_class5[25] = self.c5_25 
		self.cgm_class5[26] = self.c5_26 
		self.cgm_class5[27] = self.c5_27 
		self.cgm_class5[28] = self.c5_28 
		self.cgm_class5[29] = self.c5_29 
		self.cgm_class5[30] = self.c5_30 
		self.cgm_class5[31] = self.c5_31 
		self.cgm_class5[32] = self.c5_32 
		self.cgm_class5[33] = self.c5_33 
		self.cgm_class5[34] = self.c5_34 
		self.cgm_class5[35] = self.c5_35 
		self.cgm_class5[36] = self.c5_36 
		self.cgm_class5[37] = self.c5_37 
		self.cgm_class5[38] = self.c5_38 
		self.cgm_class5[39] = self.c5_39 
		self.cgm_class5[40] = self.c5_40 
		self.cgm_class5[41] = self.c5_41 
		self.cgm_class5[42] = self.c5_42 
		self.cgm_class5[43] = self.c5_43 
		self.cgm_class5[44] = self.c5_44 
		self.cgm_class5[45] = self.c5_45 
		self.cgm_class5[46] = self.c5_46 
		self.cgm_class5[47] = self.c5_47 
		self.cgm_class5[48] = self.c5_48 
		self.cgm_class5[49] = self.c5_49 
		self.cgm_class5[50] = self.c5_50 
		self.cgm_class5[51] = self.c5_51 
		self.cgm_class5[83] = self.c5_83 
		self.cgm_class5[99] = self.c5_99 
		self.cgm_class5[123] = self.c5_123 

		self.cgm_class6 = {}
		self.cgm_class6[1] = self.c6_01 
		self.cgm_class6[13] = self.c6_13 
                self.cgm_class6[10] = self.c6_10
		self.cgm_class6[43] = self.c6_43 
		self.cgm_class6[48] = self.c6_48 
		self.cgm_class6[59] = self.c6_59 
		self.cgm_class6[67] = self.c6_67 
		self.cgm_class6[72] = self.c6_72 
		self.cgm_class6[75] = self.c6_75 
		self.cgm_class6[99] = self.c6_99 
		self.cgm_class6[112] = self.c6_112 

		self.cgm_class7 = {}
		self.cgm_class7[1] = self.c7_01 
		self.cgm_class7[2] = self.c7_02 
		self.cgm_class7[3] = self.c7_03 
		self.cgm_class7[27] = self.c7_27 
		self.cgm_class7[35] = self.c7_35 
                self.cgm_class7[51] = self.c7_51



		self.cgm_class8 = {}
                self.cgm_class8[25] = self.c8_25

		self.cgm_class8[50] = self.c8_50
		self.cgm_class8[97] = self.c8_97
		self.cgm_class8[108] = self.c8_108

		self.cgm_class9 = {}
                self.cgm_class9[87] = self.c9_87

		self.cgm_class10 = {}
		self.cgm_class10[121] = self.c10_121

		self.cgm_class11 = {}

		self.cgm_class12 = {}
		self.cgm_class12[1] = self.c12_1 
		self.cgm_class12[2] = self.c12_2 
		self.cgm_class12[3] = self.c12_3 
		self.cgm_class12[4] = self.c12_4 
		self.cgm_class12[5] = self.c12_5 

		self.cgm_class13 = {}
                self.cgm_class13[9] = self.c13_9
		self.cgm_class13[97] = self.c13_97

		self.cgm_class14 = {}
		self.cgm_class15 = {}
		self.cgm_class15[78] = self.c15_78 
		self.cgm_class15[105] = self.c15_105
		self.cgm_class15[120] = self.c15_120 

		self.cgm_classes = { }
		self.cgm_classes[0] = self.cgm_class0
		self.cgm_classes[1] = self.cgm_class1
		self.cgm_classes[2] = self.cgm_class2
		self.cgm_classes[3] = self.cgm_class3
		self.cgm_classes[4] = self.cgm_class4
		self.cgm_classes[5] = self.cgm_class5
		self.cgm_classes[6] = self.cgm_class6
		self.cgm_classes[7] = self.cgm_class7
		self.cgm_classes[8] = self.cgm_class8
		self.cgm_classes[9] = self.cgm_class9
		self.cgm_classes[10] = self.cgm_class10
		self.cgm_classes[11] = self.cgm_class11
		self.cgm_classes[12] = self.cgm_class12
		self.cgm_classes[13] = self.cgm_class13
		self.cgm_classes[14] = self.cgm_class14
		self.cgm_classes[15] = self.cgm_class15
		self.pdfOut = None; 
		self.debugLevel = 0

	def debugPrint(self,*args): 
		if self.debugLevel > 0: print args 	

	##
	# You MUST override this function 
	def readFile(self,inputfilename,outputfile):
		self.pdfOut = cgmParsedOutputClass(outputfile); 
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

	# --------------- CLASS 0 Functions --------------------------------
	def c0_00(self,record,fd): pass 
	def c0_01(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_02(self,record,fd): pass
	def c0_03(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
		self.debugPrint("Picture Name:", record.buffer )
	def c0_04(self,record,fd): pass 
	def c0_05(self,record,fd): pass 
	def c0_06(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_07(self,record,fd): pass 
	def c0_08(self,record,fd): pass 
	def c0_09(self,record,fd): pass 
	def c0_13(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
		p1 = record.readInt(fd); 
	def c0_14(self,record,fd): pass 
	def c0_15(self,record,fd): pass 
	def c0_16(self,record,fd): pass 
	def c0_17(self,record,fd): pass 
	def c0_18(self,record,fd): pass 
	def c0_19(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
	 	record.readInt(fd)
	def c0_20(self,record,fd): pass
	def c0_21(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
	def c0_22(self,record,fd): pass
	def c0_23(self,record,fd): pass
	def c0_59(self,record,fd):  self.dummyReader(fd,record)
	
	# --------------- CLASS 1 Functions --------------------------------
	# When you read these definitions, you can try to comprehend how 
	# to read the coordinates. 
	#--------------------------------------------------------------
	def c1_01(self,record,fd): 
		record.readParameters(fd)
	def c1_02(self,record,fd): 
		self.debugPrint("File Description:", record.elementClass,record.elementID, record.parmslen)
		record.readCGMstring(fd)
		self.primitives.append("Description: " + "".join(record.buffer))
	
	def c1_03(self,record,fd): 
		self.usedefaults.parameters['vdc_type'] = record.readInt(fd)
	def c1_04(self,record,fd): self.usedefaults.precision_integer = record.readInt(fd)
	def c1_05(self,record,fd):  
		self.usedefaults.vdc_p1, self.usedefaults.vdc_p2, self.usedefaults.vdc_p3 = record.readIntTriple(fd)   
		self.debugPrint("PRECISION", self.usedefaults.vdc_p1, self.usedefaults.vdc_p2, self.usedefaults.vdc_p3 )
		if self.usedefaults.parameters['vdc_p1'] == 0: 
			if self.usedefaults.parameters['vdc_p2'] == 9  and self.usedefaults.parameters['vdc_p3'] == 23: 
				self.usedefaults.fmt_vbpString  = "ff" 
				self.usedefaults.fmt_bpString  = "f" 
			if self.usedefaults.parameters['vdc_p2'] == 12 and self.usedefaults.parameters['vdc_p3'] == 52: 
				self.usedefaults.fmt_vbpString  = "dd" 
				self.usedefaults.fmt_bpString  = "d" 
		else:
			if self.usedefaults.parameters['vdc_p2'] == 16  and self.usedefaults.parameters['vdc_p3'] == 16: 
				self.usedefaults.fmt_vbpString  = "HH" 
				self.usedefaults.fmt_bpString  = "H" 
			if self.usedefaults.parameters['vdc_p2'] == 32  and self.usedefaults.parameters['vdc_p3'] == 32: 
				self.usedefaults.fmt_vbpString  = "II" 
				self.usedefaults.fmt_bpString  = "I" 
			
	def c1_06(self,record,fd): self.usedefaults.parameters['precision_of_index'] = record.readInt(fd)
	def c1_07 (self,record,fd): self.usedefaults.parameters['precision_of_color'] = record.readInt(fd)
	def c1_08(self,record,fd): self.usedefaults.parameters['precision_of_color_index'] = record.readInt(fd)
	def c1_09 (self,record,fd): 
		self.usedefaults.parameters['max_color_index'] = record.readByte(fd)
		self.debugPrint("Color Index ", self.usedefaults.parameters['max_color_index'] )
	def c1_10 (self,record,fd): 
		if record.parmslen == 6: 
			self.usedefaults.parameters['rgb_p1'], self.usedefaults.parameters['rgb_p2'], self.usedefaults.parameters['rgb_p3'] = record.readIntTriple(fd)   
		if record.parmslen == 4: 
			self.usedefaults.parameters['rgb_p1']  = record.readInt(fd)   
			self.usedefaults.parameters['rgb_p2']  = record.readInt(fd)   
			self.usedefaults.parameters['rgb_p3']  = 0
	def c1_11 (self,record,fd):  # C
		p1,p2,p3 = record.readIntTriple(fd)   
		self.debugPrint("Elements List=", p1,p2,p3)
	def c1_12(self,record,fd):  # D
		#self.debugPrint("metaFileElements", record.elementClass,record.elementID, record.parmslen
		itemCounts = record.parmslen/2 
		for x in range(itemCounts): 
			p1  = record.readInt(fd)   
			self.debugPrint("%04x" % p1,)
			self.debugPrint(" " )
	
	def c1_13(self,record,fd): 
		self.debugPrint("Font list", record.elementClass,record.elementID, record.parmslen)
		self.usedefaults.parameters['fonts_list'] = record.readCGMstring(fd,record.parmslen)
	def c1_14(self,record,fd): 
		self.usedefaults.parameters['char_set_list'] = record.readCGMstring(fd,record.parmslen)
	def c1_15(self,record,fd): self.usedefaults.parameters['char_coding']  = record.readInt(fd)   
	def c1_16(self,record,fd): self.usedefaults.parameters['precision_of_name']  = record.readInt(fd)   
	def c1_17(self,record,fd): 
		#self.primitives.append("max_vdc_extent: "+ record.elementClass,record.elementID + " " +  record.parmslen)
		pass
	def c1_18(self,record,fd):
		self.debugPrint("seg priority extent", record.elementClass,record.elementID, record.parmslen)
	def c1_19(self,record,fd): 
		self.debugPrint("color model", record.elementClass,record.elementID, record.parmslen)
	def c1_20(self,record,fd):
		self.debugPrint("color calibration", record.elementClass,record.elementID, record.parmslen)
	def c1_21(self,record,fd): 
		self.debugPrint("font properties", record.elementClass,record.elementID, record.parmslen)
	def c1_22(self,record,fd): 
		self.debugPrint("glyph Mappging", record.elementClass,record.elementID, record.parmslen)
	def c1_23(self,record,fd):
		self.debugPrint("symbol library", record.elementClass,record.elementID, record.parmslen)
	def c1_24(self,record,fd): 
		self.debugPrint("picture directory", record.elementClass,record.elementID, record.parmslen)
		
	# --------------- CLASS 2 Functions --------------------------------
	def c2_01_scalingMode(self,record,fd): 
		self.debugPrint("Scaling Mode: "  , record.readInt(fd))    # Actually, read in the points for the VDC 
		self.usedefaults.parameters['scale_factor'] = record.readFloat(fd)    # Actually, read in the points for the VDC 
		self.debugPrint("Scaling Metric: ", self.usedefaults.parameters['scale_factor'] )
	def c2_02_colorSelectionMode(self,record,fd): 
		self.usedefaults.parameters['color_mode'] = record.readInt(fd)   
		self.debugPrint("Color Mode: ", self.usedefaults.parameters['color_mode'] )
	def c2_03_lineWidthSpecMode(self,record,fd): 
		self.usedefaults.parameters['line_width_mode'] = record.readInt(fd)   
		self.debugPrint("Line Width MODE: ", self.usedefaults.parameters['line_width_mode'] )
	def c2_04_markerSizeSpecMode(self,record,fd): 
		self.usedefaults.parameters['marker_size_mode'] = record.readInt(fd)   
		self.debugPrint("Marker Size Mode: ", self.usedefaults.parameters['marker_size_mode'] )
	def c2_05_edgeWidthMode(self,record,fd): 
		self.usedefaults.parameters['edge_width_mode'] = record.readInt(fd)   
		self.debugPrint("Edge Width Mode: ", self.usedefaults.parameters['edge_width_mode'] )
	def c2_06_vdcExtent(self,record,fd):
		self.debugPrint("VDC extent = ", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 4; 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		self.debugPrint("VDC extents, ", x1,y1,x2,y2)

	def c2_07_backgroundColor(self,record,fd): 
		self.debugPrint("Background = ", record.elementClass,record.elementID, record.parmslen)
		r = record.readByte(fd)   
		g = record.readByte(fd)   
		b = record.readByte(fd)   
		self.usedefaults.parameters['color_background'] = [r,g,b]
		self.debugPrint(self.usedefaults.parameters['color_background'])
	def c2_08_deviceViewport(self,record,fd): 
		self.debugPrint("Device ViewPort = ", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 4; 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		self.debugPrint("Viewport extents, ", x1,y1,x2,y2)
		self.usedefaults.parameters['viewport_extents'] = [x1,y1,x2,y2]

	def c2_09_deviceViewportSpecMode(self,record,fd): self.dummyReader(fd,record)
	def c2_10_deviceViewportMapping(self,record,fd): self.dummyReader(fd,record)
	def c2_11_lineRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_12_markerRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_13_textRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_14_fillRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_15_edgeRepresentation(self,record,fd): self.dummyReader(fd,record)
	def c2_16_interiorStyleMode(self,record,fd): self.dummyReader(fd,record)
	def c2_17_lineEdgeType(self,record,fd): self.dummyReader(fd,record)
	def c2_18_hatchStyle(self,record,fd): self.dummyReader(fd,record)
	def c2_19_geometricPattern(self,record,fd): self.dummyReader(fd,record)
	
	def c2_20_applicationStructure(self,record,fd): 
		self.debugPrint("c2_20", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   

	def c2_81(self,record,fd):  self.dummyReader(fd,record)

	def c3_01(self,record,fd): 
		self.dummyReader(fd,record)
	def c3_02(self,record,fd): 
		self.debugPrint("c3_02", record.elementClass,record.elementID, record.parmslen)
		if record.parmslen > 0: 
			self.usedefaults.parameters['vdc_p1'], self.usedefaults.parameters['vdc_p2'], self.usedefaults.parameters['vdc_p3'] = record.readIntTriple(fd)   
	
	def c3_03(self,record,fd):
		self.dummyReader(fd,record)
	def c3_04(self,record,fd):
		self.dummyReader(fd,record)
	def c3_05(self,record,fd):
		self.debugPrint("c3_05", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   
	def c3_06(self,record,fd): self.clip_indicator =  record.readInt(fd)   
	def c3_07(self,record,fd): self.dummyReader(fd,record)
	def c3_08(self,record,fd): self.dummyReader(fd,record)
	def c3_09(self,record,fd): self.dummyReader(fd,record)
	def c3_10(self,record,fd): self.dummyReader(fd,record)
	def c3_11(self,record,fd): self.dummyReader(fd,record)
	def c3_12(self,record,fd): self.dummyReader(fd,record)
	def c3_13(self,record,fd): self.dummyReader(fd,record)
	def c3_14(self,record,fd): self.dummyReader(fd,record)
	def c3_15(self,record,fd): self.dummyReader(fd,record)
	def c3_16(self,record,fd): self.dummyReader(fd,record)
	def c3_17(self,record,fd): self.dummyReader(fd,record)
	def c3_18(self,record,fd): self.dummyReader(fd,record)
	def c3_19(self,record,fd): self.dummyReader(fd,record)
	def c3_20(self,record,fd): self.dummyReader(fd,record)
	def c3_21(self,record,fd): self.dummyReader(fd,record)
	def c3_22(self,record,fd): 
		self.debugPrint("c3_22", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )
	def c3_74(self,record,fd): 
		self.debugPrint("c3_74", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )
	def c3_78(self,record,fd): 
		self.debugPrint("c3_78", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )

	def c3_83(self,record,fd):  self.dummyReader(fd,record)

	def c3_115(self,record,fd): 
		self.debugPrint("c3_115", record.elementClass,record.elementID, record.parmslen)
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("%04x" % record.readInt(fd)   )

	# --------------- CLASS 4 Functions --------------------------------
	def c4_01(self,record,fd): 
		self.dummyReader(fd,record)                  # Read the record.
		sz = len(record.buffer)/4
		usefmt  = "%s%d%s" % (self.usedefaults.os_prelude, sz, self.usedefaults.fmt_bpString)
		upoints = unpack(usefmt,record.buffer[:sz*4])  # Get the length
		if len(upoints) >= 16: 
			self.debugPrint("POLYLINE format", usefmt, sz, sz*4, len(record.buffer), self.usedefaults.parameters['color_line'], )
		#sw        = self.usedefaults.parameters['line_width']
		fill_style    = self.usedefaults.parameters['fill_style']
		sw            = self.usedefaults.parameters['line_width'] 
		color_line    = self.usedefaults.parameters['color_line']
		color_fill=self.usedefaults.parameters['color_fill'] 
		color_edge=self.usedefaults.parameters['color_edge'] 
		edge_visible =self.usedefaults.parameters['edge_visible'] 
		#print "Edge Visible  Mode: ", self.usedefaults.parameters['edge_visible'] 
		self.debugPrint("C4_01 :", sw, color_line, color_fill, color_edge) 
		#if len(upoints) >= 500: print "LONG POLYGON", color_line, color_fill, color_edge, sw, len(upoints) 
		self.debugPrint("C4_01 :", sw, len(upoints), fill_style, color_line, color_fill, color_edge ) 
		self.pdfOut.addPolyLine(polygon=0, stroke=color_line, strokewidth=sw, points=upoints,	edge_visible = edge_visible, 
				color_fill = "none",  strokedasharray=self.usedefaults.parameters['stroke_dasharray']);

	def c4_02(self,record,fd): self.dummyReader(fd,record)
	def c4_03(self,record,fd): self.dummyReader(fd,record)

	def c4_04(self,record,fd): 
		self.dummyReader(fd,record)
		fmt1 = "%s%sHB" % (self.usedefaults.os_prelude,self.usedefaults.fmt_vbpString)
		sz = calcsize(fmt1)  
		usefmt  = "%s%sHB%ds" % (self.usedefaults.os_prelude, self.usedefaults.fmt_vbpString, len(record.buffer) - sz)
		x,y,e,c,s =  unpack(usefmt,record.buffer)  # Get the length
		fsz = int( PIXELS_PER_INCH  * self.usedefaults.parameters['char_height'])   # Pixels per inch  - DEBUG ONLY
		self.debugPrint("CGM TEXT:", x,y,e,c,s)
		ou_s = "%f:%f:%s " % ( x,y,s )
		if not ou_s in self.textStrings: self.textStrings.append(ou_s) 
		#self.debugPrint("Fsz %d " % fsz + " char height " +  str(self.usedefaults.parameters['char_height']))
		# ----------------------------------------------------------------------------------------
		# Determine
		# ----------------------------------------------------------------------------------------
		self.fontsize = fsz * 5   
		self.pdfOut.addTextTag(x,y,s,
				anchor=self.usedefaults.parameters['text_anchor'], 
				color=self.usedefaults.parameters['color_text'],
				units="in", 
				verticalAlignment=self.vertical_alignment,
				fontsize=self.usedefaults.parameters['char_height'],
				horizontalAlignment=self.horizontal_alignment,
				matrix=self.usedefaults.parameters['rotate'])
		
	def c4_05(self,record,fd): self.dummyReader(fd,record)
	def c4_06(self,record,fd): self.dummyReader(fd,record)
	def c4_07(self,record,fd): 
		self.dummyReader(fd,record)                  # Read the record.
		sz = len(record.buffer)/4                    # Get the number of floats 
		usefmt  = "%s%d%s" % (self.usedefaults.os_prelude, sz, self.usedefaults.fmt_bpString) 
		upoints = unpack(usefmt,record.buffer[:sz*4])  # Get the length

		if self.usedefaults.parameters['edge_visible']: 
			sw=self.usedefaults.parameters['edge_width'] 
		else: 
			sw=self.usedefaults.parameters['line_width']

		edge_visible =  self.usedefaults.parameters['edge_visible']
		fill_style=self.usedefaults.parameters['fill_style']
		color_line=self.usedefaults.parameters['color_line']
		color_fill=self.usedefaults.parameters['color_fill'] 
		color_edge=self.usedefaults.parameters['color_edge'] 
		edge_visible=self.usedefaults.parameters['edge_visible'] 
		self.debugPrint("C4_07 :", sw, len(upoints), fill_style, color_line, color_fill, color_edge , edge_visible) 
		# if len(upoints) >= 500: print "FILLED POLYGON", color_line, color_fill, color_edge, sw
		self.pdfOut.addPolyLine(polygon=1, stroke=color_line, strokewidth=sw, points=upoints,
				fill_style=fill_style,edge_visible = edge_visible, 
				color_fill = color_fill,  strokedasharray=self.usedefaults.parameters['stroke_dasharray']);
		#self.pdfOut.addPolyLine(polygon=1,stroke=self.usedefaults.parameters['color_line'],
			#color_fill=self.usedefaults.parameters['color_fill'], strokewidth=sw, points=upoints);

	def c4_08(self,record,fd): self.dummyReader(fd,record)
	def c4_09(self,record,fd): 
		self.dummyReader(fd,record)
		usefmt = "%s6f3H" % self.usedefaults.os_prelude 
		upoints = unpack(usefmt,record.buffer[:30])  # Get the length
		inx  = 32 
		bufferlen = len(record.buffer)
		rlen_fmt = "%sH" % self.usedefaults.os_prelude 
		color_fmt = "%s3B" % self.usedefaults.os_prelude 
		#print "c4_09", len(record.buffer) , upoints
		ncols = upoints[6]                   # Number of columns
		ncols3 = ncols * 3                   # Number of RGB triplets per row
		nrows = upoints[7] 	             # Number of rows 
		row = 0                              # First row.
		imageData = array.array('B')         # Array of integers. ?? 
		rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0]  #  Get the first run length 
		inx += 2 
		for row in xrange(nrows):            # 
			rowdata = [] 
			col     = 0 
			while col < ncols3: 
				#----------------------------------------------------------------
				r,g,b = unpack(color_fmt,record.buffer[inx:inx+3])  # Get the color
				inx += 3 
				rowdata.extend([r,g,b] * rlen)
				#if row < 4: print row, col, "(", r, g, b, ")*", rlen, ncols3, inx, len(rowdata)
				col = len(rowdata)                                  # How many pixels do we have? 
			
				if col >= ncols3:                                   # Enough 
					if col > ncols3:                                   # Enough 
						print "---------------->column exceeed", row, col
						rowdata = rowdata[:ncols3]                  # Truncate the rest. 
					if inx % 2 == 1:                            # Skip to next word boundary if needed.
						inx += 1                            # skip to word boundary at row end
						break
				else:
					if inx >= bufferlen: break
					rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0] # Read next record. 
					inx += 2 
			imageData.fromlist(rowdata)
			#if row < 4: print "Row ", row, " length", len(imageData) , inx
			if inx >= bufferlen: break
			rlen = unpack(rlen_fmt,record.buffer[inx:inx+2])[0] # Read next record. 
			inx += 2 
		#print "Image length", len(imageData.tostring()) 
		image = Image.fromstring("RGB",(ncols,nrows),imageData.tostring()) 
		# ---------------------- Location on screen. ------------------------------
		x = upoints[0];
		y = upoints[1]; 
		width  = upoints[2] - x; 
		height = upoints[3] - y; 
		self.pdfOut.addImage(self.imageId,image,x,y,width,height,units="in")
		self.imageId += 1
		
	def c4_10(self,record,fd): self.dummyReader(fd,record)
	def c4_11(self,record,fd): 
		#self.dummyReader(fd,record) 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		color_fill = self.usedefaults.parameters['color_fill'] 
		if self.usedefaults.parameters['edge_visible'] != 0:
			color_edge =self.usedefaults.parameters['color_edge']
		else:
			color_edge ="none" 
		self.debugPrint("Rectangle" 	)
		self.pdfOut.addRectangle("Rectangle",x1,y2,x2-x1,y2-y1,units="in",
			stroke_color=color_edge,
			strokewidth=self.usedefaults.parameters['edge_width'], 
			color_fill=color_fill, 
			fill_style=self.usedefaults.parameters['fill_style'])
		return	
		
	def c4_12(self,record,fd): 
		self.debugPrint("CIRCLE" 	)
		self.dummyReader(fd,record)
	def c4_13(self,record,fd): self.dummyReader(fd,record)
	def c4_14(self,record,fd): self.dummyReader(fd,record)
	def c4_15(self,record,fd): self.dummyReader(fd,record)
	def c4_16(self,record,fd): self.dummyReader(fd,record)
	def c4_17(self,record,fd): self.dummyReader(fd,record)
	def c4_18(self,record,fd): self.dummyReader(fd,record)
	def c4_19(self,record,fd): self.dummyReader(fd,record)
	def c4_20(self,record,fd): self.dummyReader(fd,record)
	def c4_21(self,record,fd): self.dummyReader(fd,record)
	def c4_22(self,record,fd): 
		f = record.parmslen / 2; 
		for x in range(f): self.debugPrint("4_22 %04x" % record.readInt(fd)   )
	def c4_23(self,record,fd): self.dummyReader(fd,record)
	def c4_24(self,record,fd): self.dummyReader(fd,record)
	def c4_25(self,record,fd): self.dummyReader(fd,record)
	def c4_26(self,record,fd): self.dummyReader(fd,record)
	def c4_27(self,record,fd): self.dummyReader(fd,record)
	def c4_28(self,record,fd): self.dummyReader(fd,record)
	def c4_29(self,record,fd): self.dummyReader(fd,record)

	# --------------- CLASS 5 Functions --------------------------------

	def c5_01(self,record,fd): 
		self.dummyReader(fd,record)
	def c5_02(self,record,fd):
		self.usedefaults.parameters['line_type']       =   record.readInt(fd)   
		self.debugPrint("Line Type:%04x" % self.usedefaults.parameters['line_type'] )
		self.usedefaults.parameters['stroke_dasharray'] = []
		if self.usedefaults.parameters['line_type'] == 1: self.usedefaults.parameters['stroke_dasharray'] = []
		if self.usedefaults.parameters['line_type'] == 2: self.usedefaults.parameters['stroke_dasharray'] = [5, 2]
		if self.usedefaults.parameters['line_type'] == 3: self.usedefaults.parameters['stroke_dasharray'] = [1, 1]
		if self.usedefaults.parameters['line_type'] == 4: self.usedefaults.parameters['stroke_dasharray'] = [5, 2]
		if self.usedefaults.parameters['line_type'] == 5: self.usedefaults.parameters['stroke_dasharray'] = [4, 1, 1]
		
	def c5_03(self,record,fd): 
		self.usedefaults.parameters['line_width']       =   record.readFloat(fd) 
		self.debugPrint("Line Width " , self.usedefaults.parameters['line_width']       )
	def c5_04(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_line'] = [r,g,b]
		self.debugPrint("Line color = ", self.usedefaults.parameters['color_line'])
	def c5_05(self,record,fd): self.dummyReader(fd,record)
	def c5_06(self,record,fd): self.dummyReader(fd,record)
	def c5_07(self,record,fd): self.dummyReader(fd,record)
	def c5_08(self,record,fd): self.dummyReader(fd,record)
	def c5_09(self,record,fd): self.dummyReader(fd,record)
	def c5_10(self,record,fd): 
		self.debugPrint("Text Precision Factor")
		self.dummyReader(fd,record)
	def c5_11(self,record,fd): 
		self.debugPrint("Text Precision Factor")
		self.dummyReader(fd,record)
	def c5_12(self,record,fd): 
		self.debugPrint("Character Expansion Factor")
		self.dummyReader(fd,record)
	def c5_13(self,record,fd): 
		self.debugPrint("Character Spacing")
		self.dummyReader(fd,record)
	def c5_14(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_text'] = [r,g,b]
	def c5_15(self,record,fd):
		self.usedefaults.parameters['char_height'] = record.readFloat(fd) 
		self.debugPrint("Character_Height: ", self.usedefaults.parameters['char_height'] )
	def c5_16(self,record,fd): 
		self.debugPrint("Character Orientation")
		#--self.dummyReader(fd,record)
		v1 = record.readFloat(fd)
		v2 = record.readFloat(fd)
		v3 = record.readFloat(fd)
		v4 = record.readFloat(fd)
		self.debugPrint("%f %f %f %f" % (v1,v2,v3,v4))

		self.usedefaults.parameters['rotate'] = None 
		if (v1 == 1) and (v2 == 0) and (v3 == 0.0) and (v4 == -1.0): 
			self.usedefaults.parameters['rotate'] = [v1,v2,v3,v4] 

	def c5_17(self,record,fd): 
		self.debugPrint("Text Path:%04x" % record.readInt(fd)   )
	def c5_18(self,record,fd): 
		hr = record.readInt(fd)   
		if hr == 3 : self.usedefaults.parameters['text_anchor'] = 'end'
		elif hr == 2: self.usedefaults.parameters['text_anchor'] = 'middle'
		else:  self.usedefaults.parameters['text_anchor'] = 'start'
		self.horizontal_alignment =  hr
		self.vertical_alignment = record.readInt(fd)   
		self.horizontal_C_alignment = record.readInt(fd)   
		self.vertical_C_alignment = record.readInt(fd)   
		self.debugPrint("Horizontal_Text_Alignment: %04x" % hr )
		self.debugPrint("Vertical_Text_Alignment: %04x" % self.vertical_alignment )
		self.debugPrint("Horizontal_C_Text_Alignment: %04x" %  self.horizontal_C_alignment) 
		self.debugPrint("Vertical C_Text_Alignment: %04x" %  self.vertical_C_alignment) 
	def c5_19(self,record,fd): self.dummyReader(fd,record)
	def c5_20(self,record,fd): self.dummyReader(fd,record)
	def c5_21(self,record,fd): self.dummyReader(fd,record)
	def c5_22(self,record,fd): 
		f = record.readInt(fd)   
		self.usedefaults.parameters['fill_style'] = "none" 
		if f == 1: self.usedefaults.parameters['fill_style'] = "solid" 
		if f == 2: self.usedefaults.parameters['fill_style'] = "pattern" 
		if f == 3: self.usedefaults.parameters['fill_style'] = "hatched" 
		if f == 4: self.usedefaults.parameters['fill_style'] = "none" 
		#print "c5_22", self.usedefaults.parameters['fill_style'] 
	def c5_23(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_fill'] =  [r,g,b] 
		self.debugPrint("Fill color", self.usedefaults.parameters['color_fill'] )
	def c5_24(self,record,fd): self.dummyReader(fd,record)
	def c5_25(self,record,fd): 
		f = record.readInt(fd)   
		self.usedefaults.parameters['pattern_index'] = f
		#print "c5_25", self.usedefaults.parameters['pattern_index'] 
	def c5_26(self,record,fd): self.debugPrint("Edge Bundle Index"); self.dummyReader(fd,record)
	def c5_27(self,record,fd): self.debugPrint("Edge Type") ; self.dummyReader(fd,record)
	def c5_28(self,record,fd): 
		self.usedefaults.parameters['edge_width'] = record.readFloat(fd)   
	def c5_29(self,record,fd): 
		r =  record.readByte(fd)   
		g =  record.readByte(fd)   
		b =  record.readByte(fd)   
		self.usedefaults.parameters['color_edge'] =  [r,g,b] 
		self.debugPrint("Edge color", self.usedefaults.parameters['color_edge'] )
	def c5_30(self,record,fd): 
		self.usedefaults.parameters['edge_visible'] = record.readInt(fd)   
		self.debugPrint("Edge visible" ,  self.usedefaults.parameters['edge_visible'] )
		#print "Edge Visible  Mode: ", self.usedefaults.parameters['edge_visible'] 
	def c5_31(self,record,fd): self.dummyReader(fd,record)
	def c5_32(self,record,fd): 
		self.dummyReader(fd,record)
		usefmt  = "%s%dH" % (self.usedefaults.os_prelude, 4)
		patternIndex,nx,ny,precision = unpack(usefmt,record.buffer[:8]) 
		#print "c5_32 size = ", len(record.buffer) , " as ",  patternIndex,nx,ny,precision 
	def c5_33(self,record,fd): 
		x1 =  record.readFloat(fd)   
		y1 =  record.readFloat(fd)   
		x2 =  record.readFloat(fd)   
		y2 =  record.readFloat(fd)   
		#print "c5_33 items  = ", x1,y1,x2,y2
	def c5_34(self,record,fd): self.dummyReader(fd,record)
	def c5_35(self,record,fd): self.dummyReader(fd,record)
	def c5_36(self,record,fd): self.dummyReader(fd,record)
	def c5_37(self,record,fd): self.dummyReader(fd,record)
	def c5_38(self,record,fd): self.dummyReader(fd,record)
	def c5_39(self,record,fd): self.dummyReader(fd,record)
	def c5_40(self,record,fd): self.dummyReader(fd,record)
	def c5_41(self,record,fd): self.dummyReader(fd,record)
	def c5_42(self,record,fd): self.dummyReader(fd,record)
	def c5_43(self,record,fd): self.dummyReader(fd,record)
	def c5_44(self,record,fd): self.dummyReader(fd,record)
	def c5_45(self,record,fd): self.dummyReader(fd,record)
	def c5_46(self,record,fd): self.dummyReader(fd,record)
	def c5_47(self,record,fd): self.dummyReader(fd,record)
	def c5_48(self,record,fd): self.dummyReader(fd,record)
	def c5_49(self,record,fd): self.dummyReader(fd,record)
	def c5_50(self,record,fd): self.dummyReader(fd,record)
	def c5_51(self,record,fd): self.dummyReader(fd,record)
	def c5_83(self,record,fd): self.dummyReader(fd,record)
	def c5_99(self,record,fd): self.dummyReader(fd,record)
	def c5_123(self,record,fd): self.dummyReader(fd,record)
	
	def c6_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
        def c6_10(self,record,fd): self.dummyReader(fd,record)
 
	def c6_13(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_43(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_48(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_59(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_67(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_72(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_75(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_99(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c6_112(self,record,fd): record.readCGMstring(fd,record.parmslen)

	def c7_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_02(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_03(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_27(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_35(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_51(self,record,fd):  self.dummyReader(fd,record)

	def c8_25(self,record,fd):  self.dummyReader(fd,record)
	def c8_50(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c8_97(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c8_108(self,record,fd): record.readCGMstring(fd,record.parmslen)

	def c9_87(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c10_121(self,record,fd):  self.dummyReader(fd,record)
	def c12_1(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_2(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_3(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_4(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c12_5(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c13_9(self,record,fd):  self.dummyReader(fd,record)
	def c13_97(self,record,fd):  self.dummyReader(fd,record)
	def c15_78(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c15_105(self,record,fd):  self.dummyReader(fd,record)
        
	def c15_120(self,record,fd): record.readCGMstring(fd,record.parmslen)
	#----------------------  Functions --------------
	def dummyReader(self,fd,record): record.readCGMstring(fd,record.parmslen)
		#self.debugPrint(record.elementClass,record.elementID, record.parmslen

	#----------------------  Functions --------------
	def readRecord(self,fd,record):
		record.readCommand(fd)      # Sets the padding 
		record.showInfo()                  # DEBUG
		self.processCommand(fd,record)     # The record will read 
		if record.padding == 1:
			## DANGER  #self.debugPrint("Padding at [%04x] " % fd.tell(), "Char = ", record.readByte(fd) )
			#fd.read(1) # Skip the pad bye immediately
			record.readByte(fd) 
			pass
		if record.elementClass == 0 and record.elementID == 2: return 0
		return 1		

	#---------------------- Command processing  --------------
	def processCommand(self,fd,record):
		if 1:
			self.cgm_classes[record.elementClass][record.elementID](record,fd)
			return 
		if 1:
			print "BAD OPCODE", record.elementClass, record.elementID, record.parmslen 
			self.dummyReader(fd,record)
			pass
			

htmlHolder="""
<html> 

<head>

</head> 
<body>
	<embed src="%(filename)s" width="90%%" height="90%%" />
</body>
</html>
"""

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
	#if len(sys.argv) < 2: 
		#usage()
		#sys.exit(0)

	try:
		opts, alen = getopt.getopt(sys.argv[2:], 'c:f:') 
	except:
		usage()
		sys.exit(0)
	optin = {} 

	for k,v in opts: 
		#print k,v
		optin[k] = v 


	#--------------------------------- how to process 
	os_prelude = ">"
	code = optin.get('-c', '0')
	if code == '0': 
		os_prelude = ">"
	else:
		os_prelude = "<"

	#--------------------------------- where to write 
	outputfilename = optin.get('-f','tmp.pdf') 
	inputfilename  = sys.argv[1]

	#print "OPTS", opts, alen
	#print "Input  filename", inputfilename 
	#print "Output filename", outputfilename 
	#print "Output prelude ", os_prelude 

	#------------------------------------------------------------------------------
	# THE FOLLOWING ARE RESET WHEN PRECISION IS READ FROM HEADER
	#------------------------------------------------------------------------------
	xx = cgmFileReader(cgmParameters(os_prelude))
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
	
	dict = { 'filename':outputfilename, } 
	fd = open(outputfilename+".html",'w')
	fd.write(htmlHolder % dict) 
	fd.close() 
	

>>>>>>> 1ea121057ce441ebcc5eda14b3ac6324de2ef8b4
