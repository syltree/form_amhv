#!/usr/bin/python3
"""
Librairie pour la génération du fichier PDF à partir des variables qui ont été parsées dans le programme principal
Fonction à invoquer: generate_pdf
Une partie 'main' est fournie uniquement à titre d'exemple
!!! IMPORTANT !!! nécessite les utilitaires Latex -> installer le paquet 'texlive-latex-recommended' sous Ubuntu
Ressources:
https://texdoc.org/serve/fontspec/0
"""

# IMPORTS
#########

from tempfile import mkdtemp
import re
import os
import subprocess

# DEFINES
#########

# Le nombre max d'élève dans la fiche d'inscription, et donc la taille de chaque tableau
NB_ELEVES_MAX = 4

TEMPLATE_ENTETE = """
%\documentclass[a4paper,12pt,openright,notitlepage,twoside]{book}
\documentclass[a4paper,12pt]{article}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\DeclareUnicodeCharacter{2212}{-}

% Les infos pour maketitle
\\title{Inscription AMHV 2024-2025 pour '@V_contact_principal@'}

\\begin{document}
\maketitle

\section{Informations de contact}
"""

TEMPLATE_CONTACT = """
\\noindent
Nom: @D_contact#nom@ \\\\
Tel: @D_contact#tel@ \\\\
Mail: @D_contact#mail@ \\\\
Ville: @D_contact#ville@ \\\\
"""

TEMPLATE_INSCRIPTIONS = """
\section{Liste des élèves inscrits}
Nombres d'élèves inscrits: @V_nb_inscrit@ \\\\
"""

TEMPLATE_ELEVE = """
\subsection{Elève @D_eleve#prenom@}
Nom: @D_eleve#nom@ \\\\
Age: @D_eleve#age@ \\\\
Taille: @D_eleve#taille@ \\\\
Niveau scolaire: @D_eleve#NiveauScolaire@ \\\\
Parcours collectif: @D_eleve#ParcoursCol_1@ \\\\
Parcours collectif coût: @D_eleve#ParcoursCol_2@ \\\\
Parcours complet: @D_eleve#ParcoursComplet_1@ \\\\
Parcours complet coût: @D_eleve#ParcoursComplet_2@ \\\\
Acc. pratique amateur: @D_eleve#Acc_1@ \\\\
Acc. pratique amateur coût: @D_eleve#Acc_2@ \\\\
Nom professeur: @D_eleve#nomProf@ \\\\
Commentaire sur vos disponibilités: @D_eleve#remarqueDispo@ \\\\
Dispo. piano/guitare jours disponibles: @D_eleve#jourpossible@ \\\\
Dispo. piano/guitare jours éventuels: @D_eleve#jourpeut_etre@ \\\\
Dispo. piano/guitare jours non dispos: @D_eleve#jourimpossible@ \\\\
Pratique orchestre: @D_eleve#orchestre_1@ \\\\
Pratique orchestre coût: @D_eleve#orchestre_2@ \\\\
Pratique groupe: @D_eleve#coursRock_1@ \\\\
Pratique groupe coût: @D_eleve#coursRock_2@ \\\\
Nom groupe: @D_eleve#nomGroupe@ \\\\
Instrument n°1: @D_eleve#instrument1@ \\\\
Location instrument n°1 coût: @D_eleve#prixInstrument_1@ \\\\
Instrument n°2: @D_eleve#instrument2@ \\\\
Location instrument n°2 coût: @D_eleve#prixInstrument_2@ \\\\
Coût total: @D_eleve#PrixTotal@ \\\\

"""

TEMPLATE_COUTS = """
\section{Montant inscription(s)}

Ce tableau récapitule le montant total pour votre inscription. \\\\
\\textbf{Important:} si vous avez demandé la location d'instrument(s), seul le montant sans location est
  à régler pour l'inscription.\\\\

"""

