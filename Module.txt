import requests
from datetime import datetime
def recupererDonneesE(S,d,h1,m1,h2,m2):
    g=requests.get(f"https://applis.iut.univ-paris-diderot.fr/capteurs/{S}/date/{d}").json()
    H1=int((h1*3600+m1*60)/120)
    H2=int((h2*3600+m2*60)/120)
    H=[]
    T=[]
    hum=[]
    CO2=[]
    Ec=[]
    e1=g[0]
    strdate1=e1['Timestamp']
    DE1=datetime.strptime(strdate1,"%Y-%m-%d %H:%M:%S")
    e2=g[1]
    strdate2=e2['Timestamp']
    DE2=datetime.strptime(strdate2,"%Y-%m-%d %H:%M:%S") 
    HE1=[]
    HE1=DE1.hour+DE1.minute/60+DE1.second/3600
    HE2=[]
    HE2=DE2.hour+DE2.minute/60+DE2.second/3600
    if HE2-HE1<0.025:         
        for i in range(2*H1,2*(H2-2)):
            if len(g)>i:
                e=g[i]
                strdate=e['Timestamp']
                D=datetime.strptime(strdate,"%Y-%m-%d %H:%M:%S")
                H.append(D.hour+D.minute/60+D.second/3600)
                T.append(float(e['Temperature']))
                hum.append(float(e['Humidite']))    
                if len(e)==6:
                    for j in range(H1,H2+1):
                        f=g[j]
                        CO2.append(float(f['CO2']))
                        Ec.append(float(f['Eclairement'])) 
    else:
        for i in range(H1,H2-2):
            e=g[i]
            strdate=e['Timestamp']
            D=datetime.strptime(strdate,"%Y-%m-%d %H:%M:%S")
            H.append(D.hour+D.minute/60+D.second/3600)
            T.append(float(e['Temperature']))
            hum.append(float(e['Humidite']))    
            if len(e)==6:
                for j in range(H1,H2+1):
                    f=g[j]
                    CO2.append(float(f['CO2']))
                    Ec.append(float(f['Eclairement']))
    df=f"{S}-{d}.csv"
    f=open(df,'w')
    if len(g[0])==4:
        f.write('#heure,Temperature,Humidite\n')
        for i in range(len(H)):     #len(H)=117 au dernier rang: i=116
            f.write(f"{H[i]},{T[i]},{hum[i]}\n")    #Str(H[i])='23.94'
    else:
        f.write('heure,Temperature,Humidite,CO2,Eclairement\n')
        for i in range(len(H)):
            f.write(f"{str(H[i])},{str(T[i])},{str(hum[i])},{str(CO2[i])},{str(Ec[i])}\n")
    f.close()
    print("le fichier a été crée")
#####la 2
import numpy as np
import matplotlib.pyplot as plt

def afficher_graphique(salles, date, heure1, min1, heure2, min2, grandeur):
    plt.figure() 

    for salle in salles:
        nom_fichier_csv = f"{salle}-{date}.csv"

        # ###Charger les données 
        try:
            data = np.loadtxt(nom_fichier_csv, delimiter=',', skiprows=1)
        except FileNotFoundError:
            print(f"Erreur : Le fichier {nom_fichier_csv} est introuvable.") 
            continue

        heures = data[:, 0]


        if grandeur == "Temperature":
            valeurs = data[:, 1]
        elif grandeur == "Humidite":
            valeurs = data[:, 2]
        elif grandeur == "CO2":
            valeurs = data[:, 3]
        elif grandeur == "Eclairement":
            valeurs = data[:, 4]
        else:
            print(f"Erreur : La grandeur '{grandeur}' n'est pas reconnue.")
            continue

        #### Filtrer
        heure_debut = heure1 + min1 / 60
        heure_fin = heure2 + min2 / 60
        filtre = (heures >= heure_debut) & (heures <= heure_fin)

        plt.plot(heures[filtre], valeurs[filtre], label=f"{salle} - {grandeur}")

    plt.xlabel("Heure")
    plt.ylabel(grandeur)
    plt.title(f"{grandeur} pour {date} entre {heure1}h{min1} et {heure2}h{min2}")
    plt.legend()
    plt.grid()

    nom_fichier_image = f"salles_{grandeur}_{date}_{heure1}h{min1}-{heure2}h{min2}.png"
    plt.savefig(nom_fichier_image)
    plt.close()

    print(f"Graphique sauvegardé : {nom_fichier_image}")


###traitement 1
import numpy as np

def isolation_ventilation(salles, date, heure1, min1, heure2, min2):
    coefficients_iso = []  # ##Stocker les coefficients (pentes d'isolation)
    coefficients_vent = []  ### Stocker les coefficients (pentes de ventilation)

    for salle in salles:
        # Charger les données depuis le fichier CSV
        try:
            data = np.loadtxt(f"{salle}-{date}.csv", delimiter=',', skiprows=1, dtype=float)
        except FileNotFoundError:
            print(f"Erreur : Le fichier {nom_fichier_csv} est introuvable.") 
            continue
         
        heures = data[:, 0]
        temp = data[:, 1]  # Température
        try:
            co2 = data[:, 3]   # CO2
        except IndexError:
            print(f"Attention : Pas de capteur CO2 pour la salle {salle}.")
            continue
        

        # Filtrer les données 
        heure_debut = heure1 + min1 / 60
        heure_fin = heure2 + min2 / 60
        filtre = (heures >= heure_debut) & (heures <= heure_fin)
        heures_filtrees = heures[filtre]
        temp_filtrees = temp[filtre]
        co2_filtrees = co2[filtre]

        # Calculer les pentes (isolation et ventilation)
        if len(heures_filtrees) > 1:
            pente_iso = np.polyfit(heures_filtrees, temp_filtrees, 1)[0]
            pente_vent = np.polyfit(heures_filtrees, co2_filtrees, 1)[0]
            coefficients_iso.append((salle, pente_iso))
            coefficients_vent.append((salle, pente_vent))

    # Trier les coefficients par pente croissante
    coefficients_iso.sort(key=lambda x: x[1])
    coefficients_vent.sort(key=lambda x: x[1])

    # Calcul de la corrélation
    pentes_iso = []
    pentes_vent = []

    for salle, pente in coefficients_iso:
        pentes_iso.append(pente)

    for salle, pente in coefficients_vent:
        pentes_vent.append(pente)

    cov = np.cov(pentes_iso, pentes_vent, ddof=1)[0, 1]
    std_iso = np.std(pentes_iso, ddof=1)
    std_vent = np.std(pentes_vent, ddof=1)
    corr_coeff = cov / (std_iso * std_vent)

    print(f"\nCorrélation entre isolation et ventilation : {corr_coeff:.2f}")

    # Afficher les classements
    print("\nClassement des salles par isolation (Température) :")
    for (salle, pente) in coefficients_iso:
        print(f"{salle}: Pente = {pente:.2f}")

    print("\nClassement des salles par ventilation (CO2) :")
    for (salle, pente) in coefficients_vent:
        print(f"{salle}: Pente = {pente:.2f}")
