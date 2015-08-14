"""Extraire les contrats de l'ordre du jour du Comité exécutif
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


#Fonction strip_bom
#Pour enlever \ufeff
def strip_bom(fileName):
    with open(fileName, encoding="utf-8", mode="r") as f:
        text = f.read()
    text = text.replace("\ufeff","")
    with open(fileName, encoding="utf-8", mode="w") as f:
        f.write(text)

        
#Fonction epurer_ligne
def epurer_ligne(texte):

    reponse = str(texte).strip("[]")            #Épuration du texte extrait de l'ordre du jour
    reponse = mid(reponse,1,len(reponse)-2)     #Enlever les guillements au début et à la fin
    reponse = reponse.replace("  "," ")         #Pour une raison inconnu, il y a plusieurs 2 espaces consécutifs dans l'ordre du jour
    reponse = reponse.replace(" , ",", ")       #Pour une raison inconnu, il y a plusieurs virgules précédées d'un espace
    reponse = reponse.replace(";"," ")          #Enlever les ; pour éviter des problème avec le CSV qui sera généré     
    reponse = reponse.replace(u"\u2018", "'")
    reponse = reponse.replace(u"\u2019", "'")
   
    # response = (mid(reponse,1,len(reponse)-2).replace(" "," ").replace(" , ",", ").replace(";"," ").replace(u"\u2018", "'").replace(u"\u2019", "'"))   
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
#Le numéro est toujours précédé de "offres public no " ou "offres public " et suivi par le nombre de soumissionaires entre parenthèses
#A FAIRE: il arrive que des caractères non significatifs se retrouvent à la fin du numéro. Voir à bonifier la fonction pour les enlever. (voir Issue #8))
def getNo_appel_offres(texte):

    no_appel_offre = ""
    
    if texte:
 
        if "offres public no " in texte:
            debut_no_appel_offre = texte.find("offres public no") + 15
            fin_no_appel_offre = texte.find(" (", debut_no_appel_offre)
            no_appel_offre = mid(texte, debut_no_appel_offre + 1, fin_no_appel_offre - debut_no_appel_offre)
            no_appel_offre = no_appel_offre.strip() 

        elif "offres public " in texte:
            debut_no_appel_offre = texte.find("offres public ") + 13
            fin_no_appel_offre = texte.find(" (", debut_no_appel_offre)
            no_appel_offre = mid(texte, debut_no_appel_offre + 1, fin_no_appel_offre - debut_no_appel_offre)
            no_appel_offre = no_appel_offre.strip()
            
    return no_appel_offre
        

#Fonction getNbr_soumissions
#Le nombre de soumissions se trouve toujours après "offres public ", entre parenthèses
#texte: correspondant au texte complet de la décision
def getNbr_soumissions(texte):

    nbr_soumissions = ""
    
    # if len(texte) > 0:
        # if texte.find("offres public ") != -1:
            # debut_no_appel_offre = texte.find("offres public ") + 13
            # debut_nbr_soumission = texte.find(" (", debut_no_appel_offre)
            # if debut_nbr_soumission > -1:
                # fin_nbr_soumission = texte.find(" soum", debut_nbr_soumission)
            
            # nbr_soumissions = mid(texte, debut_nbr_soumission + 2, fin_nbr_soumission - debut_nbr_soumission - 2)
            # nbr_soumissions = nbr_soumissions.strip()
 
    if texte:

        if texte.find(" soumissionnaires)") > -1:

            debut_soumissionaires = texte.find(" soumissionnaires)")
            
            nbr_soumissions = mid(texte, debut_soumissionaires - 1,  1)
            
            nbr_soumissions = nbr_soumissions.strip()
            print(nbr_soumissions)

            if not nbr_soumissions.isnumeric():         #Si le résultat n'est pas un nombre, on vide nbr_soumissions
               nbr_soumissions = ""
         
    return nbr_soumissions
   
        
#Fonction getDepense_totale !!!DOIT ETRE RETRAVAILLÉ!!!
#Si le terme «Dépense total» est présent, extraire le montant.
#Ceci ne couvre pas tous les cas, mais est une première étape.
#Voir si un REGEX serait plus efficace.
def getDepense_totale(texte):

    depense_total = ""
    
    # if texte:
        
        # depense_total = 1

        # if "somme" in texte:
            # depense_total = 2
            # debut_depense_total = texte.find("somme") + 7
            #fin_depense_total = texte.find(" /$", debut_depense_total)
            # depense_total = mid(texte, debut_depense_total + 1, 10)
            #depense_total = depense_total.strip()
            # depense_total = depense_total.replace(" ", "")
     
       
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
    
    #if True:
    if False:
        print(texte)
         

#Début du traitement 

def main():
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
    strip_bom(FICHIER_ORDRE_DU_JOUR)

    #Ouverture du fichier pour les résultats
    contrats_traites = open('contrats_traites.csv', "w", encoding="utf-8")      
    fcontrats_traites = csv.writer(contrats_traites, delimiter = ';') 
    fcontrats_traites.writerow(["instance", "date_rencontre", "no_decision", "no_dossier", "instance_reference", "no_appel_offres", "nbr_soumissions", "pour", "texte_contrat", "source", "date_traitement"])

    #Passer au travers de l'ordre du jour
    with open(FICHIER_ORDRE_DU_JOUR, "r", encoding = "utf-8", ) as f:
        reader = csv.reader(f, delimiter = "|")

        for ligne in reader:

            if ligne:                                                       #Ne pas traiter les lignes vides
            
                ligne2 = epurer_ligne(ligne)
                
                print(ligne2)                                               #Affichage à l'écran pour faciliter le suivi et le débuggage
                
                if not est_numero_de_page(ligne2):                          #Ne pas traite les lignes qui donnes le numéro de page du PDF                                      
                    
                    #Début d'une décision
                    if ligne2.startswith(PREFIXE_DECISION):                 #Voir à utiliser un regex à la place???
                        
                        #Écrire le dernier contrat dans le fichier contrats_traites.txt
                        if no_decision:                                     #Dans le traitement, sur la première décision, il n'y a encore rien à écrire

                            no_appel_offre = getNo_appel_offres(texte_contrat)
                            nbr_soumissions = getNbr_soumissions(texte_contrat)
                            depense_totale = getDepense_totale(texte_contrat)
                            
                            #Écrire le nom des chgamps dans le fichier contrats_traites.csv
                            fcontrats_traites.writerow([INSTANCE, DATE_RENCONTRE, no_decision, no_dossier, instance_reference, no_appel_offre, nbr_soumissions, pour, texte_contrat, source, DATE_TRAITEMENT])
                            

                        #no_decision = ligne2                               #Nouveau numéro de décision
                        no_decision = left(ligne2, 6)                       #Nouveau numéro de décision
                        test_Debug("2.1")
                        pour = ""                                           #Initaliser le pour
                        no_dossier = ""                                     #Initaliser le numéro de dossier
                        instance_reference = ""                             #Initialiser l'instance référente du contrat
                        no_appel_offre = ""                                 #Initaliser le numéro d'appel d'offre
                        debut_no_appel_offre = ""
                        fin_no_appel_offre = ""
                        depense_totale = ""
                        texte_contrat = ""                                  #Initaliser le texte du contrat
                    
                    if not ligne2.startswith(PREFIXE_DECISION):

                        if ligne2:
                            
                            #L'instance référence du contrat
                            if est_instance_reference(ligne2):
                                instance_reference = set_instance_reference(ligne2)
                            
                            #Texte du contrat
                            if no_dossier:                                  #Ne pas mettre le 'pour' dans le texte du contrat
                                if not texte_contrat:
                                    texte_contrat = ligne2.strip()          #C'est le début du texte du contrat, évite d'avoir un espace au début
                                else:    
                                    texte_contrat = texte_contrat + " " + ligne2.strip()
                    
                            #La variable 'pour' est l'entité pour qui le contrat est adopté
                            if not no_dossier and not est_instance_reference(ligne2):                              
                                pour = pour + ligne2
                            
                            #Numéro de décision
                            if len(ligne2) > 9:                             

                                if right(ligne2,10).isnumeric():            #Voir à utiliser un regex à la place

                                    no_dossier = right(ligne2,10)
                                    pour = left(pour,len(pour)-12).strip()          #Enlever le numéro de dossier qui se trouvait à la fin de la variable pour
                                    
    #Écrire le dernier contrat
    no_appel_offre = getNo_appel_offres(texte_contrat)
    nbr_soumissions = getNbr_soumissions(texte_contrat)
    depense_totale = getDepense_totale(texte_contrat)
    fcontrats_traites.writerow([INSTANCE, DATE_RENCONTRE, no_decision, no_dossier, instance_reference, no_appel_offre, nbr_soumissions, pour, texte_contrat, source, DATE_TRAITEMENT])     

    #Fermer les fichiers            
    contrats_traites.close()

    #Indiquer que le traitement est terminé
    print()
    print('-'*60)
    print("Traitement terminé.")
    print('-'*60)

if __name__ == '__main__':
    main()