TEMPLATE_FIN = """
\section{Informations complémentaires}

Demande de facture: @V_facture@ \\\\
% TODO fixer Bénéficiaire du dispositif 'Sortir' car variable 'dispositifsortir' non fournie \\\\
Bénévole pour aider: @V_volontaire@ \\\\
Autorise la publication de photo(s): @V_autorisePhoto@ \\\\
Autorisation enfant(s) à sortir seul des cours: @V_autoriseSortie@ \\\\

\\noindent
Vos commentaires lors de l'inscription: @V_commentaire@ \\\\

\\noindent
Pour rappel, vous avez accepté les conditions d'inscriptions suivantes:
\\begin{itemize}
\item[\\textbullet] Je certifie être bien assuré-e au titre de la responsabilité civile ou être assuré-e pour des activités extra-scolaires.
\item[\\textbullet] Avoir pris connaissance du règlement intérieur de l'école et m'engager à le respecter (cf site internet).
\item[\\textbullet] Je dois m'assurer de la présence de l'enseignant au début du cours, l'école déclinant toute responsabilité en cas d'accident en dehors des cours.
\item[\\textbullet] Je dois m'assurer de la prise en charge de chaque élève à l'heure de fin de cours, les enseignants ne pouvant assurer la surveillance passé ce délai.
\item[\\textbullet] J'accepte de me voir refuser un cours collectif ou un ensemble si le nombre minimum d'élèves n'est pas atteint.
\item[\\textbullet] Après 2 cours l'inscription est considérée comme définitive. Toute année commencée est due et non remboursable.
Sauf en cas d'incapacité médicale reconnue ou de déménagement. Dans ce cas prévenir par courrier ou par mail le 
secrétariat 15 jours avant le début d'un trimestre pour être remboursé. Ni la carte d'adhérent ni les 2 premiers cours 
ne sont remboursés.
\item[\\textbullet] Je suis informé·e que les informations recueillies sur ce formulaire sont enregistrées dans un fichier 
informatisé à la seule fin d'organisation des activités, de contact en cas d'urgence et de facturation. Elles sont 
conservées aussi longtemps que vous êtes susceptible de participer aux activités. Hormis les professeurs en charge de 
l'activité, nous nous engageons à ne communiquer aucune de vos données à des tiers, même partenaires. Conformément 
au RGPD, vous pouvez exercer votre droit d'accès aux données vous concernant et les faire rectifier en vous adressant 
au secrétariat.
\end{itemize}

\\noindent
\\textbf{IMPORTANT:}
\\begin{itemize}
\item[\\textbullet] Vous disposez de 8 jours pour régler le montant de cette inscription.
\item[\\textbullet] Si vous avez souscrit un cours collectif, il est nécessaire de passer au secrétariat pour la réservation du créneau. 
\end{itemize}

\end{document}
"""

# FONCTIONS
###########

def get_variable(nom_variable:str, raise_exception=True):
    # Cette fonction retourne la valeur de la variable ou génère une exception
    res = d_vars.get(nom_variable)
    if res is None and raise_exception:
        raise Exception("variable '%s' non trouvée dans d_vars" % nom_variable)
    if res is True:
        res = 'oui'
    if res is False:
        res = 'non'
    return res

def get_champ_dict(nom_dict:str, nom_champ:str, raise_exception=True):
    # Cette fonction retourne la valeur du champ du dict ou génère une exception
    dict_temp = d_vars.get(nom_dict)
    if dict_temp is None:
        if raise_exception:
            raise Exception("dict '%s' non trouvée dans d_vars" % nom_dict)
        else:
            return None
    res = dict_temp.get(nom_champ)
    if res is None and raise_exception:
        raise Exception("champ '%s' non trouvé dans dict '%s'" % (nom_champ, nom_dict))
    return res

def get_index_liste(nom_liste:str, index:str, raise_exception=True):
    # Cette fonction retourne la valeur à l'index indiqué dans la liste ou génère une exception
    list_temp = d_vars.get(nom_liste)
    if list_temp is None:
        if raise_exception:
            raise Exception("liste '%s' non trouvée dans d_vars" % nom_liste)
        else:
            return None
    # La commande suivante génère une exception si index est invalide
    return list_temp[int(index)]

def fill(pattern:str, raise_exception=True):
    """
    Remplace les labels par leurs valeurs
    param: pattern: le modèle Latex contenant les labels à remplacer
    return: str
    """
    # 1) Cherche tous les flags
    l_flags = re.findall(r'@([VDL]_.*?)@', pattern)
    if not l_flags:
        # Pas de remplacement à faire
        return pattern
    # 2) Remplace tous les flags par leur valeur définie dans globals
    for flag in l_flags:
        nom_variable = flag[2:]
        if flag.startswith('V'):
            # C'est une variable simple
            res = get_variable(nom_variable, raise_exception)
            if res is None:
                continue
        elif flag.startswith('D'):
            # C'est un dictionnaire, donc nom_variable est du type "nom_dict|nom_champ"
            # La ligne suivante génère l'exception 'ValueError' si nom_variable est mal formaté
            nom_dict, nom_champ = nom_variable.split('#')
            res = get_champ_dict(nom_dict, nom_champ, raise_exception)
            if res is None:
                continue
        elif flag.startswith('L'):
            # C'est une liste, donc nom_variable est du type "nom_liste|index"
            # La ligne suivante génère l'exception 'ValueError' si nom_variable est mal formaté
            nom_liste, index = nom_variable.split('#')
            res = get_index_liste(nom_liste, index, raise_exception)
            if res is None:
                continue
        else:
            raise Exception("fonction fill: début de flag non traité: %s" % flag)
        # Remplace le flag par la valeur lue qui doit être convertie en string au préalable
        pattern = re.sub('@' + flag + '@', str(res), pattern)
    # 3) Supprime de pattern les variables qui n'ont pas été trouvées, en fonction du mode d'appel
    if not raise_exception:
        out = ""
        for ligne in pattern.splitlines():
            if not re.search(r'@([VDL]_.*?)@', ligne):
                out += ligne + os.linesep
        pattern = out
    return pattern

