# -*- coding: utf-8 -*-

from datetime import datetime
# from pylatex import Document, Section, Subsection, Command
# from pylatex.utils import italic, NoEscape
# Installer le compilateuir latex: sudo apt-get install texlive-pictures texlive-science texlive-latex-extra latexmk

# fonctionne avec le resultat telecharger en csv avec le séparateur ";"  et en mode separe

import sys
from gen_pdf import generate_pdf
from mail2 import envoieMail
from pathlib import Path
import argparse
import os
import subprocess
import shlex
import time
import configparser
import re


REP_PDFS = './PDFs'


IndiceAge = 0  # Indice pour le prix selon l'age
IndiceParcours = 0  # Indice pour le prix selon le parcours, 0 dans la parcours 1 sinon
nbeleve_max = 4 # Nb max d'eleve
separateur_csv="|"


ListeMailEnvoye="ListeMailEnvoye.txt"
FicConfig="config.ini"
FicAccess="acces.ini"
dateComparaison="01/09" # date à prendre pour calculer l'age, on prendra l'année en cours
    


def ecrire_log(data):
    fichierLog.write(data + "\n")

def ecrire_csv(data):
    fichiercsv.write(data)

def ecire_resume(data):
  fichierResume=open(ListeMailEnvoye,"a")
  fichierResume.write(data+"\n")
  fichierResume.close()

def in_resume(data):
  # verifie si la chaine de caractere data se trouve dans le fichier ListeMailenvoye
  with open(ListeMailEnvoye,"r") as file:
    for line in file:
      print("data:"+data+" line:"+line)
      if re.search(data,line):
        return True
  return False

def extraireNomParcours(data):
    # Fontion permettant d'extraire le nom du parcours lorsque contient <strong>
    result = ""
    if len(data) > 0:
        result = data[8:]
        # print("result0:"+result)
        result = result[:result.find("strong") - 2]
        # print("result1:"+result)
    return result

def recupNomParcours(section,key):
    # Fontion permettant de recupérer le nom du parcours
    result = ""
    maSection=section+".Texte"
    try:
        result = maConfig[maSection][key]
    except KeyError:
        print("ERREUR section %s ne contient pas la clef %s" % (section,key))

    return result


def extraireKeyParcours(section1,data,force=False):  
    # Fontion permettant de retourner la clef de la section envoyé
    #     La key est trouvé en cherchant le texte de la key de la section section1.Index dans la chaine data
    # Si force = true ne renvoie pas d'erreur si la key n'est pas trouvé dans la section demandé
    result=""
    maSection=section1+'.Index'
    maChaine=data.casefold()
    result=""
    for key in maConfig[maSection]:
        retour=maChaine.find(maConfig[maSection][key].casefold())
        if not retour == -1:
            result=key
    if result=="" and not force:
        monError="ERREUR: pas de correspondance dans la section %s avec %s" % (maSection,maChaine)
        print(monError)
        ecrire_log(monError)

    
    return result


def extrairePrix(section1,key,reduction):   # (data, inf21a, boolparcours,section1,key):
    # Fontion permettant de retourner le prix selon le type de formation choisie, l'age et si ou non dans le parcours
    result = 0
    
    if reduction:
        reduit=".Reduit"
    else:
        reduit=""
    
    section=section1+".PRIX"+reduit

    try:
        result = maConfig[section][key]
    except KeyError:
        monError="ERREUR PRIX section %s ne contient pas la clef %s" % (section,key)
        print(monError)
        ecrire_log(monError)
    return int(result)


# Fin recherche prix

def rechercheRrixInstrument(instrument):
    match instrument:
        case "Les instruments amplifiés : guitare électrique" | "Les cordes : guitare classique":
            return maConfig['Locations.PRIX']['guitare']
        case "Les instruments traditionnels : harpe celtique":
            return maConfig['Locations.PRIX']['hautbois']
        case _:
            return maConfig['Locations.PRIX']['autre']


# Fin rechercheRrixInstrument


