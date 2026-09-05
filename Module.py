import requests
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


URL_API = "https://******/capteurs"


def recupererDonnees(S, d, h1, m1, h2, m2):

    if not isinstance(S, str):
        raise TypeError("Le nom de la salle doit être un texte.")

    if not isinstance(d, str):
        raise TypeError("La date doit être un texte.")

    if not all(isinstance(x, int) for x in [h1, m1, h2, m2]):
        raise TypeError("Les heures et minutes doivent être des nombres entiers.")

    if not 0 <= h1 <= 23 or not 0 <= h2 <= 23:
        raise ValueError("Les heures doivent être comprises entre 0 et 23.")

    if not 0 <= m1 <= 59 or not 0 <= m2 <= 59:
        raise ValueError("Les minutes doivent être comprises entre 0 et 59.")

    debut = h1 * 60 + m1
    fin = h2 * 60 + m2

    if debut > fin:
        debut, fin = fin, debut

    url = f"{URL_API}/{S}/date/{d}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        donnees = response.json()
    except requests.RequestException as e:
        raise ConnectionError(f"Impossible de récupérer les données : {e}")

    if not donnees:
        raise ValueError(f"Aucune donnée trouvée pour {S} le {d}.")

    heures = []
    temperatures = []
    humidites = []
    co2 = []
    eclairement = []

    for element in donnees:

        try:
            date_mesure = datetime.strptime(
                element["Timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )
        except (KeyError, ValueError):
            continue

        minute_mesure = date_mesure.hour * 60 + date_mesure.minute

        if debut <= minute_mesure <= fin:

            heures.append(
                date_mesure.hour
                + date_mesure.minute / 60
                + date_mesure.second / 3600
            )

            temperatures.append(float(element["Temperature"]))
            humidites.append(float(element["Humidite"]))

            if "CO2" in element:
                co2.append(float(element["CO2"]))

            if "Eclairement" in element:
                eclairement.append(float(element["Eclairement"]))

    if not heures:
        raise ValueError(
            f"Aucune donnée trouvée entre {h1}h{m1} et {h2}h{m2}."
        )

    nom_fichier = f"{S}({d}).csv"

    with open(nom_fichier, "w", encoding="utf-8") as fichier:

        if co2 and eclairement:

            fichier.write(
                "heure,Temperature,Humidite,CO2,Eclairement\n"
            )

            taille = min(
                len(heures),
                len(temperatures),
                len(humidites),
                len(co2),
                len(eclairement)
            )

            for i in range(taille):

                fichier.write(
                    f"{heures[i]},"
                    f"{temperatures[i]},"
                    f"{humidites[i]},"
                    f"{co2[i]},"
                    f"{eclairement[i]}\n"
                )

        else:

            fichier.write(
                "heure,Temperature,Humidite\n"
            )

            for i in range(len(heures)):

                fichier.write(
                    f"{heures[i]},"
                    f"{temperatures[i]},"
                    f"{humidites[i]}\n"
                )

    print(f"Fichier créé : {nom_fichier}")

    return nom_fichier


def afficherGraphique(
    salles,
    date,
    heure1,
    min1,
    heure2,
    min2,
    grandeur
):

    grandeurs = [
        "Temperature",
        "Humidite",
        "CO2",
        "Eclairement"
    ]

    if grandeur not in grandeurs:
        raise ValueError(
            "Grandeur inconnue. Choisissez : "
            "Temperature, Humidite, CO2 ou Eclairement."
        )

    if not isinstance(salles, list):
        raise TypeError(
            "Les salles doivent être données sous forme de liste."
        )

    plt.figure(figsize=(10, 6))

    nombre_courbes = 0

    colonnes = {
        "Temperature": 1,
        "Humidite": 2,
        "CO2": 3,
        "Eclairement": 4
    }

    for salle in salles:

        nom_fichier = f"{salle}({date}).csv"

        try:
            data = np.loadtxt(
                nom_fichier,
                delimiter=",",
                skiprows=1
            )
        except FileNotFoundError:
            print(f"Fichier introuvable : {nom_fichier}")
            continue

        if data.ndim == 1:
            data = data.reshape(1, -1)

        colonne = colonnes[grandeur]

        if data.shape[1] <= colonne:
            print(
                f"{salle} ne possède pas la grandeur {grandeur}."
            )
            continue

        heures = data[:, 0]
        valeurs = data[:, colonne]

        heure_debut = heure1 + min1 / 60
        heure_fin = heure2 + min2 / 60

        filtre = (
            (heures >= heure_debut)
            & (heures <= heure_fin)
        )

        if np.any(filtre):

            plt.plot(
                heures[filtre],
                valeurs[filtre],
                label=f"{salle} - {grandeur}"
            )

            nombre_courbes += 1

    if nombre_courbes == 0:
        plt.close()
        raise ValueError(
            "Aucune donnée disponible pour créer le graphique."
        )

    plt.xlabel("Heure")
    plt.ylabel(grandeur)

    plt.title(
        f"{grandeur} pour plusieurs salles le {date} "
        f"entre {heure1}h{min1} et {heure2}h{min2}"
    )

    plt.legend()
    plt.grid()

    nom_salles = "_".join(salles)

    nom_image = (
        f"{nom_salles}_{grandeur}_{date}_"
        f"{heure1}h{min1}-{heure2}h{min2}.png"
    )

    plt.savefig(
        nom_image,
        dpi=150,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()

    print(f"Graphique sauvegardé : {nom_image}")

    return nom_image


def isolationVentilation(
    salles,
    date,
    heure1,
    min1,
    heure2,
    min2
):

    resultats = []

    heure_debut = heure1 + min1 / 60
    heure_fin = heure2 + min2 / 60

    for salle in salles:

        nom_fichier = f"{salle}({date}).csv"

        try:
            data = np.loadtxt(
                nom_fichier,
                delimiter=",",
                skiprows=1
            )
        except FileNotFoundError:
            print(f"Fichier introuvable : {nom_fichier}")
            continue

        if data.ndim == 1:
            data = data.reshape(1, -1)

        if data.shape[1] < 4:
            print(
                f"{salle} ne possède pas de capteur CO2."
            )
            continue

        heures = data[:, 0]
        temperature = data[:, 1]
        co2 = data[:, 3]

        filtre = (
            (heures >= heure_debut)
            & (heures <= heure_fin)
        )

        heures_filtrees = heures[filtre]
        temperatures_filtrees = temperature[filtre]
        co2_filtres = co2[filtre]

        if len(heures_filtrees) < 2:
            print(
                f"Pas assez de données pour {salle}."
            )
            continue

        pente_temperature = np.polyfit(
            heures_filtrees,
            temperatures_filtrees,
            1
        )[0]

        pente_co2 = np.polyfit(
            heures_filtrees,
            co2_filtres,
            1
        )[0]

        resultats.append(
            (
                salle,
                pente_temperature,
                pente_co2
            )
        )

    if not resultats:
        raise ValueError(
            "Aucune salle ne possède suffisamment de données."
        )

    classement_isolation = sorted(
        resultats,
        key=lambda x: x[1]
    )

    classement_ventilation = sorted(
        resultats,
        key=lambda x: x[2]
    )

    print()
    print("CLASSEMENT ISOLATION")
    print()

    for salle, pente_temperature, pente_co2 in classement_isolation:

        print(
            f"{salle} : "
            f"pente température = "
            f"{pente_temperature:.3f}"
        )

    print()
    print("CLASSEMENT VENTILATION")
    print()

    for salle, pente_temperature, pente_co2 in classement_ventilation:

        print(
            f"{salle} : "
            f"pente CO2 = "
            f"{pente_co2:.3f}"
        )

    if len(resultats) >= 2:

        pentes_temperature = np.array(
            [x[1] for x in resultats]
        )

        pentes_co2 = np.array(
            [x[2] for x in resultats]
        )

        if (
            np.std(pentes_temperature) != 0
            and np.std(pentes_co2) != 0
        ):

            correlation = np.corrcoef(
                pentes_temperature,
                pentes_co2
            )[0, 1]

            print()
            print(
                f"Corrélation isolation / ventilation : "
                f"{correlation:.2f}"
            )

    return resultats


def moyenneGrandeur(
    fichier,
    grandeur,
    periode
):

    grandeurs = {
        "Temperature": 1,
        "Humidite": 2,
        "CO2": 3,
        "Eclairement": 4
    }

    periodes = [
        "Nuit",
        "Journee avec occupation",
        "Journee sans occupation"
    ]

    if grandeur not in grandeurs:
        raise ValueError(
            "Grandeur inconnue."
        )

    if periode not in periodes:
        raise ValueError(
            "Période inconnue."
        )

    data = np.loadtxt(
        fichier,
        delimiter=",",
        skiprows=1
    )

    if data.ndim == 1:
        data = data.reshape(1, -1)

    colonne = grandeurs[grandeur]

    if data.shape[1] <= colonne:
        raise ValueError(
            f"La grandeur {grandeur} n'est pas disponible."
        )

    heures = data[:, 0]
    valeurs = data[:, colonne]

    selection = []

    if periode == "Nuit":

        filtre = (
            (heures < 8)
            | (heures >= 18)
        )

        selection = valeurs[filtre]

    elif periode == "Journee avec occupation":

        filtre = (
            (heures >= 8)
            & (heures < 18)
        )

        selection = valeurs[filtre]

    elif periode == "Journee sans occupation":

        filtre = (
            (heures < 8)
            | (heures >= 18)
        )

        selection = valeurs[filtre]

    if len(selection) == 0:
        raise ValueError(
            "Aucune donnée pour cette période."
        )

    return round(float(np.mean(selection)), 2)


def natureCapteurSalle(salles, date):

    if not isinstance(salles, list):
        raise TypeError(
            "Les salles doivent être données sous forme de liste."
        )

    for salle in salles:

        url = f"{URL_API}/{salle}/date/{date}"

        try:
            response = requests.get(
                url,
                timeout=10
            )

            response.raise_for_status()

            donnees = response.json()

        except requests.RequestException as e:

            print(
                f"Erreur pour {salle} : {e}"
            )

            continue

        if not donnees:

            print(
                f"Aucune donnée pour {salle}."
            )

            continue

        capteurs = []

        if "Temperature" in donnees[0]:
            capteurs.append("Temperature")

        if "Humidite" in donnees[0]:
            capteurs.append("Humidite")

        if "CO2" in donnees[0]:
            capteurs.append("CO2")

        if "Eclairement" in donnees[0]:
            capteurs.append("Eclairement")

        print(
            f"{salle} possède {len(capteurs)} capteurs : "
            f"{', '.join(capteurs)}"
        )


def regulariteMesures(
    fichier,
    seuil_minutes=3
):

    data = np.loadtxt(
        fichier,
        delimiter=",",
        skiprows=1
    )

    if data.ndim == 1:
        data = data.reshape(1, -1)

    heures = data[:, 0]

    interruptions = []

    seuil = seuil_minutes / 60

    for i in range(1, len(heures)):

        difference = heures[i] - heures[i - 1]

        if difference > seuil:

            interruptions.append(
                (
                    heures[i - 1],
                    heures[i],
                    difference * 60
                )
            )

    if not interruptions:

        print(
            "Aucune absence de données supérieure "
            f"à {seuil_minutes} minutes."
        )

    else:

        print(
            f"{len(interruptions)} interruption(s) détectée(s) :"
        )

        for debut, fin, duree in interruptions:

            print(
                f"Entre {debut:.2f}h et "
                f"{fin:.2f}h : "
                f"{duree:.1f} minutes"
            )

    return interruptions
