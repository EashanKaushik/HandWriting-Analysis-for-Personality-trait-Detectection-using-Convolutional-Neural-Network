import numpy as np
import neural_network as nn
import read_dataset as rd
import categorize
import extract
import math

x_data=[]
y_data=[]

neural_network_trained = nn.NeuralNetwork()

print("Random starting synaptic weights: ")
print(neural_network_trained.synaptic_weights)
    
train_input=[]
train_output=[]
    
train_input,train_output=rd.read_dataset_funct()
        
neural_network_trained.train(train_input, train_output, 60000)

print("New synaptic weights after training: ")
print(neural_network_trained.synaptic_weights)

def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0) 


while(True):
    file_name = input("Enter file name to predict or z to exit: ")
    if file_name == 'z':
    	break
    			
    raw_features = extract.start(file_name)
    		
    raw_letter_size = raw_features[0]
    letter_size, comment = categorize.determine_letter_size(raw_letter_size)
    x_data.append(letter_size)
    print("Letter Size: "+comment)
    		
    raw_line_spacing = raw_features[1]
    line_spacing, comment = categorize.determine_line_spacing(raw_line_spacing)
    x_data.append(line_spacing)
    print("Line Spacing: "+comment)
    		
    raw_word_spacing = raw_features[2]
    word_spacing, comment = categorize.determine_word_spacing(raw_word_spacing)
    x_data.append(word_spacing)
    print("Word Spacing: "+comment)
    		
    raw_pen_pressure = raw_features[3]
    pen_pressure, comment = categorize.determine_pen_pressure(raw_pen_pressure)
    x_data.append(pen_pressure)
    print("Pen Pressure: "+comment)
    
    y_data=softmax(neural_network_trained.think(x_data))
    
    print()
    print("Mental Energy or Will Power: ",math.ceil(y_data[0]*100),"%")
    print("Personal Harmony and Flexibility: ",math.ceil(y_data[1]*100),"%")
    print("Poor Concentration: ",math.ceil(y_data[2]*100),"%")
    print("Non Communicativeness: ",math.ceil(y_data[3]*100),"%")
    print("Social Isolation: ",math.ceil(y_data[4]*100),"%")
    print("---------------------------------------------------")
    print()
    
    
