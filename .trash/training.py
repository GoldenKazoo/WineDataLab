from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler

# --- DÉBUT de apprentissage.py ---
vins = pd.read_csv("data/vins_clean.csv")
print("Chargé here we go mon coco!")


## Question 15 :

X_train, X_test, y_train, y_test = train_test_split(
    # Tous sauf le prix
    vins.drop(columns=["Prix"]), vins['Prix'], train_size=0.75, random_state=49
)

print("Question 15 : \n")
print(f"Train size : {X_train.shape}")
print(f"Test size : {X_test.shape}")
print("==================================\n")


## Question 16
model_lR = LinearRegression()
model_lR.fit(X_train, y_train)
y_pred = model_lR.predict(X_test)

print("Question 16 : \n")
print(f"r2 score : {model_lR.score(X_test, y_test)}")
print("==================================\n")



## Question 17

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

model_lR_normal = make_pipeline(MinMaxScaler(),  LinearRegression())
model_lR_normal.fit(X_train, y_train)
y_pred = model_lR_normal.predict(X_test)

print("Question 18 :\n")
print(f"r2 score (_lR_normal): {model_lR_normal.score(X_test, y_test)}")

#afficherSchema(y_pred, y_test)
# Rien n'a change

# Standard
from sklearn.preprocessing import StandardScaler

model_lR_stand = make_pipeline(StandardScaler(),  LinearRegression())
model_lR_stand.fit(X_train, y_train)
y_pred = model_lR_stand.predict(X_test)

print(f"r2 score (_lR_stand): {model_lR_stand.score(X_test, y_test)}")
print("==================================\n")

#afficherSchema(y_pred, y_test)
# Rien n'a change

## Question 19 :
import numpy as np

print("Question 19 : \n")
print(f"Prix min : {vins['Prix'].min()}")
print(f"Prix max : {vins['Prix'].max()}\n")

# Grosse dispertion !

y_log = np.log(vins["Prix"])
print(f"Prix min (log) : {np.log(vins['Prix']).min()}")
print(f"Prix max (log) : {np.log(vins['Prix']).max()}")
print("==================================\n")

## Question 20 :
X_train, X_test, y_train, y_test = train_test_split(
    # Tous sauf le prix
    vins.drop(columns=["Prix"]), y_log, train_size=0.75, random_state=49
)

results = []
# LR
model_lR_log = LinearRegression()
model_lR_log.fit(X_train, y_train)
y_pred = model_lR_log.predict(X_test)
results.append(model_lR_log.score(X_test, y_test))

#print(f"r2 score : {model_lR_log.score(X_test, y_test)}")
#afficherSchema(y_pred, y_test)

# LR Normal
model_lR_normal_log = make_pipeline(MinMaxScaler(),  LinearRegression())
model_lR_normal_log.fit(X_train, y_train)
y_pred = model_lR_normal_log.predict(X_test)
results.append(model_lR_log.score(X_test, y_test))

#print(f"r2 score (_lR_normal_log): {model_lR_normal_log.score(X_test, y_test)}")
#afficherSchema(y_pred, y_test)

# LR Standard
model_lR_stand_log = make_pipeline(StandardScaler(),  LinearRegression())
model_lR_stand_log.fit(X_train, y_train)
y_pred = model_lR_stand_log.predict(X_test)
results.append(model_lR_log.score(X_test, y_test))

#print(f"r2 score (_lR_stand_log): {model_lR_stand_log.score(X_test, y_test)}")
#afficherSchema(y_pred, y_test)

# Fonction pour afficher un tableau
def printTab(model, results):
    print("+----------------------------------------------------------+")
    print("| Méthode                    |   r²                        |")
    print("+----------------------------------------------------------+")
    print(f"| {model}                    |    {results[0]}       |")
    print(f"| Normalisation + {model}    |    {results[1]}       |")
    print(f"| Standardisation + {model}  |    {results[2]}       |")
    print("+----------------------------------------------------------+")

print("Question 20 : \n")
printTab("LR", results)
print("==================================\n")
## Question 21
###############

## Question 22
from sklearn.neighbors import KNeighborsRegressor

results = []
for i in range(4,6):
    model_KNN = KNeighborsRegressor(n_neighbors=i)
    model_KNN.fit(X_train, y_train)
    results.append(model_KNN.score(X_test, y_test))
    #print(f"KNN = {i} : {model_KNN.score(X_test, y_test)}")

    model_KNN = make_pipeline(MinMaxScaler(),  KNeighborsRegressor(n_neighbors=i))
    model_KNN.fit(X_train, y_train)
    results.append(model_KNN.score(X_test, y_test))
    #print(f"KNN = {i} (Normal) : {model_KNN.score(X_test, y_test)}")

    model_KNN = make_pipeline(StandardScaler(),  KNeighborsRegressor(n_neighbors=i))
    model_KNN.fit(X_train, y_train)
    results.append(model_KNN.score(X_test, y_test))
    #print(f"KNN = {i} (Standard) : {model_KNN.score(X_test, y_test)}")
    #print("==================================================\n")

## On reste sur 4 !

## Question 23 
print("Question 23 :\n")
printTab("KNN (4)", results)
print("==================================\n")