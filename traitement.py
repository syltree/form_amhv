from datetime import datetime
#from pylatex import Document, Section, Subsection, Command
#from pylatex.utils import italic, NoEscape
# Installer le compilateuir latex: sudo apt-get install texlive-pictures texlive-science texlive-latex-extra latexmk

# fonctionne avec le resultat telecharger en csv avec le séparateur ";"  et en mode separe
from fpdf import FPDF


prixDecJardin=100
prixDecEveil=180
prixDecOrc=180
prixDecInst=350
prixParcColl=[420,470] # <21a, >21a
prixParcInd25=[520,570] # <21a, >21a
prixParcInd30=[610,660] # <21a, >21a
prixAccInd25=[500,550] # <21a, >21a
prixAccInd30=[340,370] # <21a, >21a
prixAccElec=[340,370] # <21a, >21a
prixOrcJunior=[60,80] # parcours, hors parcours
prixOrcEcole=[60,80] # parcours, hors parcours
prixOrcChoral=[60,80] # parcours, hors parcours
prixOrcHarmonie=[60,130] # parcours, hors parcours
prixGroupeRock=[180,320]  # parcours, hors parcours
prixGroupJazz=[180,320] # parcours, hors parcours
prixGroupAut=50
prixLoc=150
prixLocGuit=60
prixLocHaut=180
prixExterieur=80 # Prix pour une personne exterieur aux communes
IndiceAge=0	 # Indice pour le prix selon l'age
IndiceParcours=0 # Indice pour le prix selon le parcours, 0 dans la parcours 1 sinon
CstReducFamille=15 # prix de la reduction Famille a partir du 2eme adherent au de à de minReduc
CstminReduc=900 # Prix minimum pour obtenir la reduc famille
cotisationFamille=30

def ecrire_log(data):
	fichierLog.write(data+"\n")

def ecrire_dest(data):
	fichierDestination.write(data)

def extraireNomParcours(data):
    # Fontion permettant d'extraire le nom du parcours lorsque contient <strong>
  result=""
  if len(data)>0:
    result=data[8:]
    # print("result0:"+result)
    result=result[:result.find("strong")-2]
    # print("result1:"+result)
  return result

def extrairePrix(data,age,boolparcours):
    # Fontion permettant de retourner le prix selon le type de formation choisie, l'age et si ou non dans le parcours
  result=0
  age=1
  indicePrix=1
  if inf21a:
  	age=0
  if boolparcours:
  	indicePrix=0
  	 
  if len(data)>0:
    match data:
      case "JARDIN MUSICAL, pour PS":
        result=prixDecJardin
      case "EVEIL A LA MUSIQUE":
       	result=prixDecEveil
      case "JE DECOUVRE LES INSTRUMENTS DE L'ORCHESTRE, pour CP":
       	result=prixDevOrc
      case "1ère ANNEE DE PRATIQUE INSTRUMENTALE, obligatoire du CE1 au CM2" | "2ème ANNEE DE PRATIQUE INSTRUMENTALE, optionnelle":
       	result=prixDecInst
      case "PARCOURS: COURS COLLECTIF":
       	result=prixParcColl[age]
      case "PARCOURS: COURS INDIVIDUEL 25mn":
        result=prixParcInd25[age]
      case "PARCOURS: COURS INDIVIDUEL 30mn":
        result=prixParcInd30[age]
      case "COURS INDIVIDUEL 25mn":
       	result=prixAccInd25[age]
      case "COURS INDIVIDUEL 30mn":
        result=prixAccInd30[age]
      case "MUSIQUE ELECTRONIQUE":
        result=prixAccElec[age]
      case "ORCHESTRE JUNIOR CORDES ET VENTS":
        result=prixOrcJunior[indicePrix]
      case "CHORALE ENFANTS A L'ECOLE":
        result=prixOrcEcole[indicePrix]
      case "CHORALE ADULTE":
        result=prixOrcChoral[indicePrix]
      case "ORCHESTRE HARMONIE":
        result=prixOrcHarmonie[indicePrix]
      case "GROUPE ROCK":
        result=prixGroupeRock[indicePrix]
      case "ATELIER JAZZ":
        result=prixGroupJazz[indicePrix]
      case"Accès à la pratique autonome":
        result=prixGroupAut
     # Fin match
    textelog="function prix -data: "+data+" -prix: "+str(result)
    if result==0:
      print ("ERREUR, prix 0 alors que valeur définie")
      textelog=textelog+" ------ ERROR PRIX NUL ------ "
    # print("data: "+data+" prix:"+str(result))
    if indicePrix==0:
      textelog=textelog+" dans parcours"
    if age==0:
      textelog=textelog+" moins de 21 ans"
    ecrire_log(textelog)
    
  
    # Fin Si
  return result