def generate_pdf(pdf_file:str, d_traitement, debug:bool=False):
    """
    param: pdf_file: le chemin vers le fichier PDF qui sera généré
    param: d_traitement: le dict globals() issu de traitement.by
    param: debug: True pour tester main avec un set de variables globales réduit et donc ne pas déclencher d'exception
            si variable non trouvée dans globals()
    return: status, msg avec:
            status: bool: True si exécution OK, False sinon
            msg: str: le message d'erreur si souci sinon le répertoire contenant les fichiers latex temporaires
    """
    def get_global_var(i: int, l_nom_var: list, variable_double: bool=False):
        for nom_var in l_nom_var:
            # Par définition 'variable' doit être trouvée, sinon génère une exception
            variable = d_vars.get(nom_var)
            if variable is None:
                if debug:
                    # Mode debug pour tester 'main' avec un jeu de variables réduit
                    continue
                raise Exception("fonction get_global_var: il manque le tableau '%s' dans d_vars" % nom_var)
            # Vérifie la longueur de variable, selon que c'est une variable simple ou double
            if variable_double and len(variable) != 2:
                raise Exception("fonction get_global_var: tableau double qui n'a pas une taille de 2: %s / %r" %
                                (nom_var, variable))
            elif not variable_double and len(variable) != NB_ELEVES_MAX:
                raise Exception("fonction get_global_var: tableau simple qui n'a pas une taille de %d: %s / %r" %
                                (NB_ELEVES_MAX, nom_var, variable))
            if variable_double:
                valeur = variable[0][i]
            else:
                valeur = variable[i]
            if not valeur:
                # Valeur non définie, donc on ne remplit pas le champ correspondant dans le dict
                continue
            if variable_double:
                eleve[nom_var + '_1'] = valeur
                # Pour une variable double, on ne tient pas compte de la 2ème valeur si elle est non définie, par
                # exemple le prix de location du second instrument
                if variable[1][i]:
                    eleve[nom_var + '_2'] = variable[1][i]
            else:
                eleve[nom_var] = valeur

    # 0) Adaptation de certaines variables globales
    global d_vars
    d_vars = d_traitement
    # Debug
    # for key in d_vars.keys():
    #     print(key, ':', d_vars[key])
    # print()

    all_contact = get_variable('contact')
    d_vars['contact_principal'] = all_contact[0]['nom']

    nb_eleves = int(get_variable('nb_inscrit'))

    # 1) Génération du fichier Latex
    path_rep_stockage = mkdtemp()
    fd_fic_latex = open(os.path.join(path_rep_stockage, 'inscription.tex'), mode='w')

    # a) En-tête et infos de contact
    tex_content = fill(TEMPLATE_ENTETE)
    for i in range(2):
        contact = all_contact[i]
        if not contact['nom']:
            break
        d_vars['contact'] = contact
        tex_content += fill(TEMPLATE_CONTACT)

    # b) Liste des élèves
    tex_content += fill(TEMPLATE_INSCRIPTIONS)
    l_champs_simples = ['nom', 'prenom', 'age', 'NiveauScolaire', 'CoursChant', 'PrixTotal', 'instrument1',
                        'location1', 'instrument2', 'location2', 'taille', 'remarqueDispo', 'nomProf', 'nomGroupe',
                        'jourpossible', 'jourimpossible', 'jourpeut_etre']
    l_champs_doubles = ['ParcoursCol', 'ParcoursComplet', 'Acc', 'orchestre', 'coursRock',
                        'prixInstrument']
    for i in range(NB_ELEVES_MAX):
        # Réinitialise le dictionnaire
        eleve = dict()
        # Récupère les variables globales pour remplir le dictionnaire de cet élève
        get_global_var(i, l_champs_simples)
        get_global_var(i, l_champs_doubles, True)
        if 'nom' not in eleve.keys():
            # On s'arrête au premier élève dont le nom est vide, en supposant qu'il n'y a pas d'autre élève défini après
            break
        # TODO: utiliser variable debug
        if True:
            print("\nEleve", eleve)
        d_vars['eleve'] = eleve
        # Pour les templates élève, on sait qu'il peut y avoir des variables manquantes
        tex_content += fill(TEMPLATE_ELEVE, raise_exception=False)

    # c) Tableau des coûts
    tex_content += fill(TEMPLATE_COUTS)
    l_prenoms = get_variable('prenom')
    l_prix_total = get_variable('PrixTotal')
    l_prix_loc_instrus = get_variable('prixInstrument')
    tex_content += "\\begin{tabular}{|l|c|c|c|}\n  \hline\n  \\textbf{Prénom} & \\textbf{Prix cours (€)} & \\textbf{Prix loc (€)} & \\textbf{Total (€)}\\\ \n"
    tex_content += "  \hline\n  \hline\n"
    total_cours = 0
    total_loc = 0
    for i in range(len(l_prenoms)):
        if not l_prenoms[i]:
            break
        prix_loc = l_prix_loc_instrus[0][i] + l_prix_loc_instrus[1][i]
        prix_total = l_prix_total[i]
        prix_cours = prix_total - prix_loc
        tex_content += "  %s & %d & %d & %d\\\ \n" % (l_prenoms[i], prix_cours, prix_loc, prix_total)
        total_cours += prix_cours
        total_loc += prix_loc
    tex_content += "  \hline\n  \\textbf{Sous-total} & %d & %d & %d\\\ \n" % (total_cours, total_loc, total_cours + total_loc)
    tex_content += "  \hline\n"
    tex_content += "  Cotisation & & & %d\\\ \n" % get_variable('cotisationFamille')
    reduction = int(get_variable('reductionFamille'))
    if reduction:
        tex_content += "  Réduction famille & & & -%d\\\ \n" % reduction
    val = total_cours + total_loc + get_variable('cotisationFamille') -reduction
    if total_loc:
        tex_content += ("  \hline\n  \\textit{< Total avec location >} & & & \\textit{%d}\\\ \n" % val)
    tex_content += ("  \hline\n  \\textbf{Total pour inscription} & & & %d\\\ \n" % (val - total_loc))
    tex_content += "  \hline\n\end{tabular}\n"

    # d) Type de règlement
    l_reglement = get_variable('typeReglement').split('+')
    if len(l_reglement) == 1:
        tex_content += "\\newline\\newline\\noindent\nType de règlement: %s\n" % l_reglement[0].rstrip().lstrip()
    else:
        tex_content += "\\newline\\newline\\noindent\nType de règlement:\n\\begin{itemize}\n"
        for val in l_reglement:
            text = val.rstrip().lstrip()
            if not text.endswith('.'):
                text += '.'
            tex_content += "\item[\\textbullet] %s \n" % text
        tex_content += "\end{itemize}\n"

    # e) Fin fichier
    tex_content += fill(TEMPLATE_FIN)

    # 2) Ecrit le fichier Latex
    fd_fic_latex.write(tex_content)
    fd_fic_latex.close()
    print("fichier Latex généré:", fd_fic_latex.name)

    # 3) Génération du fichier PDF par pdflatex
    # Appel pdflatex
    opt_output_dir = '-output-directory=' + path_rep_stockage
    res = subprocess.run(['pdflatex', '-interaction=nonstopmode', opt_output_dir, 'inscription.tex'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode:
        return False, res.stdout.decode('utf-8') + res.stderr.decode('utf-8')
    # Deplace le fichier résultat
    res = subprocess.run(['mv', os.path.join(path_rep_stockage, 'inscription.pdf'), pdf_file],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode:
        return False, res.stdout.decode('utf-8') + res.stderr.decode('utf-8')
    else:
        return True, path_rep_stockage


# MAIN pour test uniquement
###########################

if __name__ == '__main__':
    # Simulation de variables globales
    nom_famille = 'Simpsons'
    nb_eleves = 2
    nom = ["Simpsons", "Simpsons", "Simpsons", ""]
    prenom = ["Alice", "Bob", "Joe", ""]
    age = [10, 12, 14, 0]
    ParcoursCol = [["V1", "V2", "V3", ""], [0, 5, 10, 0]]
    contact = [{'nom': 'test parent', 'tel': '0205030202', 'mail': 'sy@titi.fr', 'ville': 'paris'},
               {'nom': 'pat bat', 'tel': '012345678', 'mail': 'test@oi.com', 'ville': 'acigné'}]

    # Test génération PDF
    fic_pdf = './inscription.pdf'
    status, msg = generate_pdf(fic_pdf, globals(), debug=True)
    if status:
        print("OK: fichier PDF: '%s' / répertoire fichiers Latex: '%s'" % (fic_pdf, msg))
    else:
        print("Erreur:", msg)
