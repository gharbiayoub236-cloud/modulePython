import requests
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


def recupererDonneesE(S, d, h1, m1, h2, m2):

    g = requests.get(
        f"https://applis.iut.univ-paris-diderot.fr/capteurs/{S}/date/{d}"
    )

    g.raise_for_status()
    g = g.json()

    H1 = int((h1 * 3600 + m1 * 60) / 120)
    H2 = int((h2 * 3600 + m2 * 60) / 120)

    H = []
    T = []
    hum = []
    CO2 = []
    Ec = []

    DE1 = datetime.strptime(
        g[0]["Timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    DE2 = datetime.strptime(
        g[1]["Timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    HE1 = DE1.hour + DE1.minute / 60 + DE1.second / 3600
    HE2 = DE2.hour + DE2.minute / 60 + DE2.second / 3600

    if HE2 - HE1 < 0.025:

        for i in range(2 * H1, 2 * (H2 - 2)):

            if i < len(g):

                e = g[i]

                D = datetime.strptime(
                    e["Timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                H.append(
                    D.hour + D.minute / 60 + D.second / 3600
                )

                T.append(float(e["Temperature"]))
                hum.append(float(e["Humidite"]))

    else:

        for i in range(H1, H2 - 2):

            if i < len(g):

                e = g[i]

                D = datetime.strptime(
                    e["Timestamp"],
                    "%Y-%m-%d %H:%M:%S"
                )

                H.append(
                    D.hour + D.minute / 60 + D.second / 3600
                )

                T.append(float(e["Temperature"]))
                hum.append(float(e["Humidite"]))

    if len(g[0]) == 6:

        for j in range(H1, H2 + 1):

            if j < len(g):

                f = g[j]

                CO2.append(float(f["CO2"]))
                Ec.append(float(f["Eclairement"]))

    nom_fichier = f"{S}-{d}.csv"

    with open(nom_fichier, "w") as f:

        if len(g[0]) == 4:

            f.write("#heure,Temperature,Humidite\n")

            for i in range(len(H)):

                f.write(
                    f"{H[i]},{T[i]},{hum[i]}\n"
                )

        else:

            f.write(
                "heure,Temperature,Humidite,CO2,Eclairement\n"
            )

            for i in range(len(H)):

                f.write(
                    f"{H[i]},{T[i]},{hum[i]},"
                    f"{CO2[i]},{Ec[i]}\n"
                )

    print("Le fichier a été créé")


def afficher_graphique(
    salles,
    date,
    heure1,
    min1,
    heure2,
    min2,
    grandeur
):

    plt.figure()

    for salle in salles:

        nom_fichier_csv = f"{salle}-{date}.csv"

        try:

            data = np.loadtxt(
                nom_fichier_csv,
                delimiter=",",
                skiprows=1
            )

        except FileNotFoundError:

            print(
                f"Erreur : Le fichier {nom_fichier_csv} est introuvable."
            )

            continue

        heures = data[:, 0]

        if grandeur == "Temperature":

            valeurs = data[:, 1]

        elif grandeur == "Humidite":

            valeurs = data[:, 2]

        elif grandeur == "CO2":

            if data.shape[1] < 4:
                print(f"Pas de CO2 pour {salle}.")
                continue

            valeurs = data[:, 3]

        elif grandeur == "Eclairement":

            if data.shape[1] < 5:
                print(f"Pas d'éclairement pour {salle}.")
                continue

            valeurs = data[:, 4]

        else:

            print(
                f"Erreur : La grandeur '{grandeur}' n'est pas reconnue."
            )

            continue

        heure_debut = heure1 + min1 / 60
        heure_fin = heure2 + min2 / 60

        filtre = (
            (heures >= heure_debut)
            & (heures <= heure_fin)
        )

        plt.plot(
            heures[filtre],
            valeurs[filtre],
            label=salle
        )

    plt.xlabel("Heure")
    plt.ylabel(grandeur)

    plt.title(
        f"{grandeur} pour {date} "
        f"entre {heure1}h{min1} et {heure2}h{min2}"
    )

    plt.legend()
    plt.grid()

    nom_fichier_image = (
        f"salles_{grandeur}_{date}_"
        f"{heure1}h{min1}-{heure2}h{min2}.png"
    )

    plt.savefig(nom_fichier_image)
    plt.close()

    print(
        f"Graphique sauvegardé : {nom_fichier_image}"
    )


def isolation_ventilation(
    salles,
    date,
    heure1,
    min1,
    heure2,
    min2
):

    coefficients_iso = []
    coefficients_vent = []

    for salle in salles:

        nom_fichier_csv = f"{salle}-{date}.csv"

        try:

            data = np.loadtxt(
                nom_fichier_csv,
                delimiter=",",
                skiprows=1
            )

        except FileNotFoundError:

            print(
                f"Erreur : Le fichier {nom_fichier_csv} est introuvable."
            )

            continue

        heures = data[:, 0]
        temp = data[:, 1]

        if data.shape[1] < 4:

            print(
                f"Attention : Pas de capteur CO2 pour la salle {salle}."
            )

            continue

        co2 = data[:, 3]

        heure_debut = heure1 + min1 / 60
        heure_fin = heure2 + min2 / 60

        filtre = (
            (heures >= heure_debut)
            & (heures <= heure_fin)
        )

        heures_filtrees = heures[filtre]
        temp_filtrees = temp[filtre]
        co2_filtrees = co2[filtre]

        if len(heures_filtrees) > 1:

            pente_iso = np.polyfit(
                heures_filtrees,
                temp_filtrees,
                1
            )[0]

            pente_vent = np.polyfit(
                heures_filtrees,
                co2_filtrees,
                1
            )[0]

            coefficients_iso.append(
                (salle, pente_iso)
            )

            coefficients_vent.append(
                (salle, pente_vent)
            )

    coefficients_iso.sort(
        key=lambda x: x[1]
    )

    coefficients_vent.sort(
        key=lambda x: x[1]
    )

    pentes_iso = [
        pente for salle, pente in coefficients_iso
    ]

    pentes_vent = [
        pente for salle, pente in coefficients_vent
    ]

    if len(pentes_iso) >= 2 and len(pentes_vent) >= 2:

        std_iso = np.std(
            pentes_iso,
            ddof=1
        )

        std_vent = np.std(
            pentes_vent,
            ddof=1
        )

        if std_iso != 0 and std_vent != 0:

            cov = np.cov(
                pentes_iso,
                pentes_vent,
                ddof=1
            )[0, 1]

            corr_coeff = cov / (
                std_iso * std_vent
            )

            print(
                f"\nCorrélation entre isolation et ventilation : "
                f"{corr_coeff:.2f}"
            )

    print(
        "\nClassement des salles par isolation (Température) :"
    )

    for salle, pente in coefficients_iso:

        print(
            f"{salle}: Pente = {pente:.2f}"
        )

    print(
        "\nClassement des salles par ventilation (CO2) :"
    )

    for salle, pente in coefficients_vent:

        print(
            f"{salle}: Pente = {pente:.2f}"
        )
