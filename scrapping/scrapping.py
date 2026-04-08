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
