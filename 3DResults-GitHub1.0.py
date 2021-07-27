#!/usr/bin/env python
# coding: utf-8

# In[25]:


import codecs
import shutil
import numpy as np
import pandas as pd 
from datetime import datetime


# ### CTan Morphometry Results 3D
# ##### Author: Anna Valentine (annavalentine@mines.edu)
# #### Date: 07/20/21
# 
# #### Purpose: 
# This takes in a folder of CTan .txt files, converts them to UTF-8 (because python doesn't like ANSCI?) and compiles the mophometry results for 3D Data. After getting all the morphometry results in one place, SSA is calculated. The morphometry results can be found in the .csv file called "M_RESULTS_PIT1s17.csv". 

# In[26]:


# Write down my standard path here
path = '/Users/annav/1_WORK_CRREL/CTan Project 1/'  # Directory that I am working in
files = path+'Data/*.txt'                           # Folder of data
UTF8_folder = path + 'D_UTF8/'                      # Set up a folder for UTF8 conversion


# In[27]:


#A very general function that lists the files from a certain path 
def list_files_local(path):
    """ Get file list form local folder. """
    from glob import glob
    return glob(path)

list_files = list_files_local(files)  #$MAINNN  #List of files in "Data Folder"


# In[28]:


#Converts files from ANSCI to UTF8 (which python can read), dumps them in a UTF8 folder
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
    


# In[29]:


def find_start(term, file):     #Function finds what row the term given is in (.csv or .txt)
    row = 0
    file_o = open(file)
    for line in file_o:
        row += 1
        line.strip().split('/n')
        if term in line:
            return (row +1)
    file.close()


# In[30]:


#Helps to format our data frame with all of the variables that will be used 

def format_dataframe(file): 
    #Make a preliminary dataframe to append to (with description, a column with Units)
    term = "MORPHOMETRY"
    s_row1 = find_start(term, file)
    df1 = pd.read_csv(file, skiprows= s_row1, nrows= 52)  #Read in the part of the file we want, "morphometry results"


    ### Description, Abbreviation, Value, Unit
    #df1.loc[-3] = ['Sample Name', np.nan, np.nan, np.nan]  # Row for Sample Name
    df1.loc[-2] = ['Scan Depth', np.nan, np.nan, 'cm']  # Row for Scan Depth
    df1.loc[-1] = ['Average Depth', np.nan, np.nan, 'cm']  # Row for Avg. Depth
    df1.index = df1.index + 3  # shifting index
    df1.sort_index(inplace=True) 

    #Okay, our main dataframe just has the description column woohoo
    df_main = pd.DataFrame(df1["Description"])
    df_main["Unit"] = pd.DataFrame(df1["Unit"])
    
    return df_main 
    


# In[31]:


#Find the sample depth (lower)
def sample_height(file):
    #Find scan depth,
    sc = file.split("_") #This read from file name
    scan_depth_tot = sc[4]
    sc2 = scan_depth_tot.split("-")
    num = float(sc2[0])
    
    return num


# In[36]:


#### Loops through all of our files and puts values into dataframe
def loop_files(UTF8_files, df_main):
    
    for file in UTF8_files:
    
        #Find start row, read in csv for Morpho Results
        term = "MORPHOMETRY"
        row = find_start(term, file)
        df_int = pd.read_csv(file, skiprows= row, nrows= 52)
    
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
        df_int.loc[-2] = ['Scan Depth', np.nan, scan_depth, 'cm']  # Row for Scan Depth
        df_int.loc[-1] = ['Average Depth', np.nan, avg_depth, 'cm']  # Row for Avg. Depth
        df_int.index = df_int.index + 3  # shifting index
        df_int.sort_index(inplace=True) 
    
    
        #Add the column we want ("Values") to the datafram
        df_main[avg_depth] = df_int["Value"]
    
    return df_main
    


# In[33]:


#Calculates SSA
def calc_SSA(df_main):
    # Take away the dang headers
    SSA = ["SSA", "m^2/kg"]
    SSA_int = df_main.loc[ 15, : ]  #Location of Object Surface/ Volume Ratio

    # mm^2/mm^3 --> m^2/m^3
    mm2m = 1000

    # m^2/m^3 --> m^2/kg
    m2kg = .001090513

    #Initialize
    SSA_i = 0

    #Loop through and calculate
    for i in range(len(SSA_int)-2):
        SSA_i = float(SSA_int[i+2])*mm2m*m2kg
        SSA.append(SSA_i) 


    df_main.loc[55] = SSA    #Add to our main dataframe!
    
    return df_main


# In[37]:


# Main function calls all other functions 
def main(data_path, to_csv):
    
    #Curious to see execution time
    startTime = datetime.now()
    
    list_files = list_files_local(files)  #List of files in "Data Folder"
    
    #get the snowpit name of file
    snowpit = str(list_files[0][46:50])
    
    UTF8_convert(list_files)  #Convert Files to UTF8
    
    #Now let's look at our converted UTF8 files
    UTF8_files = list_files_local(UTF8_folder+ '/*.txt') 
    
    df_main = format_dataframe(UTF8_files[0])  #Format dataframe
    
    #Let's sort our files so they go into the dataframe in order:
    UTF8_files = sorted(UTF8_files, key = sample_height) 
    
    df_main = loop_files(UTF8_files, df_main)
    
    #Calculate SSA and add
    calc_SSA(df_main)
    
    #IF to .csv is wanted: 
    if to_csv:
        # Export our dataframe to a .csv
        df_main.to_csv("M_RESULTS_3D"+snowpit+".csv", index =False)
    
    print(('execution time: ' + str(datetime.now() - startTime)))
    
    return df_main
    
    


# In[38]:


main(files, True)


# In[ ]:




