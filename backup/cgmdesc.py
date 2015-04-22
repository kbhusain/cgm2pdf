# cgm code descriptions 
cgm_0_desc = { 0: 'No-op', 1: 'BEGIN_METAFILE', 2 : "END METAFILE",
	3: 'BEGIN_PICTURE', 4: 'END_PICTURE_BODY', 5: 'END_PICTURE',
	6: 'BEGIN_SEGMENT', 7: "END_SEGMENT", 
	8: 'BEGIN_FIGURE',  9: "END_FIGURE", 
	13: 'BEGIN_PROTECTION_REGION',  14: "END_PROTECTION_REGION",
	15: 'BEGIN_COMPOUND_LINE',  16: "END_COMPOUND_LINE",
	17: 'BEGIN_COMPOUND_TEXT_PATH',  18: "END_COMPOUND_TEXT_PATH",
	19: 'BEGIN_TILE_ARRAY', 20: 'END_TILE_ARRAY',
	21: 'BEGIN_APPLICATION_STRUCTURE',
	22: 'BEGIN_APPLICATION_STRUCTURE_BODY',
	23: 'END_APPLICATION_STRUCTURE' }
cgm_1_desc = { 0: 'No-op', 1: 'METAFILE_VERSION', 2 : "METAFILE DESCRIPTION",
	3: 'VDC_TYPE', 4: 'INTEGER_PRECISION', 5: 'REAL PRECISION', 6: 'INDEX', 7: 'COLOR',
	8: 'COLOR INDEX', 9: 'max color', 10: 'color value', 
	11: 'Meta file elements list', 12: 'Meta file defaults replacements',
	13: 'fonts list', 14: 'character list', 15: 'character coding announcer', 
	16: 'Name precision', 17: 'Max VDC extent', 18: 'Segment prioriy extent',
	19: 'Color model', 20: 'Color calibration', 21: 'Font Properties', 
	22: 'Glyph Mapping', 23: 'Symbol library list' }
cgm_2_desc = { 0: 'No-op', 1: 'SCALING_MODE', 2 : "COLOR_SELECTION_MODE",
	3: 'LINE_WIDTH', 4: 'MARKER_SIZE specification', 
	5: 'Edge Width', 6: 'VDC Extent', 7: 'Background color',
	8: 'Device Viewport', 9: 'Device Veiwport specification mode', 
	10: 'Device Viewport Mapping', 11: 'Line Representation', 
	12: 'Marker Representation', 13: 'Text Representation', 
	14: 'Fill Representation', 15: 'Edge Representation', 
	16: 'Interior Style Representation', 17: 'Line and Edge Type Detection', 
	18: 'Hatch Style', 19: 'Geometric Pattern', 20: "Application Struct Dir" }
	
	 
cgmDescribe = []
cgmDescribe.append(cgm_0_desc)
cgmDescribe.append(cgm_1_desc)
cgmDescribe.append(cgm_2_desc)
 
def showInfo(cl,idx):
	try:
		print "%d, %d, %s" % (cl,idx,cgmDescribe[cl][idx])
	except: 
		print "%d, %d, %s" % (cl,idx,"Not defined yet")

 		
