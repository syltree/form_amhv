#!/usr/bin/python3

"""
Librairie pour l'envoie des mails 
Fonction à invoquer: envoieMail
"""

# IMPORTS
#########

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import re
import os

"""
pip install PyEmail 
"""


# envoie %Mail
def envoieMail(destinataire, nom_pdf, password, sender_user='amhv'):

    config = configparser.ConfigParser()
    # Extrait le nom de contact
    m = re.search(r'inscription_(.+)\.pdf', nom_pdf)
    nom_contact = m.groups(0)[0]
    _, filename_fin = os.path.split(nom_pdf)

    fournisseur = "orange.fr"
    smtp_server = "smtp." + fournisseur
    port = 587
    sender_email = sender_user + '@' + fournisseur
    receiver_email = destinataire  # Enter receiver address
    # Create a secure SSL context
    context = ssl.create_default_context()
    print("Envoie du mail a:" + receiver_email)

    # Try to log in to server and send email
    try:

        subject = "Inscription AMHV " + nom_contact
        body = """Bonjour,

Vous trouverez ci-joint le récapitulatif de votre pré-inscription à l'école de musique ainsi que le détail du montant à régler. Nous sommes désolés pour le mail généré hier soir qui avait un problème de pièce-jointe.

Le paiement doit parvenir à l'école au plus tard le 25 juin. Si vous avez la possibilité de passer pendant les horaires d'ouverture du secrétariat ou les permanences pour les inscriptions, cela permettra de valider que votre dossier est complet.

Vous trouverez tous les documents utiles (Prélèvement SEPA, fiches de voeux) ici : https://www.amhv.fr/inscriptions/

IMPORTANT:
- Si vous avez opté pour la pratique instrumentale en cours collectif vous devez impérativement passer à l'école de musique pour choisir le créneau horaire et ainsi vous garantir une place.
- Pour la chorale à l'école, nous attendons les confirmations individuelles des 4 mairies pour valider cette activité.

Bien cordialement,

L'équipe AMHV"""

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        cc_mail = "contact@amhv.fr"
        message["Cc"] = cc_mail
        #message["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        filename = nom_pdf  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            "attachment; filename= " + filename_fin,
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, [receiver_email, cc_mail], text)
            server.quit()

        return True, "Mail envoyé"

    except Exception as e:
        # Print any error messages to stdout
        print("Erreur: ")
        print(e)
        return False, "Erreur"


# Fin envoieMail


if __name__ == '__main__':
    # Simulation de variables globales
    if len(sys.argv) != 4:
        print("## Erreur ## usage %s @mail_dest fic_PDF sender_user" % sys.argv[0])

    destinataire = sys.argv[1]
    fic = sys.argv[2]
    sender = sys.argv[3]
    password = input("pwd pour %s ? " % sender)

    # Test envoi PDF
    res, mess = envoieMail(destinataire, fic, password, sender_user=sender)
    if res:
        print(mess)
    else:
        print("## Erreur ##", mess)