# Fin recherche prix

def rechercheRrixInstrument(instrument):
  match instrument:
    case "Les instruments amplifiés : guitare électrique" | "Les cordes : guitare classique":
      return 60
    case "Les instruments traditionnels : harpe celtique":
      return 180
    case _:
      return 160
    
# Fin rechercheRrixInstrument



def cre_fichier_inscription():
  
  pdf = FPDF('P', 'mm', 'A4')  # Mode portrait, utilisation des mm et page A4
  pdf.add_page()
  pdf.set_font('Arial', 'B', 10) # Arial, Bold 16
  hauteur=5
  largeur=0
  margelist=20
  
  #doc = Document(nom[0])
  """Add a section, a subsection and some text to the document.
      :type doc: :class:`pylatex.document.Document` instance
  """
  indice_eleve=0
  for indice_eleve in range (int(nb_inscrit)):
     pdf.set_font('Arial', 'B', 12) # Arial, Bold 12
     pdf.cell(largeur,hauteur+2,"Elève"+str(indice_eleve+1),0,1)
     pdf.set_font('Arial', 'B', 11) # Arial, Bold 11
     pdf.cell(largeur,hauteur+1,"Identité",0,1)
     pdf.set_font('Arial', '', 10) # Arial, 10
     pdf.cell(largeur,hauteur,prenom[indice_eleve]+" "+nom[indice_eleve],0,1)
     if age[indice_eleve]!="":
      pdf.cell(largeur,hauteur,"Age: "+age[indice_eleve],0,1)
     if NiveauScolaire[indice_eleve]!="":
        pdf.cell(largeur,hauteur,"Niveau Scolaire: "+NiveauScolaire[indice_eleve],0,1)
     pdf.set_font('Arial', 'U', 10) # Arial, Souligné
     if ParcoursCol[indice_eleve]!="" or ParcoursComplet[indice_eleve]!="":
      pdf.cell(largeur,hauteur+1,"Inscrit aux cours dans le parcours suivant: ",0,1)  
     else:
        pdf.cell(largeur,hauteur+1,"Inscrit aux cours hors parcours suivant: ",0,1)
     pdf.set_font('Arial', '', 10) 
     if ParcoursCol[indice_eleve]!="":
        pdf.cell(largeur,hauteur,"\t - Parcours découverte de la musique en cours collectifs - "+ParcoursCol[indice_eleve],0,1)
     if ParcoursComplet[indice_eleve]!="":
        pdf.cell(largeur,hauteur,"\t - Parcours complet - (Instrument ou chant + 45 mn de FM ou MAO) - "+ParcoursComplet[indice_eleve],0,1)
     if Acc[indice_eleve]!="":
        pdf.cell(largeur,hauteur,"\t - Accompagnement à la pratique amateur(sans formation musicale)",0,1)
        for data in Acc[indice_eleve].split(" + "):
          pdf.set_x(margelist)
          pdf.cell(largeur,hauteur," - "+data,0,1)
     if orchestre[indice_eleve]!="":
       pdf.cell(largeur,hauteur,"\t - Ensembles et Ateliers",0,1)
       for data in orchestre[indice_eleve].split(" + "):
          pdf.set_x(margelist)
          pdf.cell(largeur,hauteur," - "+data,0,1)
     if coursRock[indice_eleve]!="":
       pdf.cell(largeur,hauteur,"\t - GROUPES ROCK/ATELIER JAZZ - Accessibles aux élèves sur validation de l'''enseignant",0,1)
       for data in coursRock[indice_eleve].split(" + "):
          pdf.set_x(margelist)
          pdf.cell(largeur,hauteur," - "+data,0,1)
       pdf.cell(largeur,hauteur,"\t Dans les groupes "+nomGroupe[indice_eleve] ,0,1)
     pdf.set_font('Arial', 'U', 10) # Arial, Souligné
     if instrument1[indice_eleve]!="" or instrument2[indice_eleve]!="":
      pdf.cell(largeur,hauteur+1,"Avec les instruments: ",0,1)  
      pdf.set_font('Arial', '', 10) # Arial
      if instrument1[indice_eleve]!="":
        pdf.write(hauteur,"\t - "+instrument1[indice_eleve])
        if location1[indice_eleve]==True:
          pdf.write(hauteur,", qui sera loué")
        pdf.ln()
      if instrument2[indice_eleve]!="":
        pdf.write(hauteur,"\t - "+instrument2[indice_eleve],0,0)
        if location2[indice_eleve]==True:
          pdf.write(hauteur,", qui sera loué")
        pdf.ln()
     if CoursChant[indice_eleve]==True:
      pdf.cell(largeur,hauteur+1,"Est inscrit aux cours de chant ",0,1)  
     pdf.set_font('Arial', '', 10) # Arial
     if nomProf[indice_eleve]!="":
       pdf.cell(largeur,hauteur," Le professeur de l'année dernière était: "+nomProf[indice_eleve])
       pdf.cell(largeur,hauteur," Les jours de cours possibles sont: "+jourpossible[indice_eleve])
       pdf.cell(largeur,hauteur," Les jours de cours impossibles sont: "+jourimpossible[indice_eleve])
       pdf.cell(largeur,hauteur," Les jours de cours dépendnat des horaires sont: "+jourpeut_etre[indice_eleve])
       pdf.cell(largeur,hauteur," Remarque sur la disponibilité: "+remarqueDispo[indice_eleve])
       
       
     

  #  with doc.create(Section('Elève '+str(indice_eleve+1),False)):
   #       doc.create(Subsection('Identité',False))
    #      doc.append(prenom[indice_eleve]+" "+nom[indice_eleve])
     #     doc.append("\n")
      #    doc.append("Age :"+age[indice_eleve])


            
    # fin pour indice
  #doc.generate_pdf(clean_tex=False)
  pdf.output(nom[0]+"_fpdf.pdf", 'F')
  

