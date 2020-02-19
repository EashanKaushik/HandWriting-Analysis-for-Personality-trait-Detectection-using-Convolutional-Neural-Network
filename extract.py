import numpy as np
import cv2

ANCHOR_POINT = 6000
MIDZONE_THRESHOLD = 15000
MIN_HANDWRITING_HEIGHT_PIXEL = 20

LETTER_SIZE = 0.0
LINE_SPACING = 0.0
WORD_SPACING = 0.0
PEN_PRESSURE = 0.0

def bilateralFilter(image, d):
	image = cv2.bilateralFilter(image,d,50,50)
	return image
def medianFilter(image, d):
	image = cv2.medianBlur(image,d)
	return image
def threshold(image, t):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	ret,image = cv2.threshold(image,t,255,cv2.THRESH_BINARY_INV)
	return image

def dilate(image, kernalSize):
	kernel = np.ones(kernalSize, np.uint8)
	image = cv2.dilate(image, kernel, iterations=1)
	return image
	
def erode(image, kernalSize):
	kernel = np.ones(kernalSize, np.uint8)
	image = cv2.erode(image, kernel, iterations=1)
	return image
	
''' function for finding contours and straightening them horizontally
    Straightened lines will give better result with horizontal projections. '''
def straighten(image):

	
	angle = 0.0
		
	filtered = bilateralFilter(image, 3)

	thresh = threshold(filtered, 120)
	
	dilated = dilate(thresh, (5 ,100))
	
	ctrs,hier = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	for i, ctr in enumerate(ctrs):
		x, y, w, h = cv2.boundingRect(ctr)
		
		if h>w or h<MIN_HANDWRITING_HEIGHT_PIXEL:
			continue
		
		roi = image[y:y+h, x:x+w]
		
		if w < image.shape[1]/2 :
			roi = 255
			image[y:y+h, x:x+w] = roi
			continue

		rect = cv2.minAreaRect(ctr)
		angle = rect[2]

		if angle < -45.0:
			angle += 90.0;
			
		rot = cv2.getRotationMatrix2D(((x+w)/2,(y+h)/2), angle, 1)

		extract = cv2.warpAffine(roi, rot, (w,h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))

		image[y:y+h, x:x+w] = extract

	return image

''' function to calculate horizontal projection of the image pixel rows and return it '''
def horizontalProjection(img):

    (h, w) = img.shape[:2]
    sumRows = []
    for j in range(h):
        row = img[j:j+1, 0:w]
        sumRows.append(np.sum(row))
    return sumRows
	
''' function to calculate vertical projection of the image pixel columns and return it '''
def verticalProjection(img):
    (h, w) = img.shape[:2]
    sumCols = []
    for j in range(w):
        col = img[0:h, j:j+1] # y1:y2, x1:x2
        sumCols.append(np.sum(col))
    return sumCols
	
