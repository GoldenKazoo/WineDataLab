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

########################################
# A DECOMMENTER POUR LA PARTIE SCRAPING#
########################################
#option = Options()
#option.headless = True
#driver = webdriver.Firefox(options=option) #Ouverture page unique
URL = "https://www.millesima.fr/"

# Question 1 : recup la soup de la page
def getsoup(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body"))) #On wait pour laisser le temps a la page de se charger
    return soup

# Question 2 : recup prix a partir de soup de la page
def prix(soup):
    temp = soup.find('div', class_="ProductPrice_below-price-bloc__C0aol")
    if temp is None or temp.span is None:
        return None
    price_str = temp.span.get_text(strip=True)
    price_str = price_str.replace(',', '.')
    cleaned = ""
    for c in price_str:
        if c.isdigit() or c == '.':
            cleaned += c
    if cleaned == "":
        print("Conversion pas possible :", price_str)
        return None
    try:
        return float(cleaned)
    except ValueError:
        print("Conversion pas possible :", price_str)
        return None
  
# Question 3 : Renvoie appelation du vin a partir de soup
def appellation(soup):
    table_rows = soup.find_all("tr")
    for row in table_rows:
        tds = row.find_all("td")
        if len(tds) >= 2:
            header = tds[0].get_text(strip=True)
            if "Appellation" in header:
                return tds[1].get_text(strip=True)
    return None
   
# Question 4 : Renvoie la note de Parker
def parker(soup): 
    notations = soup.find_all('span', class_="WineCriticSlide_name__qih2Y")
    for i in range(len(notations)):
        #print(notations[i].string)
        if(notations[i].string == "Parker"):
            # print("[+] Parker found !")
            parker_notation = soup.find('span', class_="WineCriticSlide_rating__jtxAA").string
            return note(parker_notation)
        else:
            return None

def note(s):
    if not s:
        return None
    s = s.strip()
    if '/' in s:
        s = s.split('/')[0]
    if '-' in s:
        a, b = s.split('-')
        b = b.replace('+', '')
        try:
            return (float(a) + float(b)) / 2
        except ValueError:
            print("Impossible de convert la note :", s)
            return None
    s = s.replace('+', '')
    try:
        return float(s)
    except ValueError:
        print("Impossible de convert la note :", s)
        return None

def fill_csv_resume(start_page=60):
    with open("wine.csv", "a", newline="\n", encoding="utf-8") as file:
        writer = csv.writer(file)
        page = start_page
        while True:
            print(f"\n=== Page {page} ===")
            url = f"{URL}/bordeaux.html?page={page}"
            soup = getsoup(url)
            wine_links = get_wine_links_bordeaux(soup)
            print(f"Nombre de vins trouves : {len(wine_links)}")
            if not wine_links:
                print("Finito")
                break
            for link in wine_links:
                try:
                    wine_soup = getsoup(link)
                    line = informations(wine_soup)
                    writer.writerow(line.split(","))
                    print("Lien add :", link)
                    # time.sleep(1)
                except Exception as e:
                    print("Erreur skill issue :", link, e)
            page += 1

    driver.quit()

# Question 5 : Pareil pour Robinson et Suckling
def find_critic(soup, str): # On a decide de laisser Parker tel quel pour repondre a la question precedente et de factoriser pour les 2 suivantes, meme principe en soit on change le str par Parker
    notations = soup.find_all('span', class_="WineCriticSlide_name__qih2Y")
    for i in range(len(notations)):
        # print(notations[i].string)
        if(notations[i].string == str):
            # print(str)
            notations = soup.find('span', class_="WineCriticSlide_rating__jtxAA").string
            return note(notations)
    return None

def robinson(soup):
    return (find_critic(soup, "J. Robinson"))


def suckling(soup):
    return(find_critic(soup, "J. Suckling"))

# def note(str):
#     tmp = ""
#     index = str.index("/")
#     for i in range(index):
#         if (str[i] == '+'):
#             return int(tmp)
#         if (str[i] == '-'):
#             tmp2 = str[i+1:index]
#             # print(f"Split : {tmp2}")
#             return (int(tmp) + int(tmp2))/2
#         tmp += str[i]

#     return int(tmp)

# Question 6 : Renvoie Appelation + Note Parker + Note Robinson + Note Suckling
def informations(soup):
    return str(appellation(soup)) + "," + str(parker(soup)) + "," + str(robinson(soup)) + "," + str(suckling(soup)) + "," + str(prix(soup))

# Question 7 : Recup les bordeaux et stocker leurs infos dans le csv
def get_wine_links_bordeaux(soup):
    links = []
    cards = soup.select("div.ProductCard_infosContainer__D0bNH")
    for card in cards:
        tag_of_a = card.select_one("div.ProductCardName_container__XW6iR a")
        if tag_of_a:
            href = tag_of_a.get("href")
            if href.endswith(".html"):
                full_link = "https://www.millesima.fr" + href
                if full_link not in links:
                    links.append(full_link)
    return links

def fill_csv():
    global driver

    with open("wine.csv", "w", newline="\n", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Appelation", "Parker", "Robinson", "Suckling", "Prix"])
        page = 1
        while True:
            if page % 5 == 0: # Pour gerer les timeout qu'on avait, on relance le navigateur
                driver.quit()
                driver = webdriver.Firefox(options=option)
            print(f"\n=== Page {page} ===")
            url = f"{URL}/bordeaux.html?page={page}"
            soup = getsoup(url)
            wine_links = get_wine_links_bordeaux(soup)
            print(f"Nombre de vins trouves : {len(wine_links)}")  # Nombre de vins (45 normalement)
            if not wine_links:
                print("Finito")
                break
            for link in wine_links:
                try:
                    wine_soup = getsoup(link)
                    line = informations(wine_soup)
                    writer.writerow(line.split(","))
                    print("Lien add :", link)
                    time.sleep(1)  # Respectons le site
                except Exception as e:
                    print("Erreur skill issue :", link, e)
            page = page + 1

    driver.quit()


# Question 8 :
# VERIFIER LES DONNEES ? COMMENT CA ?
vins = pd.read_csv('wine.csv')

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
#print(vins.shape) # OK selon le sujet
#print(vins.dtypes) # Valeurs bien numeriques


## Question 15 :
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

X_train, X_test, y_train, y_test = train_test_split(
    # Tous sauf le prix
    vins.drop(columns=["Prix"]), vins['Prix'], train_size=0.75, random_state=49
)

print(f"Train size : {X_train.shape}")
print(f"Test size : {X_test.shape}")


## Question 16
model_lR = LinearRegression()
model_lR.fit(X_train, y_train)
y_pred = model_lR.predict(X_test)

print(f"r2 score : {model_lR.score(X_test, y_test)}")



## Question 17
import matplotlib.pyplot as plt

def afficherSchema(y_pred, y_test):
    plt.figure(figsize=(10,6))
    plt.scatter(y_pred, y_test)

    plt.plot([y_test.min(), y_test.max()],
            [y_test.min(), y_test.max()])

    plt.xlabel("estim_LR (prédictions)")
    plt.ylabel("y_test (valeurs réelles)")
    plt.title("Régression linéaire : prédictions vs valeurs réelles")

    plt.show()

#afficherSchema(y_pred ,y_test)
# Constat : C'est tres moche

## Question 18 :

# Normaliser avec MinMaxScaler()
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

model_lR_normal = make_pipeline(MinMaxScaler(),  LinearRegression())
model_lR_normal.fit(X_train, y_train)
y_pred = model_lR_normal.predict(X_test)

print(f"r2 score (_lR_normal): {model_lR_normal.score(X_test, y_test)}")

#afficherSchema(y_pred, y_test)
# Rien n'a change

# Standard
model_lR_stand = make_pipeline(StandardScaler(),  LinearRegression())
model_lR_stand.fit(X_train, y_train)
y_pred = model_lR_stand.predict(X_test)

print(f"r2 score (_lR_stand): {model_lR_stand.score(X_test, y_test)}")

#afficherSchema(y_pred, y_test)
# Rien n'a change

## Question 19 :
import numpy as np
print(f"Prix min : {vins['Prix'].min()}")
print(f"Prix max : {vins['Prix'].max()}")
# Grosse dispertion !

y_log = np.log(vins["Prix"])
print(f"Prix min (log) : {np.log(vins['Prix']).min()}")
print(f"Prix max (log) : {np.log(vins['Prix']).max()}")

## Question 20 :
X_train, X_test, y_train, y_test = train_test_split(
    # Tous sauf le prix
    vins.drop(columns=["Prix"]), y_log, train_size=0.75, random_state=49
)
# LR
model_lR_log = LinearRegression()
model_lR_log.fit(X_train, y_train)
y_pred = model_lR_log.predict(X_test)

print(f"r2 score : {model_lR_log.score(X_test, y_test)}")
#afficherSchema(y_pred, y_test)

# LR Normal
model_lR_normal_log = make_pipeline(MinMaxScaler(),  LinearRegression())
model_lR_normal_log.fit(X_train, y_train)
y_pred = model_lR_normal_log.predict(X_test)

print(f"r2 score (_lR_normal_log): {model_lR_normal_log.score(X_test, y_test)}")
afficherSchema(y_pred, y_test)

# LR Standard
model_lR_stand_log = make_pipeline(StandardScaler(),  LinearRegression())
model_lR_stand_log.fit(X_train, y_train)
y_pred = model_lR_stand_log.predict(X_test)

print(f"r2 score (_lR_stand_log): {model_lR_stand_log.score(X_test, y_test)}")
#afficherSchema(y_pred, y_test)



# Tests
# print(informations(getsoup("https://www.millesima.fr/chateau-gloria-2016.html")))
# print(f"Prix : {prix(getsoup("https://www.millesima.fr/chateau-citran-2018.html"))}") # OK
# print(f"Rating parker : {parker(getsoup("https://www.millesima.fr/champagne-drappier-carte-d-or-0000.html"))}") 
# print(f"Rating parker : {parker(getsoup("https://www.millesima.fr/chateau-lafite-rothschild-2000.html"))}")
# print(f"Robinson rate : {robinson(getsoup("https://www.millesima.fr/chateau-lafite-rothschild-2000.html"))}")
# print(f"Suckling rate : {suckling(getsoup("https://www.millesima.fr/chateau-lafite-rothschild-2000.html"))}")
# print(f"Rating parker : {parker(getsoup("https://www.millesima.fr/chateau-peyrabon-2019.html"))}")
# fill_csv()
# print(note("90-93+/100")) Existe avec - et + ???
# print(note("17/20"))
# print(note("1/20"))
# print(note("1/100"))
# print(note("90+/100"))
# fill_csv()
# print(note("90-93/100"))

# print(appellation(getsoup("https://www.millesima.fr/chateau-gloria-2016.html")))

# print(informations(getsoup("https://www.millesima.fr/chateau-citran-2018.html")))