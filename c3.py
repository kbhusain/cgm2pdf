
# Python command parser file 
import os,sys , copy
from struct import *
from cgmdesc import *

class cgmParameters:
	def __init__(self):
		self.vdc_type     = 0;
		self.precision_integer  = 0; 
		self.precision_of_index  = 0; 
		self.precision_of_color  = 0; 
		self.precision_of_color_index  = 0; 
		self.max_color_index  = 255; 
		self.char_set_list =  ''
		self.precision_of_name = 8
		self.char_coding  = 1 
		self.vdc_integer  = 0 
		self.vdc_realprec = 4
		self.vdc_p1       = 0   
		self.vdc_p2       = 16   
		self.vdc_p3       = 16   
		self.vdc_intprec  = 2
		self.enum_prec    = 2;
		self.rgb_p1       = 0;   
		self.rgb_p2       = 16;   
		self.rgb_p3       = 16;   
		self.fonts_list   = ''

class cgmRecord: 
	def __init__(self,defaults,id=0):
		self.cmd = None
		self.defaults = defaults
		self.ID =id
		self.elementClass = None
		self.elementID=None
		self.parameters = ''
		self.parmslen = 0
		self.padding  = 0
		self.opcodes = None # Could include drawing primitives, etc. 
		self.myBuffer  =  ''

	def readCommand(self,fd):
		# print "At [ %04x ] " %  fd.tell(), 
		buf = fd.read(2)                      # At location!
		cmd = unpack(fmt_wordString,buf)[0]   # I am using a global, yuck.
		self.cmd = cmd                        # Copy of the local 
		self.elementClass = (cmd >> 12) & 0xF; 
		self.elementID    = (cmd >> 5) & 0x7f;
		self.parmslen 	  = cmd & 0x1f;
		if self.parmslen == 31:
			buf = fd.read(2)
			p = unpack(fmt_wordString,buf)[0]  # Get the length
			self.padding  = p & 0x8000
			self.parmslen = p & 0x7FFF
		self.leftToRead = self.parmslen
		self.padding = self.parmslen & 1;

	def readParameters(self,fd):
		# print "Reading [", self.parmslen, "]" 
		self.parameters = fd.read(self.parmslen)
		
	def readCGMstring(self,fd,ilen=0):
		if ilen == 0: 
			buf = fd.read(1)                     # Get segment length
			slen = unpack(fmt_byteString,buf)[0] # 
		else:
			slen = ilen
		self.leftToRead -= slen;
		self.myBuffer = fd.read(slen)
		#print "Reading ", slen, " characters and leftToRead = ", self.leftToRead, len(self.myBuffer)

	def readFloat(self,fd): 
		if (self.defaults.vdc_p3 == 23): 
			buf = fd.read(4)                     # Get segment lengthbb
			return unpack(fmt_floatString,buf)[0]
		if (self.defaults.vdc_p3 == 52): 
			buf = fd.read(8)                     # Get segment lengthbb
			return unpack(fmt_doubleString,buf)[0]
		if (self.defaults.vdc_p3 == 16): 
			buf = fd.read(4)                     # Get segment lengthbb
			i = unpack(fmt_longString,buf)[0]
			return float(i) /0x00010000; 
		if (self.defaults.vdc_p3 == 32): 
			buf = fd.read(8)                     # Get segment lengthbb
			i = unpack(fmt_doubleString,buf)[0]
			return double(i) /0x01000000; 
		return 0.0 	

	def readByte(self,fd): 
		buf = fd.read(1)                     # Get segment lengthbb
		return unpack(fmt_byteString,buf)[0]

	def readInt(self,fd): 
		buf = fd.read(2)                     # Get segment lengthbb
		return unpack(fmt_wordString,buf)[0]
		
	def readIntTriple(self,fd): 
		buf = fd.read(6)                     # Get segment lengthbb
		return unpack(fmt_3i,buf)
		
	def showInfo(self,level=0):
		print "Command [%04x] Class [%x] ID[%X] %d %d " % \
			(self.cmd,self.elementClass,self.elementID,self.parmslen, len(self.myBuffer))

	def showParameters(self):
		pass
		
class cgmFileReader:
	def __init__(self,usedefaults):
		self.usedefaults = usedefaults
		self.cmd   = None
		
		# Some defaults:
		self.vdc_type = 0


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
		#self.cgm_class0[10]  = self.c0_10
		#self.cgm_class0[11]  = self.c0_11
		#self.cgm_class0[12]  = self.c0_12
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

		self.cgm_class6 = {}
		self.cgm_class6[1] = self.c6_01 

		self.cgm_class7 = {}
		self.cgm_class7[1] = self.c7_01 
		self.cgm_class7[2] = self.c7_02 

		self.cgm_classes = { }
		self.cgm_classes[0] = self.cgm_class0
		self.cgm_classes[1] = self.cgm_class1
		self.cgm_classes[2] = self.cgm_class2
		self.cgm_classes[3] = self.cgm_class3
		self.cgm_classes[4] = self.cgm_class4
		self.cgm_classes[5] = self.cgm_class5
		self.cgm_classes[6] = self.cgm_class6
		self.cgm_classes[7] = self.cgm_class7

	# --------------- CLASS 0 Functions --------------------------------
	def c0_00(self,record,fd): pass 
	def c0_01(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_02(self,record,fd): pass
	def c0_03(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_04(self,record,fd): pass 
	def c0_05(self,record,fd): pass 
	def c0_06(self,record,fd): 
		record.readCGMstring(fd,record.parmslen)
	def c0_07(self,record,fd): pass 
	def c0_08(self,record,fd): pass 
	def c0_09(self,record,fd): pass 
	def c0_13(self,record,fd): 
		print "C_13:", record.elementClass,record.elementID, record.parmslen
		p1 = record.readInt(fd); 
	def c0_14(self,record,fd): pass 
	def c0_15(self,record,fd): pass 
	def c0_16(self,record,fd): pass 
	def c0_17(self,record,fd): pass 
	def c0_18(self,record,fd): pass 
	def c0_19(self,record,fd): 
		print "C0_19:", record.elementClass,record.elementID, record.parmslen
	 	record.readInt(fd)
	def c0_20(self,record,fd): pass
	def c0_21(self,record,fd): 
		print "File Description:", record.elementClass,record.elementID, record.parmslen
	def c0_22(self,record,fd): pass
	def c0_23(self,record,fd): pass

	
	# --------------- CLASS 1 Functions --------------------------------
	def c1_01(self,record,fd): 
		record.readParameters(fd)
		print "MetaFile Version:", record.elementClass,record.elementID
	def c1_02(self,record,fd): 
		print "File Description:", record.elementClass,record.elementID, record.parmslen
		record.readCGMstring(fd)
	
	def c1_03(self,record,fd): self.usedefaults.vdc_type = record.readInt(fd)
	def c1_04(self,record,fd): self.usedefaults.precision_integer = record.readInt(fd)
	def c1_05(self,record,fd):  
		self.usedefaults.vdc_p1, self.usedefaults.vdc_p2, self.usedefaults.vdc_p3 = record.readIntTriple(fd)   
	def c1_06(self,record,fd): self.usedefaults.precision_of_index = record.readInt(fd)
	def c1_07 (self,record,fd): self.usedefaults.precision_of_color = record.readInt(fd)
	def c1_08(self,record,fd): self.usedefaults.precision_of_color_index = record.readInt(fd)
	def c1_09 (self,record,fd): self.usedefaults.max_color_index = record.readInt(fd)
	def c1_10 (self,record,fd): 
		if record.parmslen == 6: 
			self.usedefaults.rgb_p1, self.usedefaults.rgb_p2, self.usedefaults.rgb_p3 = record.readIntTriple(fd)   
		if record.parmslen == 4: 
			self.usedefaults.rgb_p1  = record.readInt(fd)   
			self.usedefaults.rgb_p2  = record.readInt(fd)   
			self.usedefaults.rgb_p3  = 0
	def c1_11 (self,record,fd):  # C
		p1,p2,p3 = record.readIntTriple(fd)   
		#print "Cls,ID=", record.elementClass,record.elementID, p1,p2,p3
	def c1_12(self,record,fd):  # D
		#print "metaFileElements", record.elementClass,record.elementID, record.parmslen
		itemCounts = record.parmslen/2 
		for x in range(itemCounts): p1  = record.readInt(fd)   
	
	def c1_13(self,record,fd): 
		print "font list", record.elementClass,record.elementID, record.parmslen
		self.usedefaults.fonts_list = record.readCGMstring(fd,record.parmslen)
	def c1_14(self,record,fd): 
		self.usedefaults.char_set_list = record.readCGMstring(fd,record.parmslen)
	def c1_15(self,record,fd): self.usedefaults.char_coding  = record.readInt(fd)   
	def c1_16(self,record,fd): self.usedefaults.precision_of_name  = record.readInt(fd)   
	def c1_17(self,record,fd): 
		print "max vdc extent", record.elementClass,record.elementID, record.parmslen
	def c1_18(self,record,fd):
		print "seg priority extent", record.elementClass,record.elementID, record.parmslen
	def c1_19(self,record,fd): 
		print "color model", record.elementClass,record.elementID, record.parmslen
	def c1_20(self,record,fd):
		print "color calibration", record.elementClass,record.elementID, record.parmslen
	def c1_21(self,record,fd): 
		print "font properties", record.elementClass,record.elementID, record.parmslen
	def c1_22(self,record,fd): 
		print "glyph Mappging", record.elementClass,record.elementID, record.parmslen
	def c1_23(self,record,fd):
		print "symbol library", record.elementClass,record.elementID, record.parmslen
	def c1_24(self,record,fd): 
		print "picture directory", record.elementClass,record.elementID, record.parmslen
		
	# --------------- CLASS 2 Functions --------------------------------
	def c2_01_scalingMode(self,record,fd): 
		record.readIntTriple(fd)    # Actually, read in the points for the VDC 
	def c2_02_colorSelectionMode(self,record,fd): record.readInt(fd)   
	def c2_03_lineWidthSpecMode(self,record,fd): record.readInt(fd)   
	def c2_04_markerSizeSpecMode(self,record,fd): record.readInt(fd)   
	def c2_05_edgeWidthMode(self,record,fd): record.readInt(fd)   
	def c2_06_vdcExtent(self,record,fd):
		print "VDC extent = ", record.elementClass,record.elementID, record.parmslen
		f = record.parmslen / 2; 
		#for x in range(f): print "%04x" % record.readInt(fd)   
		for x in range(f): record.readInt(fd)   

	def c2_07_backgroundColor(self,record,fd): 
		print "Background = ", record.elementClass,record.elementID, record.parmslen
		record.readCGMstring(fd,record.parmslen)

	def c2_08_deviceViewport(self,record,fd): 
		print "Background = ", record.elementClass,record.elementID, record.parmslen
		record.readIntTriple(fd)    # Actually, read in the points for the VDC 
		record.readIntTriple(fd)   

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
		print "c2_20", record.elementClass,record.elementID, record.parmslen
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   
	def c3_01(self,record,fd): 
		self.dummyReader(fd,record)
	def c3_02(self,record,fd): 
		self.dummyReader(fd,record)
	def c3_03(self,record,fd):
		self.dummyReader(fd,record)
	def c3_04(self,record,fd):
		self.dummyReader(fd,record)
	def c3_05(self,record,fd):
		print "c3_05", record.elementClass,record.elementID, record.parmslen
		f = record.parmslen / 2; 
		for x in range(f): record.readInt(fd)   
	def c3_06(self,record,fd): self.dummyReader(fd,record)
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
		print "c3_22", record.elementClass,record.elementID, record.parmslen
		f = record.parmslen / 2; 
		for x in range(f): print "%04x" % record.readInt(fd)   


	# --------------- CLASS 4 Functions --------------------------------
	def c4_01(self,record,fd): 
		#self.dummyReader(fd,record)
		record.showInfo(0)
		if record.parmslen == 16:
			v1 = record.readFloat(fd)
			v2 = record.readFloat(fd)
			v3 = record.readFloat(fd)
			v4 = record.readFloat(fd)
			print v1,v2,v3,v4
		else:
			self.dummyReader(fd,record)
		return 
	def c4_02(self,record,fd): self.dummyReader(fd,record)
	def c4_03(self,record,fd): self.dummyReader(fd,record)
	def c4_04(self,record,fd): 
		self.dummyReader(fd,record)
		#record.showInfo(1)
		#if len(record.myBuffer)> 4: 
		#	ostr = ">hhhhh"
		#	print "hello", fmt_longString, len(record.myBuffer)
		#	print "%04x, %04x, %04x, %04x %04x" % unpack(ostr,record.myBuffer[0:10])

	def c4_05(self,record,fd): self.dummyReader(fd,record)
	def c4_06(self,record,fd): self.dummyReader(fd,record)
	def c4_07(self,record,fd):self.dummyReader(fd,record)
	def c4_08(self,record,fd): self.dummyReader(fd,record)
	def c4_09(self,record,fd): self.dummyReader(fd,record)
	def c4_10(self,record,fd): self.dummyReader(fd,record)
	def c4_11(self,record,fd): self.dummyReader(fd,record)
	def c4_12(self,record,fd): self.dummyReader(fd,record)
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
		for x in range(f): print "4_22 %04x" % record.readInt(fd)   
	def c4_23(self,record,fd): self.dummyReader(fd,record)
	def c4_24(self,record,fd): self.dummyReader(fd,record)
	def c4_25(self,record,fd): self.dummyReader(fd,record)
	def c4_26(self,record,fd): self.dummyReader(fd,record)
	def c4_27(self,record,fd): self.dummyReader(fd,record)
	def c4_28(self,record,fd): self.dummyReader(fd,record)
	def c4_29(self,record,fd): self.dummyReader(fd,record)

	# --------------- CLASS 5 Functions --------------------------------

	def c5_01(self,record,fd): self.dummyReader(fd,record)
	def c5_02(self,record,fd): self.dummyReader(fd,record)
	def c5_03(self,record,fd): self.dummyReader(fd,record)
	def c5_04(self,record,fd): self.dummyReader(fd,record)
	def c5_05(self,record,fd): self.dummyReader(fd,record)
	def c5_06(self,record,fd): self.dummyReader(fd,record)
	def c5_07(self,record,fd):self.dummyReader(fd,record)
	def c5_08(self,record,fd): self.dummyReader(fd,record)
	def c5_09(self,record,fd): self.dummyReader(fd,record)
	def c5_10(self,record,fd): self.dummyReader(fd,record)
	def c5_11(self,record,fd): self.dummyReader(fd,record)
	def c5_12(self,record,fd): self.dummyReader(fd,record)
	def c5_13(self,record,fd): self.dummyReader(fd,record)
	def c5_14(self,record,fd): self.dummyReader(fd,record)
	def c5_15(self,record,fd): self.dummyReader(fd,record)
	def c5_16(self,record,fd): self.dummyReader(fd,record)
	def c5_17(self,record,fd): 
		print "%04x" % record.readInt(fd)   
	def c5_18(self,record,fd): self.dummyReader(fd,record)
	def c5_19(self,record,fd): self.dummyReader(fd,record)
	def c5_20(self,record,fd): self.dummyReader(fd,record)
	def c5_21(self,record,fd): self.dummyReader(fd,record)
	def c5_22(self,record,fd): 
		f = record.parmslen / 2; 
		for x in range(f): print "%04x" % record.readInt(fd)   
	def c5_23(self,record,fd): self.dummyReader(fd,record)
	def c5_24(self,record,fd): self.dummyReader(fd,record)
	def c5_25(self,record,fd): self.dummyReader(fd,record)
	def c5_26(self,record,fd): self.dummyReader(fd,record)
	def c5_27(self,record,fd): self.dummyReader(fd,record)
	def c5_28(self,record,fd): self.dummyReader(fd,record)
	def c5_29(self,record,fd): self.dummyReader(fd,record)
	def c5_30(self,record,fd): self.dummyReader(fd,record)
	def c5_31(self,record,fd): self.dummyReader(fd,record)
	def c5_32(self,record,fd): self.dummyReader(fd,record)
	def c5_33(self,record,fd): self.dummyReader(fd,record)
	def c5_34(self,record,fd): self.dummyReader(fd,record)
	def c5_35(self,record,fd): self.dummyReader(fd,record)
	def c5_36(self,record,fd): self.dummyReader(fd,record)
	def c5_37(self,record,fd):self.dummyReader(fd,record)
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
	
	def dummyReader(self,fd,record):
		return record.readCGMstring(fd,record.parmslen)
		#print record.elementClass,record.elementID, record.parmslen

	def c6_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_01(self,record,fd): record.readCGMstring(fd,record.parmslen)
	def c7_02(self,record,fd): record.readCGMstring(fd,record.parmslen)
	#---------------------- Reading Functions --------------
	def readRecord(self,fd,record):
		record.readCommand(fd)      # Sets the padding 
		#record.showInfo()                  # DEBUG
		self.processCommand(fd,record)     # The record will read 
		if record.padding == 1:
			# print "Padding at [%04x] " % fd.tell()
			fd.read(1) # Skip the pad bye immediately
		if record.elementClass == 0 and record.elementID == 2: return 0
		return 1		

	#---------------------- Command processing  --------------
	def processCommand(self,fd,record):
		if 1:
			self.cgm_classes[record.elementClass][record.elementID](record,fd)
			return 
		#except:
			#print "Class ", record.elementClass, " ************ Unknown ID = ", record.elementID, record.parmslen
			#sys.exit(0)
			#pass
			
				
if __name__ == '__main__':
	if len(sys.argv) < 3: 
		print "Usage: prog filename code"
		print "code = 0 for Windows origin file"
		print "code = 1 for Unix origin file"
		sys.exit(0)

	if sys.argv[2] == '0': 
		os_prelude = ">"
	else:
		os_prelude = "<"

	# These are global for this name space. 
	# Arrgh. 
	fmt_byteString = "%sB" % (os_prelude)
	fmt_wordString = "%sH" % (os_prelude)
	fmt_3i = "%s3h" % (os_prelude)
	fmt_shortString = "%sh" % (os_prelude)
	fmt_floatString = "%sf" % (os_prelude)
	fmt_doubleString = "%sd" % (os_prelude)
	fmt_longString = "%sI" % (os_prelude)
	fd = open (sys.argv[1],'rb')
	myrecords = [ ]
	pp = cgmParameters() 
	xx = cgmFileReader(pp)
	i = 0
	for i in range(100000): 
		mb = cgmRecord(pp,i)      # keep these in an arra
		r = xx.readRecord(fd,mb)
		if r == 0: break;
		i += 1;
	print 'EOF at ', i, fd.tell()
	fd.close()