''' function to extract lines of handwritten text from the image using horizontal projection '''
def extractLines(img):

	global LETTER_SIZE
	global LINE_SPACING
	
	filtered = bilateralFilter(img, 5)
	
	thresh = threshold(filtered, 160)
	hpList = horizontalProjection(thresh)

	topMarginCount = 0
	for sum in hpList:
		if(sum<=255):
			topMarginCount += 1
		else:
			break
			
	lineTop = 0
	lineBottom = 0
	spaceTop = 0
	spaceBottom = 0
	indexCount = 0
	setLineTop = True
	setSpaceTop = True
	includeNextSpace = True
	space_zero = [] # stores the amount of space between lines
	lines = [] # a 2D list storing the vertical start index and end index of each contour
	
	# we are scanning the whole horizontal projection now
	for i, sum in enumerate(hpList):
		# sum being 0 means blank space
		if(sum==0):
			if(setSpaceTop):
				spaceTop = indexCount
				setSpaceTop = False # spaceTop will be set once for each start of a space between lines
			indexCount += 1
			spaceBottom = indexCount
			if(i<len(hpList)-1): # this condition is necessary to avoid array index out of bound error
				if(hpList[i+1]==0): # if the next horizontal projectin is 0, keep on counting, it's still in blank space
					continue
			# we are using this condition if the previous contour is very thin and possibly not a line
			if(includeNextSpace):
				space_zero.append(spaceBottom-spaceTop)
			else:
				if (len(space_zero)==0):
					previous = 0
				else:
					previous = space_zero.pop()
				space_zero.append(previous + spaceBottom-lineTop)
			setSpaceTop = True # next time we encounter 0, it's begining of another space so we set new spaceTop
		
		# sum greater than 0 means contour
		if(sum>0):
			if(setLineTop):
				lineTop = indexCount
				setLineTop = False # lineTop will be set once for each start of a new line/contour
			indexCount += 1
			lineBottom = indexCount
			if(i<len(hpList)-1): # this condition is necessary to avoid array index out of bound error
				if(hpList[i+1]>0): # if the next horizontal projectin is > 0, keep on counting, it's still in contour
					continue
					
				# if the line/contour is too thin <10 pixels (arbitrary) in height, we ignore it.
				# Also, we add the space following this and this contour itself to the previous space to form a bigger space: spaceBottom-lineTop.
				if(lineBottom-lineTop<20):
					includeNextSpace = False
					setLineTop = True # next time we encounter value > 0, it's begining of another line/contour so we set new lineTop
					continue
			includeNextSpace = True # the line/contour is accepted, new space following it will be accepted
			
			# append the top and bottom horizontal indices of the line/contour in 'lines'
			lines.append([lineTop, lineBottom])
			setLineTop = True # next time we encounter value > 0, it's begining of another line/contour so we set new lineTop
	
	
	# SECOND we extract the very individual lines from the lines/contours we extracted above.
	fineLines = [] # a 2D list storing the horizontal start index and end index of each individual line
	for i, line in enumerate(lines):
	
		anchor = line[0] # 'anchor' will locate the horizontal indices where horizontal projection is > ANCHOR_POINT for uphill or < ANCHOR_POINT for downhill(ANCHOR_POINT is arbitrary yet suitable!)
		anchorPoints = [] # python list where the indices obtained by 'anchor' will be stored
		upHill = True # it implies that we expect to find the start of an individual line (vertically), climbing up the histogram
		downHill = False # it implies that we expect to find the end of an individual line (vertically), climbing down the histogram
		segment = hpList[line[0]:line[1]] # we put the region of interest of the horizontal projection of each contour here
		
		for j, sum in enumerate(segment):
			if(upHill):
				if(sum<ANCHOR_POINT):
					anchor += 1
					continue
				anchorPoints.append(anchor)
				upHill = False
				downHill = True
			if(downHill):
				if(sum>ANCHOR_POINT):
					anchor += 1
					continue
				anchorPoints.append(anchor)
				downHill = False
				upHill = True
				
		#print anchorPoints
		
		# we can ignore the contour here
		if(len(anchorPoints)<2):
			continue
		
		# len(anchorPoints) > 3 meaning contour composed of multiple lines
		lineTop = line[0]
		for x in range(1, len(anchorPoints)-1, 2):
			# 'lineMid' is the horizontal index where the segmentation will be done
			lineMid = (anchorPoints[x]+anchorPoints[x+1])/2
			lineBottom = lineMid
			# line having height of pixels <20 is considered defects, so we just ignore it
			# this is a weakness of the algorithm to extract lines (anchor value is ANCHOR_POINT, see for different values!)
			if(lineBottom-lineTop < 20):
				continue
			fineLines.append([lineTop, lineBottom])
			lineTop = lineBottom
		if(line[1]-lineTop < 20):
			continue
		fineLines.append([lineTop, line[1]])
		
	# LINE SPACING and LETTER SIZE will be extracted here
	# We will count the total number of pixel rows containing upper and lower zones of the lines and add the space_zero/runs of 0's(excluding first and last of the list ) to it.
	# We will count the total number of pixel rows containing midzones of the lines for letter size.
	# For this, we set an arbitrary (yet suitable!) threshold MIDZONE_THRESHOLD = 15000 in horizontal projection to identify the midzone containing rows.
	# These two total numbers will be divided by number of lines (having at least one row>MIDZONE_THRESHOLD) to find average line spacing and average letter size.
	space_nonzero_row_count = 0
	midzone_row_count = 0
	lines_having_midzone_count = 0
	flag = False
	for i, line in enumerate(fineLines):
		segment = hpList[int(line[0]):int(line[1])]
		for j, sum in enumerate(segment):
			if(sum<MIDZONE_THRESHOLD):
				space_nonzero_row_count += 1
			else:
				midzone_row_count += 1
				flag = True
				
		# This line has contributed at least one count of pixel row of midzone
		if(flag):
			lines_having_midzone_count += 1
			flag = False
	
	# error prevention ^-^
	if(lines_having_midzone_count == 0): lines_having_midzone_count = 1
	
	
	total_space_row_count = space_nonzero_row_count + np.sum(space_zero[1:-1]) #excluding first and last entries: Top and Bottom margins
	# the number of spaces is 1 less than number of lines but total_space_row_count contains the top and bottom spaces of the line
	average_line_spacing = float(total_space_row_count) / lines_having_midzone_count 
	average_letter_size = float(midzone_row_count) / lines_having_midzone_count
	# letter size is actually height of the letter and we are not considering width
	LETTER_SIZE = average_letter_size
	# error prevention ^-^
	if(average_letter_size == 0): average_letter_size = 1
	# We can't just take the average_line_spacing as a feature directly. We must take the average_line_spacing relative to average_letter_size.
	# Let's take the ratio of average_line_spacing to average_letter_size as the LINE SPACING, which is perspective to average_letter_size.
	relative_line_spacing = average_line_spacing / average_letter_size
	LINE_SPACING = relative_line_spacing
	
	return fineLines
	
''' function to extract words from the lines using vertical projection '''
def extractWords(image, lines):

	global LETTER_SIZE
	global WORD_SPACING
	
	# apply bilateral filter
	filtered = bilateralFilter(image, 5)
	
	# convert to grayscale and binarize the image by INVERTED binary thresholding
	thresh = threshold(filtered, 180)
	#cv2.imshow('thresh', wthresh)
	
	# Width of the whole document is found once.
	width = thresh.shape[1]
	space_zero = [] # stores the amount of space between words
	words = [] # a 2D list storing the coordinates of each word: y1, y2, x1, x2
	
	# Isolated words or components will be extacted from each line by looking at occurance of 0's in its vertical projection.
	for i, line in enumerate(lines):
		extract = thresh[int(line[0]):int(line[1]), 0:width] # y1:y2, x1:x2
		vp = verticalProjection(extract)
		#print i
		#print vp
		
		wordStart = 0
		wordEnd = 0
		spaceStart = 0
		spaceEnd = 0
		indexCount = 0
		setWordStart = True
		setSpaceStart = True
		spaces = []
		
		# we are scanning the vertical projection
		for j, sum in enumerate(vp):
			# sum being 0 means blank space
			if(sum==0):
				if(setSpaceStart):
					spaceStart = indexCount
					setSpaceStart = False # spaceStart will be set once for each start of a space between lines
				indexCount += 1
				spaceEnd = indexCount
				if(j<len(vp)-1): # this condition is necessary to avoid array index out of bound error
					if(vp[j+1]==0): # if the next vertical projectin is 0, keep on counting, it's still in blank space
						continue

				# we ignore spaces which is smaller than half the average letter size
				if((spaceEnd-spaceStart) > int(LETTER_SIZE/2)):
					spaces.append(spaceEnd-spaceStart)
					
				setSpaceStart = True # next time we encounter 0, it's begining of another space so we set new spaceStart
			
			# sum greater than 0 means word/component
			if(sum>0):
				if(setWordStart):
					wordStart = indexCount
					setWordStart = False # wordStart will be set once for each start of a new word/component
				indexCount += 1
				wordEnd = indexCount
				if(j<len(vp)-1): # this condition is necessary to avoid array index out of bound error
					if(vp[j+1]>0): # if the next horizontal projectin is > 0, keep on counting, it's still in non-space zone
						continue
				
				# append the coordinates of each word/component: y1, y2, x1, x2 in 'words'
				# we ignore the ones which has height smaller than half the average letter size
				# this will remove full stops and commas as an individual component
				count = 0
				for k in range(int(line[1])-int(line[0])):
					row = thresh[int(line[0])+k:int(line[0])+k+1, wordStart:wordEnd] # y1:y2, x1:x2
					if(np.sum(row)):
						count += 1
				if(count > int(LETTER_SIZE/2)):
					words.append([int(line[0]),int(line[1]), wordStart, wordEnd])
					
				setWordStart = True # next time we encounter value > 0, it's begining of another word/component so we set new wordStart
		
		space_zero.extend(spaces[1:-1])
	
	#print space_zero
	space_columns = np.sum(space_zero)
	space_count = len(space_zero)
	if(space_count == 0):
		space_count = 1
	average_word_spacing = float(space_columns) / space_count
	relative_word_spacing = average_word_spacing / LETTER_SIZE
	WORD_SPACING = relative_word_spacing
	#print "Average word spacing: "+str(average_word_spacing)
	#print ("Average word spacing relative to average letter size: "+str(relative_word_spacing))
	
	return words
def barometer(image):

	global PEN_PRESSURE

	# it's extremely necessary to convert to grayscale first
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# inverting the image pixel by pixel individually. This costs the maximum time and processing in the entire process!
	h, w = image.shape[:]
	inverted = image
	for x in range(h):
		for y in range(w):
			inverted[x][y] = 255 - image[x][y]
	
	#cv2.imshow('inverted', inverted)
	
	# bilateral filtering
	filtered = bilateralFilter(inverted, 3)
	
	# binary thresholding. Here we use 'threshold to zero' which is crucial for what we want.
	# If src(x,y) is lower than threshold=100, the new pixel value will be set to 0, else it will be left untouched!
	ret, thresh = cv2.threshold(filtered, 100, 255, cv2.THRESH_TOZERO)
	#cv2.imshow('thresh', thresh)
	
	# add up all the non-zero pixel values in the image and divide by the number of them to find the average pixel value in the whole image
	total_intensity = 0
	pixel_count = 0
	for x in range(h):
		for y in range(w):
			if(thresh[x][y] > 0):
				total_intensity += thresh[x][y]
				pixel_count += 1
				
	average_intensity = float(total_intensity) / pixel_count
	PEN_PRESSURE = average_intensity
	
	return

	
def start(file_name):

	global LETTER_SIZE
	global LINE_SPACING
	global WORD_SPACING
	global PEN_PRESSURE

	image = cv2.imread(r'D:\Users\Eashan\Desktop\NEURAL NETWORK/'+file_name)
	
	barometer(image)
   
	straightened = straighten(image)
	lineIndices = extractLines(straightened)
	wordCoordinates = extractWords(straightened, lineIndices)
	LETTER_SIZE = round(LETTER_SIZE, 2)
	LINE_SPACING = round(LINE_SPACING, 2)
	WORD_SPACING = round(WORD_SPACING, 2)
	PEN_PRESSURE = round(PEN_PRESSURE, 2)
    
	return [LETTER_SIZE, LINE_SPACING, WORD_SPACING, PEN_PRESSURE]
	
