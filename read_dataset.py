import random

lines=[]

x_input=[]
y_output=[]

X_letter_size = []
X_line_spacing = []
X_word_spacing = []
X_pen_pressure = []

def read_dataset_funct():
    
    file1 = open('label_list.txt', 'r') 
    count = 0
      
    while True: 
        count += 1
        line = file1.readline() 
        if not line: 
            break
        lines.append(line)
  
    file1.close()
    
    random.shuffle(lines)

    
    for l in lines:
        x=[]
        y=[]
        content=l.split()
        
        letter_size = float(content[2])
        x.append(letter_size)
        
        line_spacing = float(content[3]) 
        x.append(line_spacing)

        word_spacing = float(content[4])
        x.append(word_spacing)

        pen_pressure = float(content[5])
        x.append(pen_pressure)
        
        x_input.append(x)
        	
        trait_1 = float(content[8])
        y.append(trait_1)	
		
        trait_2 = float(content[10])
        y.append(trait_2)

        trait_3 = float(content[12])
        y.append(trait_3)

        trait_4 = float(content[13])
        y.append(trait_4)
			
        trait_5 = float(content[14])
        y.append(trait_5)
        
        y_output.append(y)
        
        
    return (x_input,y_output)