# fin cre_fichier_inscription



# Debut prog
if __name__ == '__main__':
  fichierSource = open("Atraiter.csv", "r",encoding='UTF-8')
  fichierDestination = open("Dest.txt", "w")
  fichierLog=open("Log.txt","w")

  ecrire_log("\n\n\n ***********************   "+ datetime.today().strftime("%Y-%m-%d %H:%M") +"   ************ \n\n\n")

  # on récupère la 1ere ligne de donnée du fichier, les 3 eres sont les entetes
  line=fichierSource.readline()
  line=fichierSource.readline()

  line=fichierSource.readline()
  liste_entete=line.split("\";\"") # contient les entetes

  # On traite la ligne
  line=fichierSource.readline()
  while line:  # On parcours l'ensemble des fiches
    # declaration des tableaux, pour chaque eleve
    nom=["","","",""]
    prenom=["","","",""]
    age=["","","",""]
    reinscription=[False,False,False,False]
    NiveauScolaire=["","","",""]
    ParcoursCol=[["","","",""],[0,0,0,0]]   # Nom , prix
    ParcoursComplet=[["","","",""],[0,0,0,0]]   # Nom , prix
    Acc=[["","","",""],[0,0,0,0]]   # Nom , prix
    CoursChant=[False,False,False,False]
    PrixTotal=[0,0,0,0]
    instrument1=["","","",""]
    location1=[False,False,False,False]
    instrument2=["","","",""]
    location2=[False,False,False,False]
    taille=["","","",""]
    remarqueDispo=["","","",""]
    nomProf=["","","",""]
    orchestre=[["","","",""],[0,0,0,0]]   # Nom , prix
    coursRock=[["","","",""],[0,0,0,0]]   # Nom , prix
    nomGroupe=["","","",""]
    jourpossible=["","","",""]
    jourimpossible=["","","",""]
    jourpeut_etre=["","","",""]
    prixInstrument=[[0,0,0,0],[0,0,0,0]] # location instrument 1, instrument 2 
    contact=[{'nom':"", 'tel':"",'mail':"",'ville':""},{'nom':"", 'tel':"",'mail':"",'ville':""}]
    typeReglement=""
    reductionFamille=0
    nf21a=False
    parcours=False
     
    ecrire_log(line)
    liste_data=line.split("\";\"")
    count=0
    eleve=-1
    nb_inscrit=0
    facture=False
    dispositifSortir=False
    volontaire=False
    autorisePhoto=False
    autoriseSortie=True
    for data in liste_data: # On parcours les info de la fiche
     count=count+1
     nomcoursAcc=""
     nomcoursOrc=""
     nomcoursRock=""
     jour=""
     match count:
      case 6: 
         if liste_entete[count-1]!="Brouillon":
          print("Erreur entete non correcte")
          ecrire_log("Erreur entete non correcte: "+liste_entete[count-1]+" numéro colonne: "+str(count))
         match data:
             case "1":
               etat="brouillon"
             case "0":
               etat="valide"
      # fin match data
      case 10:  # Nb inscrit
        if liste_entete[count-1]!="Nombre d'élève à inscrire":
          print("Erreur entete non correcte")
          ecrire_log("Erreur entete non correcte: "+liste_entete[count-1]+" numéro colonne: "+str(count))
        nb_inscrit=data
      case 11 | 46 | 81 | 116: # nom
        if liste_entete[count-1]!="Nom" and liste_entete[count-1]!="Nom  (si différent de l'élève 1)":
          print("Erreur entete non correcte")
          ecrire_log("Erreur entete non correcte: "+liste_entete[count-1]+" numéro colonne: "+str(count))
        eleve=eleve+1 # On a un nouvel eleve
        parcours=False  # On initialise le parcours a false, le met a true si une formation dans le parcours est choisie plus tard
        if data=="":  # Le nom est vide, on prend donc le nom de l'elever precedent (le 1er ne peut pas etre vide)
            nom[eleve]=nom[eleve-1]
        else:  
            nom[eleve]=data
      case 12 | 47 | 82 | 117: # prenom
        if liste_entete[count-1]!="Prénom":
          print("Erreur entete non correcte")
          ecrire_log("Erreur entete non correcte: "+liste_entete[count-1]+" numéro colonne: "+str(count))
        prenom[eleve]=data
      case 13 | 48 | 83 | 118: # age
        if liste_entete[count-1]!="Age au 01/09/2024":
          print("Erreur entete non correcte")
          ecrire_log("Erreur entete non correcte: "+liste_entete[count-1]+" numéro colonne: "+str(count))
        age[eleve]=data
        if data=="> 21 ans":
            inf21a=False
        else:
            inf21a=True
        # print("eleve :"+str(eleve)+" nb inscrit:"+nb_inscrit+" age:"+age[eleve]+" source:"+data)
      case 14 | 49 | 84 | 119: # reinscription
          if data=="nouvel inscrit":
              reinscription[eleve]=False
          else:
              reinscription[eleve]=True
      case 15 | 50 | 85 | 120: # Niveau scolaire
          NiveauScolaire[eleve]=data
      case 16 | 51 | 86 | 121: # Parcours decouverte de la musique en cours collectif
          if data[:6]=="Pas de":
            data=""   
          if len(data)>0:
            parcours=True
            ParcoursCol[0][eleve]=extraireNomParcours(data)
            ParcoursCol[1][eleve]=extrairePrix(ParcoursCol[0][eleve],inf21a,parcours)
            PrixTotal[eleve]=PrixTotal[eleve]+ParcoursCol[1][eleve]
      case 17 | 52 | 87 | 122: # Parcours complet - instrument ou champs + FM
          if data[:6]=="Pas de":
            data=""   
          if len(data)>0:
            parcours=True
            ParcoursComplet[0][eleve]=extraireNomParcours(data)
            ParcoursComplet[1][eleve]=extrairePrix("PARCOURS: "+ParcoursComplet[0][eleve],inf21a,parcours)  # On ajoute PARCOURS pour différentier la pratique amateur 
            PrixTotal[eleve]=PrixTotal[eleve]+ParcoursComplet[1][eleve]
      case 19 | 54 | 89 | 124: # Instrument ou chant 
          if data=="X":
            nomcoursAcc="COURS INDIVIDUEL 25mn"
      case 20 | 55 | 90 | 125: # Instrument ou chant 
          if data=="X": 
            nomcoursAcc="COURS INDIVIDUEL 30mn"
      case 21 | 56 | 91 | 126: # Instrument ou chant 
          if data=="X": # 
            nomcoursAcc="MUSIQUE ELECTRONIQUE"
      case 22 | 57 | 92 | 127:  # Cours de chant 
         if data=="Oui":
            CoursChant[eleve]=True
      case 23 | 58 | 93 | 128: # Nom Instrument 1
        instrument1[eleve]=data
      case 24 | 59 | 94 | 129: # Location Instrument 1
        if data=="Oui":
          location1[eleve]=True
          prixInstrument[0][eleve]=rechercheRrixInstrument(instrument1[eleve])
          prixTotal[eleve]=PrixTotal[eleve]+prixInstrument[0][eleve]
          # print ("location1 Oui pour eleve:"+str(eleve)+nom[eleve])
      case 25 | 60 | 95 | 130: # Nom Instrument 2
        instrument2[eleve]=data
      case 26 | 61 | 96 | 131: # Location Instrument 2
        if data=="Oui":
          location2[eleve]=True
          prixInstrument[1][eleve]=rechercheRrixInstrument(instrument2[eleve])
          prixTotal[eleve]=PrixTotal[eleve]+prixInstrument[1][eleve]
      case 27 | 62 | 97 | 132: # Taille eleve
        taille[eleve]=data
      case 28 | 63 | 98 | 133: # Jour de preference
        if len(data)>0:
          jour="lundi"
      case 29 | 64 | 99 | 134: # Jour de preference
        if len(data)>0:
          jour="mardi"
      case 30 | 65 | 100 | 135: # Jour de preference
        if len(data)>0:
          jour="mercredi"
      case 31 | 66 | 101 | 136: # Jour de preference
        if len(data)>0:
          jour="jeudi"
      case 32 | 67 | 102 | 137: # Jour de preference
        if len(data)>0:
          jour="vendredi"
      case 33 | 68 | 103 | 138: # Jour de preference
        if len(data)>0:
          jour="samedi"
      case 34 | 69 | 104 | 139: # Remarque sur dispo
        remarqueDispo[eleve]=data
      case 35 | 70 | 105 | 140: # Nom prof
        nomProf[eleve]=data
      case 37 | 72 | 107 | 142: # Orchestre et chorale
        if data=="X":
            nomcoursOrc="ORCHESTRE JUNIOR CORDES ET VENTS"
      case 38 | 73 | 108 | 143: # Orchestre et chorale
        if data=="X":
            nomcoursOrc="CHORALE ENFANTS A L'ECOLE"
      case 39 | 74 | 109 | 144: # Orchestre et chorale
        if data=="X":
            nomcoursOrc="CHORALE ADULTE"
      case 40 | 75 | 110 | 145: # Orchestre et chorale
        if data=="X":
            nomcoursOrc="ORCHESTRE HARMONIE"
      case 42 | 77 | 112 | 147: # Groupe Rock
        if data=="X":
            nomcoursRock="GROUPE ROCK"
      case 43 | 78 | 113 | 148: # Groupe Rock
        if data=="X":
            nomcoursRock="ATELIER JAZZ"
      case 44 | 79 | 114 | 149: # Groupe Rock
        if data=="X":
            nomcoursRock="Accès à la pratique autonome"
      case 45 | 80 | 115 | 150: # Nom des groupes
            nomGroupe[eleve]=data
      case 151: # Nom et prenom contact
        contact[0]['nom']=data
      case 152: 
        contact[0]['tel']=data
      case 153:
        contact[0]['mail']=data
      case 154:
        contact[0]['ville']=data
        if data!="Autre":
          prixExterieur=0
      case 155: # ville si autre
        if data!="":
          contact[0]['ville']=data
      case 156:
        contact[1]['nom']=data  
      case 157:
        contact[1]['tel']=data
      case 158:
        contact[1]['mail']=data
      case 159:
        contact[1]['ville']=data
        if data!="Autre":
          prixExterieur=0
      case 160: # ville si autre
        if data!="":
          contact[1]['ville']=data
      case 161: # Info complementaire
        if data=="X":
          facture=True
      case 162: # Info complementaire
        if data=="X":
          dispositifSortir=True
      case 163: # Info complementaire
        if data=="X":
          volontaire=True
      case 164: # Info complementaire
        if data=="X":
          autorisePhoto=True
      case 165 : # Reglement
        if data=="X":
          typeReglement="Règlement de l'intégralité"
      case 166 : # Reglement
        if data=="X":
          typeReglement=typeReglement+ " + "+"Règlement par chèque en 3 fois"
      case 167 : # Reglement
        if data=="X":
          typeReglement=typeReglement+ " + "+"Par prélèvement en 5 fois (vers le 8 des mois d'octobre 2024, novembre 2024, décembre 2024, février 2025 et mars 2025) -  - le SEPA et le RIB sont alors nécessaire"
      case 168: # Reglement
        if data=="X":
          typeReglement=typeReglement+ " + "+"Par prélèvement en 1 fois  - le SEPA et le RIB sont alors nécessaire"
      case 169: # Reglement
        if data=="X":
          typeReglement=typeReglement+ " + "+"Par chèques vacances - un chèque de caution est alors nécessaire"
      case 177: # Autorise sortie
        if data=="non":
          autoriseSortie=False
      case 178:
        commentaire=data[:len(data)-2] # Ne prend pas le dernier caratère qui est un ""]

     # fin match count
     
     if len(nomcoursRock)>0:  # L'eleve a choisi un cours Rock ou Atelier
       # On défini le prix
       prixtemp=extrairePrix(nomcoursRock,inf21a,parcours)
       coursRock[1][eleve]=coursRock[1][eleve]+prixtemp
       PrixTotal[eleve]=PrixTotal[eleve]+prixtemp
       if len(coursRock[0][eleve])==0: # Aucun cours n'a encore été choisi, c'est le 1er
         coursRock[0][eleve]=nomcoursRock
       else:  # un autre cours a deja ete choisi
         coursRock[0][eleve]=coursRock[0][eleve]+" + "+nomcoursRock
       nomcoursRock=""

     if len(nomcoursOrc)>0: # L'eleve a choisi un orchestre
       prixtemp=extrairePrix(nomcoursOrc,inf21a,parcours)
       orchestre[1][eleve]=orchestre[1][eleve]+prixtemp
       PrixTotal[eleve]=PrixTotal[eleve]+prixtemp
       if len(orchestre[0][eleve])==0: # Aucun cours n'a encore été choisi, c'est le 1er
         orchestre[0][eleve]=nomcoursOrc
       else: # un autre cours a deja ete choisi
         orchestre[0][eleve]=orchestre[0][eleve]+" + "+nomcoursOrc
       nomcoursOrc=""

     if len(nomcoursAcc)>0: # l'eleve a choisi une pratique amateur
       prixtemp=extrairePrix(nomcoursAcc,inf21a,parcours)
       Acc[1][eleve]=Acc[1][eleve]+prixtemp
       PrixTotal[eleve]=PrixTotal[eleve]+prixtemp
       if len(Acc[0][eleve])==0:  # Aucun cours n'a encore été choisi, c'est le 1er
         Acc[0][eleve]=nomcoursAcc
       else: # un autre cours a deja ete choisi
         Acc[0][eleve]=Acc[0][eleve]+" + "+nomcoursAcc
       nomcoursAcc=""

     if len(jour)>0:
      if data=="jour possible":
        if len(jourpossible[eleve])==0:  # Aucun jour encore défini
          jourpossible[eleve]=jour
        else:
          jourpossible[eleve]=jourpossible[eleve]+" + "+jour
      if data=="jour impossible":
        if len(jourimpossible[eleve])==0:  # Aucun jour encore défini
          jourimpossible[eleve]=jour
        else:
          jourimpossible[eleve]=jourimpossible[eleve]+" + " +jour
      if data=="peut-être":
        if len(jourpeut_etre[eleve])==0:  # Aucun jour encore défini
          jourpeut_etre[eleve]=jour
        else:
          jourpeut_etre[eleve]=  jourpeut_etre[eleve]+" + "+jour
     jour=""
          
    # fin for, colonne suivante
     
    if count>10: 
      PrixFamille=cotisationFamille # prix de l'adhesion

      if typeReglement[:3]==" + ":  # On suprime le + devant
                ypeReglement=typeReglement[3:]
      

      for indice in range (int(nb_inscrit)):
        # Calcul du prix famille
        PrixFamille=PrixFamille+PrixTotal[indice]+prixExterieur  # prix exterieur est passe à 0 si pas exterieur

        ecrire_log("eleve: "+str(indice)+" nb colonne:"+ str(count)+" prix:"+ str(PrixTotal[indice])+" Etat:"+etat+" nb inscrit:"+str(nb_inscrit)+" nom:"+nom[indice]+
         " prenom:"+prenom[indice]+" age:"+age[indice]+" reinscription:"+str(reinscription[indice])+
         " NiveauScolaire:"+NiveauScolaire[indice]+" ParcoursCol:"+ParcoursCol[0][indice]+" Prix: "+str(ParcoursCol[1][indice])+
         " parcours:"+ParcoursComplet[0][indice]+" Prix: "+str(ParcoursComplet[1][indice])+ "accompagnement:"+Acc[0][indice]+" Prix: "+str(Acc[1][indice])+" chant:"+ str(CoursChant[indice])+
         " instrument1:"+instrument1[indice]+" location1:"+str(location1[indice])+" instrument2:"+instrument2[indice]+
         " location2:"+str(location2[indice])+" taille:"+taille[indice]+" preference:"+jourpossible[indice]+
         " impossible:"+jourimpossible[indice]+" peut-être:"+jourpeut_etre[indice]+" remarquedispo:"+remarqueDispo[indice]+
         " nom prof:"+nomProf[indice]+" orchestre:"+orchestre[0][indice]+" Prix: "+str(orchestre[1][indice])+
         " groupe rock:"+coursRock[0][indice]+" Prix: " +str(coursRock[1][indice])+ " nom groupe:"+nomGroupe[indice])
         # fin for indice, fin nombre inscrit

      ecrire_log(" contact1:"+contact[0]['nom']+" tel1:"+contact[0]['tel']+" mail1:"+contact[0]['mail']+" ville1:"+contact[0]['ville']+
         " contact2:"+contact[0]['nom']+" tel2:"+contact[0]['tel']+" mail2:"+contact[0]['mail']+" ville2:"+contact[0]['ville']+" facture:"+str(facture)+" sortir:"+str(dispositifSortir)+" aide:"+str(volontaire)+
         " photo:"+str(autorisePhoto)+" prelevement:"+typeReglement+" autorise sortie:"+str(autoriseSortie)+" commentaire:"+commentaire)
      
      # calcul reduction famille
      if PrixFamille>=CstminReduc:
        reductionFamille=CstReducFamille*(int(nb_inscrit)-1)
        if int(nb_inscrit)>1:
          PrixFamille=PrixFamille-reductionFamille
      ecrire_log(" Prix Famille:"+str(PrixFamille))
   # fin si count>10

   # On redige le fichier
#   cre_fichier_inscription()
    line=fichierSource.readline()
# fin while
fichierSource.close()


