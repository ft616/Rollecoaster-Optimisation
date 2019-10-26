from urllib.request import urlopen as urq
from bs4 import BeautifulSoup as bs
import re
from time import sleep
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn import metrics

plt.style.use('ggplot')
plt.rc("font", size=7)

# function for scraping data from website
def scrapedata(retrievals,df):
    #refresh page to retrieve random rollercoaster
    for i in range(retrievals):
    #open up connection and grab the page
        url = 'https://rcdb.com/'
        client = urq(url)
        html = client.read()
        client.close() 
        #parse html
        html = bs(html, "html.parser")
        rcc_text = html.find(id="rrc_text")
        try:
            name = rcc_text.find("span", text=re.compile(r"Roller Coaster")).findParent("p").a.string
        except:
            name = None
        try:
            park = rcc_text.find("span", text=re.compile(r"Park")).findParent("p").a.string
        except:
            park = None
        try:
            location = rcc_text.find("span", text=re.compile(r"Location")).find_parent("p").text[8:]
        except:
            location = None           
        try:
            status = rcc_text.find("span", text=re.compile(r"Status")).find_parent("p").text[6:]
        except:
            status = None            
        try:
            inversions = int(rcc_text.find("span", text=re.compile(r"Inversions")).find_parent("p").text[10:])
        except:
            inversions = None           
        try:
            speed = float(rcc_text.find("span", text=re.compile(r"Speed")).find_parent("p").text[5:-4])
        except:
            speed = None            
        try:
            height = float(rcc_text.find("span", text=re.compile(r"Height")).find_parent("p").text[6:-3])
        except:
            height = None       
        try:
            drop = float(rcc_text.find("span", text=re.compile(r"Drop")).find_parent("p").text[4:-3])
        except:
            drop = None       
        try:
            length = float(rcc_text.find("span", text=re.compile(r"Length")).find_parent("p").text[6:-3])
        except:
            length = None          
        try:
            g_force = float(rcc_text.find("span", text=re.compile(r"G-Force")).find_parent("p").text[7:])
        except:
            g_force = None           
        try:
            layout = rcc_text.find("span", text=re.compile(r"Layout")).find_parent("p").a.string
        except:
            layout = None           
        try:
            manufacturer = rcc_text.find("span", text=re.compile(r"Manufacture")).find_parent('p').a.string 
        except:
            manufacturer = None
        #create dictionary for scraped data
        data = {'Name':name, 'Park':park, 'Location':location, 'Status':status, 'Inversions':inversions, 'Speed /mph':speed, 
                'Height':height, 'Drop /ft':drop, 'Length /ft':length, 'G-Force':g_force, 'Layout':layout, 'Manufacturer':manufacturer}
        #add data to empty dataframe
        df = df.append(data, ignore_index=True)
        print(i+1,"/", retrievals)
        sleep(0.5)
    return(df)




#for scraping the website and starting a new dataset
print("Do you want to scrape www.rcdb.com to build the dataset from scratch? yes/no")
if input()== 'yes':
    print( "How many rollercoasters do you want to add to the dataset?")
    df = scrapedata(int(input()),pd.DataFrame(columns = ["Name", "Park", "Location", "Status", "Inversions", "Speed /mph", "Height/ ft", "Drop /ft", "Length /ft", "G-Force", "Layout", "Manufacturer"]))
    print("Finished!")
    print("Do you want to save the dataset?")
    if input() == 'yes':
        print("enter filepath and file name")
        filepathname = input()
        df.to_csv("%s.csv" %filepathname)
        print("saved!")
        exit()
        
#For using the program to add more data to an existing dataset
print("Add data to existing dataset?") 
if input()== 'yes':
    print("How many rollercoasters do you want to add to the dataset?")
    iterations = int(input())
    print("enter filepath and file name")
    file = str(input())+".csv"    
    df = scrapedata(iterations,pd.read_csv(file,index_col = 0))
    df.to_csv(file)
    print("data appended and saved!")
    exit()

#load and process data   
print("Please specify filepath and file name of data to read.")
df = pd.read_csv(str(input())+".csv", index_col = 0)
#remove duplicate rows
df = df.drop_duplicates()
#drop rows with more than 4 values missing
df = df.dropna(thresh=8, axis=0)

#plot boxplots for numeric values
plt.subplot(1,4,1)
boxplot = df.boxplot(column='Speed /mph')
plt.subplot(1,4,2)
boxplot = df.boxplot(column='Height /ft')
plt.subplot(1,4,3)
boxplot = df.boxplot(column='Length /ft')
plt.subplot(1,4,4)
boxplot = df.boxplot(column='Drop /ft')

#save figure
plt.savefig('Speed_Height_Length_Drop_Boxplots.png')
plt.show()

#remove non numeric columns and rows with Status missing
df = df.drop(columns=['Name', 'Park', 'Location', 'Layout','Manufacturer'])
df.dropna(subset=['Status'])

#change operating and defunct to 1 and 0
df = df.replace("Operating", 1)
df = df.replace("Defunct", 0)
df = df.replace("SBNO", 0)



column_names_to_normalise = ['Speed /mph', 'Height /ft', 'Length /ft', 'Drop /ft']
#fill missing data with mean
for names in column_names_to_normalise:
    df[names] = df[names].fillna((df[names].mean()))
#normalise data
#nums = df[column_names_to_normalise].values
#min_max_scaler = MinMaxScaler()
#x_scaled = min_max_scaler.fit_transform(nums)
#df_temp = pd.DataFrame(x_scaled, columns=column_names_to_normalise, index = df.index)
#df[column_names_to_normalise] = df_temp

#reorganise index
df = df.reset_index()

#Define features (X) and labels (Y)
X = df[column_names_to_normalise]
Y = df['Status']

X_train,X_test,y_train,y_test=train_test_split(X,Y,test_size=0.25,random_state=0)

logreg = LogisticRegression()
# fit the model with data
logreg.fit(X_train,y_train)
y_pred=logreg.predict(X_test)

confusion_matrix = metrics.confusion_matrix(y_test, y_pred)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))

print("Enter Speed (mph):")
input_speed=input()
print("Enter Height (ft):")
input_height=input()
print("Enter Drop (ft):")
input_drop=input()
print("Enter Length (ft):")
input_length=input()

test=logreg.predict(pd.DataFrame({"Speed /mph": [input_speed], "Height/ ft": [input_height], "Drop /ft": [input_drop] ,"Length /ft": [input_length]}))

if test == 1:
    print("Rollercoaster is predicted to succeed")
else:
    print("Rollercoaster is predicted to fail")



