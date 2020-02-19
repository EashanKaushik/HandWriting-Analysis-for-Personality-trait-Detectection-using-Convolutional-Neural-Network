def determine_letter_size(raw_letter_size):
	comment = ""
	# big
	if(raw_letter_size >= 18.0):
		letter_size = 0
		comment = "BIG"
	# small
	elif(raw_letter_size < 13.0):
		letter_size = 1
		comment = "SMALL"
	# medium
	else:
		letter_size = 2
		comment = "MEDIUM"
		
	return letter_size, comment

def determine_line_spacing(raw_line_spacing):
	comment = ""
	# big
	if(raw_line_spacing >= 3.5):
		line_spacing = 0
		comment = "BIG"
	# small
	elif(raw_line_spacing < 2.0):
		line_spacing = 1
		comment = "SMALL"
	# medium
	else:
		line_spacing = 2
		comment = "MEDIUM"
		
	return line_spacing, comment

def determine_word_spacing(raw_word_spacing):
	comment = ""
	# big
	if(raw_word_spacing > 2.0):
		word_spacing = 0
		comment = "BIG"
	# small
	elif(raw_word_spacing < 1.2):
		word_spacing = 1
		comment = "SMALL"
	# medium
	else:
		word_spacing = 2
		comment = "MEDIUM"
		
	return word_spacing, comment

def determine_pen_pressure(raw_pen_pressure):
	comment = ""
	# heavy
	if(raw_pen_pressure > 180.0):
		pen_pressure = 0
		comment = "HEAVY"
	# light
	elif(raw_pen_pressure < 151.0):
		pen_pressure = 1
		comment = "LIGHT"
	# medium
	else:
		pen_pressure = 2
		comment = "MEDIUM"
		
	return pen_pressure, comment