# Debut prog
if __name__ == '__main__':
    # Lecture des arguments en ligne de commande
    parser = argparse.ArgumentParser(usage="Traite les fichiers CSV d'inscription en ligne, génère les PDF et envoie les mails si spécifié")
    parser.add_argument('-f', type=str, default='./ATraiter.csv', help="Spécifie le fichier CSV à traiter")
    parser.add_argument('-m', action='store_true', help="Envoie les mails après génération du PDF")
    parser.add_argument('-r', action='store_true', help="Ne reinitialise pas la liste des mails envoyés - on verifie si un mail a déjà été envoyé précédemment")
    parser.add_argument('-s', action='store_true', help="N'ecrase pas les fichiers pdf s'ils existent déjà")
    # les mails envoyes sont mis dans un fichier, si l'adresse apparait dans ce fichier, le mail n'est pas envoyé. Si l'onption r est utilisé le fichier précédent n'est pas effacé
    # Les fichiers pdf existant sont pas remplacés, sauf avec l'option -s. Sans cette option si 2 meme nom sont traités dans le même cycle seul le 2eme restera dans le répertoire
    args = parser.parse_args()
    filepath = args.f
    
    fichierLog = open("Log.txt", "w")
    fichiercsv = open("result.csv", "w")

    ecrire_log(
        "\n\n\n ***********************   " + datetime.today().strftime("%Y-%m-%d %H:%M") + "   ************ \n\n\n")


    # Recuperation des données des fichiers de config
    pwd_sender=""
    config_acces = configparser.ConfigParser()
    if os.path.exists(FicAccess):
        config_acces.read(FicAccess)
        try:
            pwd_sender=config_acces['acces']['password']
        except KeyError:
            pwd_sender=""
    maConfig = configparser.ConfigParser()
    if not os.path.exists(FicConfig):
        print("ERREUR ---- pas de fichier de configuration")
        quit()
    maConfig.read(FicConfig)
    try:
        sender=maConfig['Mail']['sender']
    except KeyError:
        pwd_sender=""
        ecrire_log("ERREUR - Sender non défini dans le fichier init")
    
    # Créé le répertoire pour stockage des PDFs s'il n'existe pas
    if not os.path.exists(REP_PDFS):
        os.makedirs(REP_PDFS)

    # Demande le password si envoie des mails
    if args.m:
        if pwd_sender=="":
            pwd_sender = input('Mot de passe pour expéditeur %s ? ' % sender)
    
    fichierSource = open(filepath, "r", encoding='UTF-8')
    
    if args.r:
        fichierResume=open(ListeMailEnvoye,"a")
    else:
        fichierResume=open(ListeMailEnvoye,"w")

    # On ecrit l'entete du fichier csv
    for indice in range(nbeleve_max):
                ecrire_csv("prix total eleve " + str(indice)+separateur_csv + "Prix exterieur eleve " + str(indice)+separateur_csv + "nom eleve " + str(indice)+separateur_csv + "prenom  eleve " + str(indice)+separateur_csv + "age  eleve " + str(indice)+separateur_csv + "date naissance eleve " + str(indice)+separateur_csv + "reinscription eleve " + str(indice)+separateur_csv + "NiveauScolaire eleve " + str(indice)+separateur_csv + "ParcoursCol eleve " + str(indice)+separateur_csv + "Prix Parcours Col eleve " + str(indice)+separateur_csv + "parcours eleve " + str(indice)+separateur_csv + "Prix Parcours eleve " + str(indice)+separateur_csv + "accompagnement eleve " + str(indice)+separateur_csv + "Prix Acoompagnement eleve " + str(indice)+separateur_csv + "cours de chant eleve " + str(indice)+separateur_csv + "instrument1 eleve " + str(indice)+separateur_csv + "location1 eleve " + str(indice)+separateur_csv + "prix location1 eleve " + str(indice)+separateur_csv + "instrument2 eleve " + str(indice)+separateur_csv + "location2 eleve " + str(indice)+separateur_csv + "prix location2 eleve " + str(indice)+separateur_csv + "taille eleve " + str(indice)+separateur_csv + "jour de preference eleve " + str(indice)+separateur_csv + "jour impossible eleve " + str(indice)+separateur_csv + "jour peut-être eleve " + str(indice)+separateur_csv + "remarquedispo eleve " + str(indice)+separateur_csv + "nom prof eleve " + str(indice)+separateur_csv + "orchestre eleve " + str(indice)+separateur_csv + "Prix Orchestre eleve " + str(indice)+separateur_csv + "groupe rock eleve " + str(indice)+separateur_csv + "Prix groupe eleve " + str(indice)+separateur_csv + "nom groupe eleve " + str(indice)+separateur_csv + "coursFMO eleve " + str(indice)+separateur_csv)
    ecrire_csv("Etat fiche"+separateur_csv)
    for indice in range(2):
                ecrire_csv("contact " + str(indice)+separateur_csv + "tel contact " + str(indice)+separateur_csv + "mail contact " + str(indice)+separateur_csv + "ville contact " + str(indice)+separateur_csv + "adresse contact " + str(indice)+separateur_csv + "changement d'adresse contact " + str(indice)+separateur_csv)
    ecrire_csv("facture" + separateur_csv + "sortir" + separateur_csv + "aide" + separateur_csv + "photo" + separateur_csv + "prelevement" + separateur_csv + "changeBanque" + separateur_csv + "autorise sortie" + separateur_csv + "commentaire" + separateur_csv + "Prix exterieur total" + separateur_csv + "Prix Famille" + separateur_csv + "reductionFamille" + separateur_csv + "Cotisation Famille\n")

                
    # Utiliser pour Calculer l'age, on calcul l'age à partir de dateComparaison
    date = datetime.now().date()
    dateComparaison=dateComparaison+"/"+str(date.year)

    # on récupère la 1ere ligne de donnée du fichier, les 3 eres sont les entetes
    line = fichierSource.readline()
    line = fichierSource.readline()

    line = fichierSource.readline() # On est sur la ligne d'entete - on supprime le retour chariot de fin et le dernier guillemé
    line=line[:len(line)-2] 
    liste_entete = line.split("\";\"")  # contient les entetes

    # On traite la ligne
    line = fichierSource.readline()
    while line:  # On parcours l'ensemble des fiches
        # declaration des tableaux, pour chaque eleve
        nom = ["", "", "", ""]
        prenom = ["", "", "", ""]
        age = ["", "", "", ""]
        dateNaissance = ["", "", "", ""]
        reinscription = [False, False, False, False]
        NiveauScolaire = ["", "", "", ""]
        ParcoursCol = [["", "", "", ""], [0, 0, 0, 0]]  # Nom , prix
        ParcoursComplet = [["", "", "", ""], [0, 0, 0, 0]]  # Nom , prix
        Acc = [["", "", "", ""], [0, 0, 0, 0]]  # Nom , prix
        CoursFMO=["","","",""] # choix du cours de FMO
        CoursChant = [False, False, False, False]
        PrixTotal = [0, 0, 0, 0]
        instrument1 = ["", "", "", ""]
        location1 = [False, False, False, False]
        instrument2 = ["", "", "", ""]
        location2 = [False, False, False, False]
        taille = ["", "", "", ""]
        remarqueDispo = ["", "", "", ""]
        nomProf = ["", "", "", ""]
        orchestre = [["", "", "", ""], [0, 0, 0, 0]]  # Nom , prix
        coursRock = [["", "", "", ""], [0, 0, 0, 0]]  # Nom , prix
        nomGroupe = ["", "", "", ""]
        jourpossible = ["", "", "", ""]
        jourimpossible = ["", "", "", ""]
        jourpeut_etre = ["", "", "", ""]
        prixInstrument = [[0, 0, 0, 0], [0, 0, 0, 0]]  # location instrument 1, instrument 2
        reduclocation=1 # multiplicateur de la reduction a appliquer sur la location d'nstrument
        contact = [{'nom': "", 'tel': "", 'mail': "", 'changementAdd':False,'adresse':"",'ville': ""}, {'nom': "", 'tel': "", 'mail': "", 'changementAdd':False,'adresse':"", 'ville': ""}]
        typeReglement = ""
        reductionFamille = 0
        inf21a = False
        parcours = False
        prixExterieurEleve = [maConfig['Divers.PRIX'].getint('prixExterieur'),maConfig['Divers.PRIX'].getint('prixExterieur'),maConfig['Divers.PRIX'].getint('prixExterieur'),maConfig['Divers.PRIX'].getint('prixExterieur')]
        prixExterieur=0
        commentaire = ""
        cotisationFamille = maConfig['Divers.PRIX'].getint('cotisationFamille')
        facture = False
        dispositifSortir = False
        volontaire = False
        autorisePhoto = False
        autoriseSortie = True
        changeBanque=False

        ecrire_log("Nouvelle ligne" + line)
        liste_data = line.split("\";\"")
        count = 0
        eleve = -1
        nb_inscrit = 0
        indice_contact=0 # indice pour le contact parent
        if not (len(liste_data) == len(liste_entete)):
            texte="ERREUR - l'entete n'a pas autant d'element que les data %s" % liste_data
            print(texte)
            ecrire_log(texte)
        # Fin si len

        for data in liste_data:  # On parcours les info de la fiche pour chaque famille (chaque ligne)
            count = count + 1  # défini la colonne du csv
            # Initialisation des variables temporaires
            nomcoursAcc = ""
            nomcoursOrc = ""
            nomcoursRock = ""
            jour = ""

            if data=="X" and not (liste_entete[count - 1][:5] == "Pas d"):  # On est dans une liste à multiple choix, on traite séparément
                # On regarde si on est dans la section ammatteur
                section="Amatteur"
                key=extraireKeyParcours(section,liste_entete[count - 1],True)
                if not (key==""): # On est dans la section Amatteur
                    prixtemp = extrairePrix(section,key,parcours or inf21a)
                    Acc[1][eleve] = Acc[1][eleve] + prixtemp
                    PrixTotal[eleve] = PrixTotal[eleve] + prixtemp
                    if len(Acc[0][eleve]) == 0:  # Aucun cours n'a encore été choisi, c'est le 1er
                        Acc[0][eleve] = recupNomParcours(section,key)
                    else:  # un autre cours a deja ete choisi
                        Acc[0][eleve] = Acc[0][eleve] + " + " + recupNomParcours(section,key)
                    # fin si len
                # fin si key
                if key =="":
                    # il n'y a pas le texte cherché dans la section Amatteur, on est danc dans une autre section
                    section="Orchestre"
                    key=extraireKeyParcours(section,liste_entete[count - 1],True)
                    if not (key==""): # On est dans la section Orchestre
                        prixtemp = extrairePrix(section,key,parcours or inf21a)
                        orchestre[1][eleve] = orchestre[1][eleve] + prixtemp
                        PrixTotal[eleve] = PrixTotal[eleve] + prixtemp
                        if len(orchestre[0][eleve]) == 0:  # Aucun cours n'a encore été choisi, c'est le 1er
                            orchestre[0][eleve] = recupNomParcours(section,key)
                        else:  # un autre cours a deja ete choisi
                            orchestre[0][eleve] = orchestre[0][eleve] + " + " + recupNomParcours(section,key)
                        # fin si  len
                    # fin si key Orchestre
                # fin si key 
                if key =="":
                    # il n'y a pas le texte cherché dans la section Groupe, on est danc dans une autre section
                    section="Groupe"
                    key=extraireKeyParcours(section,liste_entete[count - 1],True)
                    if not (key==""): # On est dans la section Groupe
                            prixtemp = extrairePrix(section,key,parcours or inf21a)
                            coursRock[1][eleve] = coursRock[1][eleve] + prixtemp
                            PrixTotal[eleve] = PrixTotal[eleve] + prixtemp
                            if len(coursRock[0][eleve]) == 0:  # Aucun cours n'a encore été choisi, c'est le 1er
                                coursRock[0][eleve] = recupNomParcours(section,key)
                            else:  # un autre cours a deja ete choisi
                                coursRock[0][eleve] = coursRock[0][eleve] + " + " + recupNomParcours(section,key)
                            # fin si len
                    # fin si key groupe
                # fin si key
                if key =="":
                    # il n'y a pas le texte cherché dans la section, on est danc dans une autre section
                    section = "Complement"
                    key=extraireKeyParcours(section,liste_entete[count - 1],True)
                    if not (key==""): # On est dans la section Complement
                        match key:
                            case "facture":
                                facture=True
                            case "sortir":
                                 dispositifSortir = True
                            case "volontaire":
                                volontaire = True
                            case "photo": 
                                autorisePhoto = True
                            case other:
                                texteError="ERREUR key '%s' de la section '%s' non traitee" % (key,section)
                                print(texteError)
                                ecrire_log(texteError)        
                if key =="":
                    # il n'y a pas le texte cherché dans la section, on est danc dans une autre section
                    section = "Reglement"
                    key=extraireKeyParcours(section,liste_entete[count - 1],True)
                    if not (key==""): # On est dans la section Reglement
                        typeReglement = typeReglement + " + " + recupNomParcours(section,key)
                if key =="":
                    # il n'y a pas le texte cherché dans la section, on est danc dans une autre section
                    section = "ReglementInterieur"
                    key=extraireKeyParcours(section,liste_entete[count - 1],True)
                    if not (key==""): # On est dans la section Reglementinterieur
                        validation=True
                
                if key =="":
                    # il n'y a pas le texte cherché dans la section, on est danc dans une autre section
                    texteError="ERREUR DATA=X et '%s' non trouve dans les index" % liste_entete[count-1]
                    print(texteError)
                    ecrire_log(texteError)
                 # fin si key

            elif not (liste_entete[count - 1][:5] == "Pas d"): # data différent de X, si pas de on ne fait rien
                match liste_entete[count - 1]:
                    case "Brouillon":
                        match data:
                            case "1":
                                etat = "brouillon"
                                texteError="ERREUR - Traitement d'une fiche non finalisée au nom de  "+nom[eleve]
                                print(texteError)
                                ecrire_log(texteError)
                                _ = input("Appuyer sur Entrée pour continuer ...")
                            case "0":
                                etat = "valide"
                    # fin match data
                    case "Nombre d'élève à inscrire":
                     nb_inscrit = data
                    case "Nom" | "Nom  (si différent de l'élève 1)":
                        eleve = eleve + 1  # On a un nouvel eleve
                        indice_instrument=0 # indice de l'instrument pour l'eleve
                        parcours = False  # On initialise le parcours a false, le met a true si une formation dans le parcours est choisie plus tard
                        if data == "" and eleve < int(nb_inscrit):  # Le nom est vide, on prend donc le nom de l'eleve precedent (le 1er ne peut pas etre vide)
                            nom[eleve] = nom[eleve - 1]
                        else:
                            nom[eleve] = data
                    case "Prénom":
                        if not(nom[eleve] =="") and data =="":
                            texteError="ERREUR - Saisie incorrect, pas de prenom pour "+nom[eleve]+" . nb d'inscrit incorrect"
                            print(texteError)
                            ecrire_log(texteError)
                            _ = input("Appuyer sur Entrée pour continuer ...")
                        prenom[eleve] = data
                    
                    case "Date de naissance":
                        if len(data)>0:
                            dateNaissance[eleve] = data
                            temp_naissance=datetime.strptime(data,'%d/%m/%Y')
                            temp_now=datetime.strptime(dateComparaison,'%d/%m/%Y')
                            age[eleve]=(temp_now.year - temp_naissance.year - ((temp_now.month, temp_now.day) < (temp_naissance.month, temp_naissance.day)))
                            if age[eleve] > 21:
                                inf21a = False
                            else:
                                inf21a = True
                        else:
                            if not (nom[eleve] ==""):
                                texteError="ERREUR - date naissance non renseigné pour "+nom[eleve]+" "+prenom[eleve]
                                print(texteError)
                                ecrire_log(texteError)
                    case "Réinscription":# 14 | 49 | 84 | 119:  # reinscription
                        if data == "nouvel inscrit":
                            reinscription[eleve] = False
                        else:
                            reinscription[eleve] = True
                    case "Niveau Scolaire si élève en primaire ou maternelle":  # Niveau scolaire
                        NiveauScolaire[eleve] = data
                    case "Parcours découverte de la musique en cours collectifs":  # Parcours decouverte de la musique en cours collectif
                        if data[:6] == "Pas de":
                            data = ""
                        if len(data) > 0:
                            parcours = True
                            section="Decouverte"
                            key=extraireKeyParcours(section,data)
                            ParcoursCol[0][eleve] = recupNomParcours(section,key)
                            ParcoursCol[1][eleve] = extrairePrix(section,key,inf21a)    
                            PrixTotal[eleve] = PrixTotal[eleve] + ParcoursCol[1][eleve]
                            reduclocation=maConfig[section+".PRIX.Reduit"]["location"]
                    case "Parcours complet - (Instrument  ou chant + 45 mn de FM ou MAO)":  # Parcours complet - instrument ou champs + FM
                        if data[:6] == "Pas de":
                            data = ""
                        if len(data) > 0:
                            parcours = True
                            section="Parcours"
                            key=extraireKeyParcours(section,data)
                            ParcoursComplet[0][eleve] = recupNomParcours(section,key)
                            ParcoursComplet[1][eleve] = extrairePrix(section,key,inf21a)
                            PrixTotal[eleve] = PrixTotal[eleve] + ParcoursComplet[1][eleve]
                    case "Formation Musicale et MAO":
                        if data[:17] == "Ne s'inscrit pas":
                            data=""
                        CoursFMO[eleve]=data
                    case "Cours de Chant":  # Cours de chant
                        if data == "Oui":
                            CoursChant[eleve] = True
                    
                    case "Nom de l'instrument":  # Nom Instrument 1
                        indice_instrument=indice_instrument+1
                        if indice_instrument==1:
                            instrument1[eleve] = data
                        else:
                            if indice_instrument==2:
                                instrument2[eleve] = data
                            else:
                                texteError="ERREUR - indice_instrument %d non valide" % indice_instrument
                                print(texteError)
                    case "Location d'instrument":  # Location Instrument 1
                        if data == "Oui":
                            if indice_instrument==1:
                                location1[eleve] = True
                                prixInstrument[0][eleve] = float(rechercheRrixInstrument(instrument1[eleve]))*float(reduclocation)
                                # PrixTotal[eleve]=PrixTotal[eleve]+prixInstrument[0][eleve] # le prix de la location n'est pas facturé à l'inscription
                        
                            else:
                                if indice_instrument==2:
                                    location2[eleve] = True
                                    prixInstrument[1][eleve] = float(rechercheRrixInstrument(instrument2[eleve]))*float(reduclocation)
                                    # PrixTotal[eleve]=PrixTotal[eleve]+prixInstrument[1][eleve] # le prix de la location n'est pas facturé à l'inscription
                                else:
                                    texteError="ERREUR - indice_instrument %d non valide" % indice_instrument
                                    print(texteError)
                        
                    case "Taille de l'élève en cm" | "Taille de l'élève  en cm":  # Taille eleve
                        taille[eleve] = data
                    case "Lundi" | "Mardi" | "Mercredi" | "Jeudi" | "Vendredi" | "Samedi":  # Jour de preference
                        if len(data)>0:
                          match data.casefold():
                            case "jour possible":
                                if len(jourpossible[eleve]) == 0:  # Aucun jour encore défini
                                    jourpossible[eleve] = liste_entete[count - 1] # jour
                                else:
                                    jourpossible[eleve] = jourpossible[eleve] + " + " + liste_entete[count - 1] # jour
                            case  "jour impossible":
                                if len(jourimpossible[eleve]) == 0:  # Aucun jour encore défini
                                    jourimpossible[eleve] = liste_entete[count - 1] # jour
                                else:
                                    jourimpossible[eleve] = jourimpossible[eleve] + " + " + liste_entete[count - 1] # jour
                            case "peut-être":
                                if len(jourpeut_etre[eleve]) == 0:  # Aucun jour encore défini
                                    jourpeut_etre[eleve] = liste_entete[count - 1] # jour
                                else:
                                    jourpeut_etre[eleve] = jourpeut_etre[eleve] + " + " + liste_entete[count - 1] # jour
                            case other:
                                texteError="ERREUR jour valeur '%s' pour l'entete '%s' non traitée" % (data,liste_entete[count-1])
                                print(texteError)
                                ecrire_log(texteError)
                          # Fin case data
                        # fin si len
                    
                    case "Remarques sur vos disponibilités":  # Remarque sur dispo
                        remarqueDispo[eleve] = data
                    case "Donnez le nom du professeur de l'année passée":  # Nom prof
                        nomProf[eleve] = data
                    
                    case "Nom des groupes":  # Nom des groupes
                        nomGroupe[eleve] = data
                    case "NOM et Prénom" | "Nom / Prénom" :  # Nom et prenom contact
                        indice_contact=indice_contact+1
                        contact[indice_contact-1]['nom'] = data
                    case "Tél portable":
                        contact[indice_contact-1]['tel'] = data
                    case "Email":
                        contact[indice_contact-1]['mail'] = data
                    case "Avez-vous déménager depuis l'inscription de l'an dernier":
                        if (data=="Oui"):
                            contact[indice_contact-1]['changementAdd']=True
                        else:
                            contact[indice_contact-1]['changementAdd']=False
                    case "Numéro et nom de rue":
                        if not (data==""):
                            contact[indice_contact-1]['adresse']=data
                    case "Ville":
                        contact[indice_contact-1]['ville'] = data
                        if data != "Autre" and data !="":
                            prixExterieurEleve = [0,0,0,0]
                            ecrire_log("Non Exterieur  " + str(prixExterieurEleve) + " Data: " + data)
                    case "Préciser le code postal et la ville":  # ville si autre
                        if data != "":
                            contact[indice_contact-1]['ville'] = data
                    case "Commentaires":
                        commentaire = data[:len(data) - 2]  # Ne prend pas le dernier caratère qui est un ""]
                    case "Cocher la case pour valider le choix du cours collectif" | "\"Séquentiel" | "SID" | "Heure de soumission" | "Heure de complétion" | "Heure de modification" | "Heure de modification" | "UID" | "Nom d'utilisateur" | "Adresse IP" | "Age au 01/09/2024":
                        # On ne fait rien, pas de traitement nécessaire
                        pasDeTraitement=True
                    case "Avez-vous changer de banque depuis l'inscription de l'an dernier":
                        if data=="Oui":
                            changeBanque=True
                        else:
                            changeBanque=False
                    case "J'autorise mon enfant (mineur) à quitter seul l'AMHV à la fin de ces cours":
                        if data=="Non":
                            autoriseSortie=False
                        else:
                            autoriseSortie=True
                    case other:
                        if not (data == ""):
                            texteError="ERREUR entete '%s' non traitee, data '%s'" % (liste_entete[count-1],data)
                            print(texteError)
                            ecrire_log(texteError)        

                # fin match count
            # fin si case ="X"
            
        # fin for, colonne suivante
        
        if count > 10:
            PrixFamille = 0

            if typeReglement[:3] == " + ":  # On suprime le + devant
                typeReglement = typeReglement[3:]

            for indice in range(int(nb_inscrit)):
                # print("Calcul prix")
                # Calcul du prix famille
                if prixExterieurEleve[indice] > 0:
                    # On passe le prix exterieur à 0 si pas de cours autre que orchestre
                    if Acc[1][indice] == 0 and coursRock[1][indice] == 0 and ParcoursCol[1][indice] == 0 and \
                            ParcoursComplet[1][indice] == 0:
                        prixExterieurEleve[indice] = 0
                # fin si prixexterieur

                PrixFamille = PrixFamille + PrixTotal[indice] + prixExterieurEleve[indice]
                prixExterieur=prixExterieur+prixExterieurEleve[indice]
                # print("Log")

                ecrire_log("eleve: " + str(indice) + " ;; nb colonne:" + str(count) + " ;; prix eleve:" + str(
                    PrixTotal[indice]) + " ;; Prix exterieur:" + str(prixExterieurEleve[indice]) +" ;; Etat:" + etat + " ;; nb inscrit:" + str(nb_inscrit) + " ;; nom:" + nom[indice] +
                           " ;; prenom:" + prenom[indice] + " ;; age:" + str(age[indice]) + " ;; reinscription:" + str(
                    reinscription[indice]) +
                           " ;; NiveauScolaire:" + NiveauScolaire[indice] + " ;; ParcoursCol:" + ParcoursCol[0][
                               indice] + " ;; Prix: " + str(ParcoursCol[1][indice]) +
                           " ;; parcours:" + ParcoursComplet[0][indice] + " ;; Prix: " + str(
                    ParcoursComplet[1][indice]) + " ;; accompagnement:" + Acc[0][indice] + " ;; Prix: " + str(
                    Acc[1][indice]) + " ;; chant:" + str(CoursChant[indice]) +
                           " ;; instrument1:" + instrument1[indice] + " ;; location1:" + str(
                    location1[indice]) + " ;; instrument2:" + instrument2[indice] +
                           " ;; location2:" + str(location2[indice]) + " ;; taille:" + taille[indice] + " ;; preference:" +
                           jourpossible[indice] +
                           " ;; impossible:" + jourimpossible[indice] + " ;; peut-être:" + jourpeut_etre[
                               indice] + " ;; remarquedispo:" + remarqueDispo[indice] +
                           " ;; nom prof:" + nomProf[indice] + " ;; orchestre:" + orchestre[0][indice] + " ;; Prix: " + str(
                    orchestre[1][indice]) +
                           " ;; groupe rock:" + coursRock[0][indice] + " ;; Prix: " + str(
                    coursRock[1][indice]) + " ;; nom groupe:" + nomGroupe[indice]+" ;; coursFMO" + CoursFMO[indice])
                # fin for indice, fin nombre inscrit
            
            for indice in range(nbeleve_max):
                ecrire_csv(str(PrixTotal[indice]) + separateur_csv + str(prixExterieurEleve[indice]) + separateur_csv + nom[indice] + separateur_csv + prenom[indice] + separateur_csv + str(age[indice]) + separateur_csv + dateNaissance[indice] + separateur_csv + str(reinscription[indice]) + 
                    separateur_csv + NiveauScolaire[indice] + separateur_csv + ParcoursCol[0][indice] + separateur_csv + str(ParcoursCol[1][indice]) + separateur_csv + ParcoursComplet[0][indice] + separateur_csv + str(ParcoursComplet[1][indice]) + separateur_csv + Acc[0][indice] + 
                    separateur_csv + str(Acc[1][indice]) + separateur_csv + str(CoursChant[indice]) + separateur_csv + instrument1[indice] + separateur_csv + str(location1[indice]) + separateur_csv + str(prixInstrument[0][indice]) +separateur_csv + instrument2[indice] + 
                    separateur_csv + str(location2[indice]) + separateur_csv + str(prixInstrument[1][indice]) + separateur_csv + taille[indice] + separateur_csv + jourpossible[indice] +
                    separateur_csv + jourimpossible[indice] + separateur_csv + jourpeut_etre[indice] + separateur_csv + remarqueDispo[indice] + separateur_csv + nomProf[indice] + separateur_csv + orchestre[0][indice] + separateur_csv + str(orchestre[1][indice]) +
                    separateur_csv + coursRock[0][indice] + separateur_csv + str(coursRock[1][indice]) + separateur_csv + nomGroupe[indice] + separateur_csv + CoursFMO[indice] + separateur_csv)

            ecrire_csv(etat + separateur_csv)
            for indice in range(2):
                ecrire_csv(contact[indice]['nom'] + separateur_csv + contact[indice]['tel'] + separateur_csv + contact[indice]['mail'] + separateur_csv + contact[indice]['ville'] + separateur_csv + contact[indice]['adresse'] + separateur_csv + str(contact[indice]['changementAdd'])+separateur_csv)
            ecrire_csv(str(facture) + separateur_csv + str(dispositifSortir) + separateur_csv + str(volontaire) + separateur_csv + str(autorisePhoto) + separateur_csv + typeReglement + separateur_csv + str(changeBanque) + separateur_csv + str(autoriseSortie) + separateur_csv + commentaire + separateur_csv)

            ecrire_log(" contact1:" + contact[0]['nom'] + " ;; tel1:" + contact[0]['tel'] + "  ;; mail1:" + contact[0][
                'mail'] + "  ;; ville1:" + contact[0]['ville'] +
                       "  ;; contact2:" + contact[1]['nom'] + "  ;; tel2:" + contact[1]['tel'] + "  ;; mail2:" + contact[1][
                           'mail'] + "  ;; ville2:" + contact[1]['ville'] + "  ;; facture:" + str(facture) + "  ;; sortir:" + str(
                dispositifSortir) + "  ;; aide:" + str(volontaire) +
                       "  ;; photo:" + str(autorisePhoto) + "  ;; prelevement:" + typeReglement + "  ;; autorise sortie:" + str(
                autoriseSortie) + "  ;; commentaire:" + commentaire)

            # calcul reduction famille
            if PrixFamille >= int(maConfig['Divers.PRIX']['minReduc']):
                reductionFamille = int(maConfig['Divers.PRIX']['reducFamille']) * (int(nb_inscrit) - 1)
                if int(nb_inscrit) > 1:
                    PrixFamille = PrixFamille - reductionFamille
            PrixFamille=PrixFamille+cotisationFamille  # prix de l'adhesion
            ecrire_csv(str(prixExterieur) + separateur_csv + str(PrixFamille)+ separateur_csv + str(reductionFamille)+ separateur_csv + str(cotisationFamille) + "\n")
            ecrire_log(" Prix exterieur inclus dans prixFamille: " + str(prixExterieur) + "  ; Prix Famille:" + str(PrixFamille)+" ; reductionFamille: " + str(reductionFamille))

            if etat == "valide":
                # Génération du PDF
                nom_tmp = contact[0]['nom']
                # Traitement ici pour éviter les noms de fichier du type 'inscription_MITTAUD_Geneviève_(_mamie).pdf' ;)
                l_mots = nom_tmp.split(' ')
                nom_tmp = '_'.join(l_mots[:2])
                mailDestinataire = contact[0]['mail']
                nom_pdf = 'inscription_' + nom_tmp + '.pdf'
                fic_pdf = os.path.join(REP_PDFS, nom_pdf)
        
                # On verifie si le fichier existe, si oui on ajoute la date de creation sur la derniere version
                if os.path.exists(fic_pdf) and args.s:
                    fic_pdf_prec=fic_pdf
                    fic_pdf=os.path.dirname(fic_pdf)+"/"+Path(fic_pdf).stem+datetime.today().strftime("%Y_%m_%d_%H_%M_%S")+".pdf"
                    print("WARNING ----- fichier PDF: '%s' existe déjà, renomme le fichier avec date du jour %s" % (fic_pdf_prec,fic_pdf))
                    ecrire_log("WARNING ----- fichier PDF: '%s' existe déjà, renomme le fichier avec date du jour %s" % (fic_pdf_prec,fic_pdf))
                    
        

                status, msg = generate_pdf(fic_pdf, globals(), debug=True)
                if status:
                    ecrire_log("OK: fichier PDF: '%s' / répertoire fichiers Latex: '%s'" % (fic_pdf, msg))
                else:
                    ecrire_log("Erreur: " + msg)
                    print("Erreur:", msg)
                    _ = input("Appuyer sur Entrée pour continuer ...")

                # Envoie du mail si spécifié en ligne de commande et si fichier généré proprement
                if args.m and status:
                    if not in_resume(mailDestinataire): # On envoie le mail si pas déjà envoyé
                        ecrire_log("Envoie du mail à: " + mailDestinataire)
                        try:
                            cc=maConfig['Mail']['cc']
                        except KeyError:
                            cc=""
                            ecrire_log("Attention -- Pas de champs cc dans le fichier de config pour le mail")
                        status, msg = envoieMail(mailDestinataire, fic_pdf, pwd_sender, sender_user=sender,cc_mail=cc)
                        if status:
                            ecrire_log("envoie mail OK ; tempo  ...")
                            ecire_resume(mailDestinataire+"  send the "+datetime.today().strftime("%Y-%m-%d %H:%M"))
                            # Petite tempo pour ne pas risquer de générer un DOS sur le serveur
                            time.sleep(2)
                        else:
                            ecrire_log("ERREUR ----- : " + msg)
                            print("Erreur:", msg)
                            _ = input("Appuyer sur Entrée pour continuer ...")
                    else: # Le mail a déjà ete envoye, on ne le renvoie pas, meme si un deuxieme fichier existe
                        ecrire_log("ERREUR ----- Mail déjà envoye à :"+mailDestinataire+" fichier "+fic_pdf+" non envoyé")
                        print("ERREUR -----  Mail déjà envoye à :"+mailDestinataire+" fichier "+fic_pdf+" non envoyé")
                        _ = input("Appuyer sur Entrée pour continuer ...")

        # fin si count>10

        line = fichierSource.readline()
# fin while, ligne suivante
fichierSource.close()
fichierLog.close()

# Clean fichiers si tout s'est bien passé
# Pas de gestion d'erreur sur la commande rm car elle génère systématiquement: "rm: impossible de
# supprimer 'inscription.*': Aucun fichier ou dossier de ce nom" alors que les fichiers inscription.* sont bien
# supprimés ...
cmd = 'rm inscription.*'
subprocess.run(shlex.split(cmd))
