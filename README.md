# odj_ce2contrats
Extraction des contrats à partir de l'ordre du jour du Conseil exécutif de la Ville de Montréal.

# Objectif
Rendre disponible l'information sur les contrats devant être adoptés au Conseil exécutif.

En ce moment, cette information se retrouve dans le site «Vue sur les contrats» seulement après l'adoption.

Les citoyens devraient être en mesure de connaître les contrats avant la rencontre.

# Variables
    no_decision             Numéro de la décision dans le procès-verbal
    pour                    L'entité pour qui le contrat est voté
    no_dossier              Numéro de dossier en lien avec le contrat
    instance_reference      L'instance de qui vient la demande du contrat 
    no_appel_offre          Numéro de l'appel d'offres, si applicable 
    debut_no_appel_offre    Position du début du numéro de l'appel d'offres
    fin_no_appel_offre      Position de la fin du numéro de l'appel d'offres
    depense_totale          Montant total de la dépense du contrat (peut ou pas inclure les taxes)
    texte_contrat           Texte de la décision relative au cpontrat 
    source                  Lien vers le fichier source PDF sur le site de la Ville de Montréal
