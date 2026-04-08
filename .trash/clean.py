from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd
from selenium.webdriver.firefox.options import Options

# Question 8 :
# VERIFIER LES DONNEES ? COMMENT CA ?
vins = pd.read_csv("/home/zak/Rendu/WineDataLab/data/wine.csv")

# Question 9 :
# SRC : https://stackoverflow.com/questions/13413590/how-to-drop-rows-of-pandas-dataframe-whose-value-in-a-certain-column-is-nan
# Ca NE modifie PAS le fichier csv !

vins = vins.dropna(subset=['Appelation'])
#for i in vins["Appelation"]:
#    print(i)


##################################################################################
# QUESTION GENERIQUE ?? ON FAIT UNE FONCTION QUI REPONDS A L'EXIGENCE DEMANDEE ? #
##################################################################################
# Question 10 : (Deja traitee plus haut en realite)
for i in vins["Prix"]:
    if type(i) is not float:
        print("Error!")

# SRC : https://stackoverflow.com/questions/2365411/convert-unicode-to-ascii-without-errors-in-python
def convert_ascii(string):
    return string.encode('ascii', 'ignore')

#print("test\u202fbalbla")
#print(convert_ascii("test\u202fbalbla"))

# Question 11 : 

moyenne_robert = vins.groupby("Appelation")["Parker"].mean()
#print(moyenne_robert)
moyenne_robert = moyenne_robert.fillna(0)
#print(moyenne_robert)

#Question 12 :

def get_moyenne(name):
    moyenne = vins.groupby("Appelation")[name].mean()
    moyenne = moyenne.fillna(0)
    return(moyenne)
    #return vins.groupby("Appelation")[name].mean().fillna(0) # SI on est audacieux

moyenne_robinson = get_moyenne("Robinson")
moyenne_suckling = get_moyenne("Suckling")
#print(moyenne_robinson)
print(moyenne_suckling)

## Question 13 :
def replace(df,moyenne):
    key = f"{moyenne.name}_bis"
    df = df.merge(moyenne, on=["Appelation"], suffixes=('', '_bis'))
    #print(df)
    df[moyenne.name] = df[moyenne.name].fillna(df[key])
    #print(df)
    df = df.drop(columns=[key])
    return df

vins = replace(vins,moyenne_robert)
vins = replace(vins,moyenne_robinson)
vins = replace(vins,moyenne_suckling)
print(vins)

## Question 14 :
vins = pd.get_dummies(vins, prefix='App', dtype = int)
print(vins)
print("==================================\n")
#print(vins.shape) # OK selon le sujet
#print(vins.dtypes) # Valeurs bien numeriques

# --- FIN du nettoyage c'est CLEAN ---

vins.to_csv("data/wine_clean.csv", index=False)
print("Sauvegardé !")
