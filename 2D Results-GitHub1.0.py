#!/usr/bin/env python
# coding: utf-8

# In[20]:


import codecs
import shutil
import numpy as np
import pandas as pd 


# ### CTan Morphometry Results 2D
# ##### Author: Anna Valentine (annavalentine@mines.edu)
# #### Date: 07/19/21
# 
# #### Purpose:  
# Takes in Ctan/batman files from microCT and concatonates the 2D results from the snowpit into one dataframe. This is meant for one snowpit at a time. 

# In[21]:


# Write down my standard path here
path = '/Users/annav/1_WORK_CRREL/CTan Project 1/' 
files = path+'Data/*.txt'  
UTF8_folder = path + 'D_UTF8/'   # set up a folder for UTF8 conversion


# In[22]:


#general takes a path and spits out all of the file names 
def list_files_local(path):
    """ Get file list form local folder. """
    from glob import glob
    return glob(path)


# In[23]:


# Converts files from ANSCI to UTF8, which python can read
def UTF8_convert(list_files):
    BLOCKSIZE = 300000 # desired size in bytes, this is 300 kB, which is larger than biggest file 

    for file in list_files: 
        name_conv = UTF8_folder + file[46:62] +'_UTF8.txt'   #naming convention and moves to folder for UTF8-Files
        with codecs.open(file, "r", "mbcs") as sourceFile:
            with codecs.open(name_conv, "w", "utf-8") as targetFile:     # convert to UTF-8
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
    


# In[24]:


# gives the sample depth (lower) from the file name
def sample_height(file):
    #Find scan depth,
    sc = file.split("_") #This read from file name
    scan_depth_tot = sc[4]
    sc2 = scan_depth_tot.split("-")
    num = float(sc2[0])
    
    return num


# In[25]:


#Find the term in the file (used for knowing where to start dataframe)
def find_term(term, file):
    row = 0
    file_o = open(file)
    for line in file_o:
        row += 1
        line.strip().split('/n')
        if term in line:
            return (row)
    file.close()


# In[26]:


#Loop through all of the files in the snowpit and concatonates in one dataframe
def loop_files(files):
    
    #start and end terms
    start = "2D analysis"
    end = "3D analysis"
    frames = []

    for file in files:

        #Find start row, read in csv for Morpho Result
        end_row = (find_term(end, file)-4)
        start_row = find_term(start, file)+9
        nrow = end_row - start_row
        df_int = pd.read_csv(file, skiprows= (start_row), nrows=(nrow))

        #Find scan depth,
        sc = file.split("_") #This read from file name
        scan_depth = sc[4]

        #find average depth
        cutoff = scan_depth[0:-2]
        x = cutoff.split("-")
        hi = float(x[0])
        lo = float(x[1])
        avg_depth = (hi + lo)/2


        ### Add in some rows for this prelim info
        ### Description, Abbreviation, Value, Unit
        df_int['Scan Depth'] = [scan_depth]*nrow  # Row for Scan Depth

        df_int = df_int.drop([df_int.index[0]])
        df_int = df_int.rename(columns={'Unnamed: 0':'File Name'})

        #Add the column we want ("Values") to the datafram
        frames.append(df_int)
       

    result = pd.concat(frames)
        
    return result 
    
    


# In[27]:


#Main calls all other functions, takes in a file path and yes/no if you want a .csv out 
def main(files, to_csv):
    list_files = list_files_local(files)  
    
    #get the snowpit name of file
    snowpit = str(list_files[0][46:50])
    
    
    #Convert to UTF-8
    UTF8_convert(list_files)
    
    #Sort-Files
    UTF8_files = list_files_local(UTF8_folder+ '/*.txt') 
    UTF8_files = sorted(UTF8_files, key = sample_height) 
    
    
    #Find Start/End of the dataframe
    start = "2D analysis"
    end = "3D analysis"
    
    #Loop through the files
    result = loop_files(UTF8_files)
    
    #If to .csv is wanted: 
    if to_csv:
        # Export our dataframe to a .csv
        result.to_csv("M_RESULTS_2D"+snowpit+".csv", index =False)
        
    return result 


# In[28]:


main(files, True)


# In[ ]:




