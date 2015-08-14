""" test Extraire les contrats de l'ordre du jour du Comité exécutif
Version 2.0, 2015-08-13
Développé en Python 3.4
Licence CC-BY-NC 4.0 Pascal Robichaud, pascal.robichaud.do101@gmail.com

Mettre les fichiers requis pour le traitement dans C:\contrats

Fichier PDF de l'ordre du jour (12 août 2015): 
http://ville.montreal.qc.ca/sel/adi-public/afficherpdf/fichier.pdf?typeDoc=odj&doc=7203

Convertir le PDF en TXT avec pdf2txt, en Python 2.7
Extraire que les pages sur les contrats seulement
python pdf2txt.py -p 6,7,8,9,10,11,12,13,14,15 -o odj.txt -c utf-8 odj.pdf
À faire éventuellement: faire en sorte que le script détecte les fichiers PDF 
dans un sous-répertoire et fasse le traitement automatiquement.

Voir à détecter s'il s'agit d'un ordre du jour du Conseil municipal, Comité exécutif, etc.
Par exemple, via le nom du fichier: CE_ODJ_LP_ORDI_2015-08-12_08h30_FR.pdf
"""

__version__ = "$2.0$"                                   #Veuillez m'indioquez si c'est la bonne façon de faire ;-)
# $Source$

import datetime
import csv                                              #Pour sauvegarder les résultats dans le fichier verification.csv

INSTANCE = "Comité exécutif"
#INSTANCE = "Conseil municipal"
FICHIER_ORDRE_DU_JOUR = "C:\\contrats\\odj.txt"         #Emplacement du fichier du l'ordre du jour
DATE_RENCONTRE = "2015-08-12"                           #À changer
PREFIXE_DECISION = "20."                                #À changer au besoin
DATE_TRAITEMENT = datetime.datetime.today()             #Date à laquelle l'extraction des contrats a été faite
                                                        #Arranger le format AAAA-MM-JJ


#Fonction strip_BOM
def strip_BOM(fileName):

    with open(fileName, encoding='utf-8', mode='r') as f:
        reading = []
        for line in f:
                line=line.replace('\ufeff',"")
                reading.append(line)
                for rest in f:
                        reading.append(rest)
    with open(fileName, encoding='utf-8', mode='w') as f:
        for line in reading:
                f.write(line)

        
#Fonction epurer_ligne
def epurer_ligne(texte):

    reponse = str(texte).strip('[]')            #Épuration du texte extrait de l'ordre du jour
    reponse = mid(reponse,1,len(reponse)-2)     #Enlever les guillements au début et à la fin
    reponse = reponse.replace("  "," ")         #Pour une raison inconnu, il y a plusieurs 2 espaces consécutifs dans l'ordre du jour
    reponse = reponse.replace(" , ",", ")       #Pour une raison inconnu, il y a plusieurs virgules précédées d'un espace
    reponse = reponse.replace(";"," ")          #Enlever les ; pour éviter des problème avec le CSV qui sera généré     
    reponse = reponse.replace(u"\u2018", "'")
    reponse = reponse.replace(u"\u2019", "'")
    
    return reponse

#Fonction est_numero_de_page    
#Vérifie si la ligne est un numéro de page du PDF de l'ordre du jour
def est_numero_de_page(texte):

    reponse = False

    if texte.startswith("Page "):
        reponse = True
     
    return reponse

#Fonction est_instance_reference
#Vérifie si la ligne indique l'instance qui a référé le contrat
def est_instance_reference(texte):
    
    reponse = False
                                #A OPTIMISER!!!
    if "CE" in texte:           #Comité exécutif
        reponse = True
    elif "CG" in texte:         #Conseil d'agglomération
        reponse = True
    elif "CM" in texte:         #Conseil municipal
        reponse = True
        
    return reponse
  
#Fonction set_instance_reference
#Retourne l'instance qui a référé le contrat
def set_instance_reference(texte):
    
    reponse = ""
                                #A OPTIMISER!!!
    if "CE" in texte:           #Comité exécutif
        reponse = "Comité exécutif"
    elif "CG" in texte:         #Conseil d'agglomération
        reponse = "Conseil d'agglomération"
    elif "CM" in texte:         #Conseil municipal
        reponse = "Conseil municipal"
        
    return reponse

  
#Fonction getNo_appel_offres
#Le numéro est toujours précédé de "offres public " et suivi par le nombre de soumissionaires entre parenthèses
def getNo_appel_offres(texte):

    no_appel_offre = ""
    
    if texte:
        if "offres public " in texte:
            debut_no_appel_offre = texte.find("offres public ") + 13
            fin_no_appel_offre = texte.find(" (", debut_no_appel_offre)
            no_appel_offre = mid(texte, debut_no_appel_offre + 1, fin_no_appel_offre - debut_no_appel_offre)
            no_appel_offre = no_appel_offre.strip()
            
    return no_appel_offre
        

#Fonction getNbr_soumissions
#Le nombre de soumissions se trouve toujours après "offres public ", entre parenthèses
def getNbr_soumissions(texte):

    nbr_soumissions = ""

    if texte:
        if "offres public " in texte:
            debut_no_appel_offre = texte.find("offres public ") + 13
            debut_nbr_soumission = texte.find(" (", debut_no_appel_offre)
            if debut_nbr_soumission > -1:
                fin_nbr_soumission = texte.find(" soum", debut_nbr_soumission)
            
            #A faire: il arrive que le nombre de soumission est au début de la ligne
            nbr_soumissions = mid(texte, debut_nbr_soumission + 2, fin_nbr_soumission - debut_nbr_soumission - 2)
            nbr_soumissions = nbr_soumissions.strip()
            
    return nbr_soumissions
   
        
#Fonction getDepense_totale !!!DOIT ETRE RETRAVAILLÉ!!!
#Si le terme «Dépense total» est présent, extraire le montant.
#Ceci ne couvre pas tous les cas, mais est une première étape.
#Voir si un REGEX serait plus efficace.
def getDepense_totale(texte):

        depense_total = ""
        
        if texte:
            
            depense_total = 1

            if "somme" in texte:
                depense_total = 2
                debut_depense_total = texte.find("somme") + 7
                #fin_depense_total = texte.find(" /$", debut_depense_total)
                depense_total = mid(texte, debut_depense_total + 1, 10)
                #depense_total = depense_total.strip()
                depense_total = depense_total.replace(" ", "")
        
        print(depense_total)        
        return depense_total

        
#Fonction left
def left(s, amount = 1, substring = ""):

    if (substring == ""):
        return s[:amount]
    else:
        if (len(substring) > amount):
            substring = substring[:amount]
        return substring + s[:-amount]
         
 
#Fonction mid
def mid(s, offset, amount):

    return s[offset:offset+amount]

         
        
#Fonction right
def right(s, amount = 1, substring = ""):

    if (substring == ""):
        return s[-amount:]
    else:
        if (len(substring) > amount):
            substring = substring[:amount]
        return s[:-amount] + substring    
         
        
#Fonction test_Debug
def test_Debug(texte):
    
    if True:
    #if False:
        print(texte)
         

#Début du traitement 

#Initialisation des variables
no_decision = ""
pour = ""
no_dossier = ""
instance_reference = ""
no_appel_offre = ""
debut_no_appel_offre = ""
fin_no_appel_offre = ""
depense_totale = ""
texte_contrat = ""
source = "http://ville.montreal.qc.ca/sel/adi-public/afficherpdf/fichier.pdf?typeDoc=odj&doc=7203"

#Enlever le BOM au début du fichier
strip_BOM(FICHIER_ORDRE_DU_JOUR)

#Ouverture du fichier pour les résultats
contrats_traites = open('contrats_traites.csv', "w", encoding="utf-8")      
fcontrats_traites = csv.writer(contrats_traites, delimiter = ';') 
fcontrats_traites.writerow(["INSTANCE", "DATE_RENCONTRE", "no_decision", "no_dossier", "instance_reference", "no_appel_offres", "nbr_soumissions", "depense_total", "pour", "texte_contrat", "source", "date_traitement"])

#Passer au travers de l'ordre du jour
with open(FICHIER_ORDRE_DU_JOUR, 'r', encoding = 'utf-8', ) as f:
    reader = csv.reader(f, delimiter = '|')

    for ligne in reader:

        if ligne:                                               #Ne pas traiter les lignes vides
            ligne2 = epurer_ligne(ligne)
            test_Debug("1")
            
            if not est_numero_de_page(ligne2):                  #Ne pas traite les lignes qui donnes le numéro de page du PDF
            
                print(ligne2)                                       #Affichage à l'écran pour faciliter le suivi et le débuggage
                
                #Début d'une décision
                if ligne2.startswith(PREFIXE_DECISION):             #Voir à utiliser un regex à la place???
                    test_Debug("2")
                    
                    #Écrire le dernier contrat dans le fichier contrats_traites.txt
                    if no_decision != "":                           #Dans le traitement, sur la première décision, il n'y a encore rien à écrire
                        no_appel_offre = getNo_appel_offres(texte_contrat)
                        nbr_soumissions = getNbr_soumissions(texte_contrat)
                        #depense_totale = getDepense_totale(texte_contrat)
                        fcontrats_traites.writerow([INSTANCE, DATE_RENCONTRE, no_decision, no_dossier, instance_reference, no_appel_offre, nbr_soumissions, pour, texte_contrat, source, DATE_TRAITEMENT])
                    
                    #no_decision = ligne2                           #Nouveau numéro de décision
                    no_decision = left(ligne2, 6)                   #Nouveau numéro de décision
                    test_Debug("2.1")
                    pour = ""                                       #Initaliser le pouyr
                    no_dossier = ""                                 #Initaliser le numéro de dossier
                    instance_reference = ""                         #Initialiser l'instance référente du contrat
                    no_appel_offre = ""                             #Initaliser le numéro d'appel d'offre
                    debut_no_appel_offre = ""
                    fin_no_appel_offre = ""
                    #depense_totale = ""
                    texte_contrat = ""                              #Initaliser le texte du contrat
                
                if not ligne2.startswith(PREFIXE_DECISION):
                    test_Debug("3")
                    if ligne2:
                        test_Debug("4")
                        
                        if est_instance_reference(ligne2):
                            instance_reference = set_instance_reference(ligne2)
                        
                        if no_dossier:                              #Ne pas mettre le 'pour' dans le texte du contrat
                            if not texte_contrat:
                                texte_contrat = ligne2.strip()      #C'estlde début du texte du contrat, évite d'avoir un espace au début
                            else:    
                                texte_contrat = texte_contrat + " " + ligne2.strip()
                
                        if not no_dossier:                          #La variable 'pour' est l'entité pour qui le contrat est adopté
                            pour = pour + ligne2.strip()
                
                        if len(ligne2) > 9:                         #Numéro de décision
                            test_Debug("5")
                            if right(ligne2,10).isnumeric():        #Voir à utiliser un regex à la place
                                test_Debug("6")
                                no_dossier = right(ligne2,10)
                                pour = left(pour,len(pour)-14)
                        
#Écrire le dernier contrat
test_Debug("7")
no_appel_offre = getNo_appel_offres(texte_contrat)
nbr_soumissions = getNbr_soumissions(texte_contrat)
#depense_totale = getDepense_totale(texte_contrat)
fcontrats_traites.writerow([INSTANCE, DATE_RENCONTRE, no_decision, no_dossier, instance_reference, no_appel_offre, nbr_soumissions, pour, texte_contrat, source, DATE_TRAITEMENT])     

#Fermer les fichiers            
contrats_traites.close()

#Indiquer que le traitement est terminé
print()
print('-'*60)
print("Traitement terminé.")
print('-'*60)



