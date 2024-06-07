import numpy as np
import pandas as pd
import os
import regex as re
import unicodedata

input_correct = "/correct"
input_pascorrect = "/correct_encours"

big_df = pd.DataFrame()

for name in os.listdir(input_correct):
    path_csv = os.path.join(input_correct,name)
    df = pd.read_csv(path_csv, sep="\t", encoding="utf-8") 

    is_aligned = [True for i in range(len(df))]
    theme = name[:-14]
    page = name[-12:-10]
    rectangle = name[-9:-8] 

    df["Aligned"] = np.array(is_aligned)
    df["Thème"] = np.array([theme for i in range(len(df))])
    df["Page"] = np.array([page for i in range(len(df))])
    df["Rectangle"] = np.array([rectangle for i in range(len(df))])    

    big_df = pd.concat([big_df,df])

for name in os.listdir(input_pascorrect):
    path_csv = os.path.join(input_pascorrect,name)
    df = pd.read_csv(path_csv, sep="\t",encoding="utf-8") 

    is_aligned = [False for i in range(len(df))]
    theme = name[:-14]
    page = name[-12:-10]
    rectangle = name[-9:-8] 

    df["Aligned"] = np.array(is_aligned)
    df["Thème"] = np.array([theme for i in range(len(df))])
    df["Page"] = np.array([page for i in range(len(df))])
    df["Rectangle"] = np.array([rectangle for i in range(len(df))])    

    big_df = pd.concat([big_df,df])

output = "/output/big_csv/sauvegarde_intermédiaire.csv"

big_df.to_csv(output, sep='\t',encoding="utf-8")





# 2) Nettoyage du csv 

copy = big_df
copy = copy.drop(columns=['deu_is_noun','fra_is_noun'])
copy = copy.drop(columns=[copy.columns.tolist()[0]])





# 3) On reproduit la démarche 1.4 du mémoire de post-traitement du vocabulaire grâce aux expressions régulières.
# Ainsi, il sera possible de retrouver le terme exactement tel qu'il apparaît dans nos listes.
# Il a fallu adapter quelque peu les fonction à notre nouveau format !

# On travaille sur des listes car cela est plus simple. On les réintègrera ensuite dans le csv.
liste_noms = list(copy['German_voc'])
liste_noms = [str(nom) for nom in liste_noms]

# On sélectionne les cellules dont le texte commence bien par un déterminant.
liste_bool = [(len(nom)>3 and (nom[0:3] in articles)) for nom in liste_noms]

new_liste=[]
for i,nom in enumerate(liste_noms):
    if liste_bool[i]:
        new_liste.append(nom)
    else :
        new_liste.append("")
        
# On reprend la pipeline développée en l'adaptant

# Traitement simple sans changement
def enleve_marque_pluriel(ligne):
    
    # Traitement des cas où la marque est séparée par une virgule
    if "," in ligne :
        newline = ""
        indice = 0
        while ligne[indice]!=",":
            newline += ligne[indice]
            indice+=1 
        return newline
    else :
        return ligne

new_liste = [enleve_marque_pluriel(ligne) for ligne in new_liste] # On retire la marque pluriel

# Traitement des parenthèses à adapter : On ne crée pas de nouveau éléments dans la liste, mais un élément peut contenir un saut de ligne '\n' si il y a plusieurs alternatives pour un seul mot.

def parenthese(line): # au niveau de la ligne et non plus au niveau de la liste entière
    reg1 = r"\p{Ll}\(\p{Ll}+\)\p{Ll}" # ex : das Grum(me)t
    reg2 = r"\p{Ll}\(\p{Ll}+\)" # ex : der Springwurm(wickler)
    reg3 = r"\(\p{Lu}\p{Ll}+\)\p{Ll}" # ex : der (Futter)trog
    reg_par = r'\(|\)'
    reg_chunk = r'\((\p{Ll}|\p{Lu})+\)'
    reg_chunk_elargi = r' \(.+\)'
    match1 = re.search(reg1,line)
    match2 = re.search(reg2,line)
    if match1 or match2:
        newline = re.sub(reg_par,'',line) +'\n'+ re.sub(reg_chunk,'',line)
    elif re.search(reg3,line):
        temp = re.sub(reg_chunk,'',line)
        newline = re.sub(reg_par,'',line) +'\n'+ temp[:4] + temp[4].upper() + temp[5:]
    else :
        newline = re.sub(reg_chunk_elargi,'',line)
    return line
    
new_liste = [parenthese(ligne) for ligne in new_liste]

# De même pour les slashs. Par ailleurs il convient de distinguer les cas qui entraînent non pas une modification de l'écriture d'un terme au sein de la future liste de vocabulaire thématique, mais la supression de ce potentiel terme, car jugé comme inadéquat. Lors de telles suppressions, il faut alors aussi changer les valeurs de la liste de bouléens.

def slash(line):
    reg1 = r"/(der|die|das)" # deux genres possibles, ex : "der/das", puis das Abbeeren/das Entrappen, der Holzschliff/der Holzstoff
    reg2 = r"-/" # ex : der Hau-/Hackklotz, die Zier-/Profilleiste
    reg3 = r"\p{Ll}/\p{Lu}" # ex : das Weiderecht/Triftrecht, der Wabenhonig/Scheibenhonig
    if re.match(reg1, line[3:]):
        newline = line[:3] + line[7:]
    elif re.search(reg1,line):
        split = re.split('/',line,maxsplit=1)
        newline = split[0]+'\n'+split[1]
    elif re.search(reg3,line):
        split = re.split('/',line,maxsplit=1)
        newline = split[0]+'\n'+line[:4] + split[1]
    else :
        newline = line
    return newline
    
new_liste = [slash(ligne) for ligne in new_liste]

def slash_complement():
    reg2 = r"-/" # ex : der Hau-/Hackklotz, die Zier-/Profilleiste
    for i, line in enumerate(new_liste):
        if re.search(reg2,line):
            new_liste[i] = ""
            liste_bool[i]=False
        else:
            new_liste[i] = re.sub('/','',line)

slash_complement()

# point-virgule

def point_virgule(line):
    if re.search('; ',line):
        split = re.split(r' *; ',line,maxsplit=1)
        newline = split[0]
        if split[1][0:3] in articles:
            newline+= '\n' + split[1]
    else:
        newline = re.sub(r' *;','',line)
    return newline
    
new_liste = [point_virgule(ligne) for ligne in new_liste]

# reste : modification de la liste des bouléens.

def reste_modif():
    reg1 = r"\p{Ll}-"
    for i,line in enumerate(new_liste):
        spaces = re.finditer(' ',line)
        longueur = len(list(spaces))
        if re.match(reg1,line[-2:]):
            new_liste[i] = ""
            liste_bool[i]=False
        elif '(' in line and ')' not in line:
            new_liste[i] = ""
            liste_bool[i]=False
        elif ')' in line and '(' not in line:
            new_liste[i] = ""
            liste_bool[i]=False
        elif re.match(r'\p{Ll}',line[4:]):
            new_liste[i] = ""
            liste_bool[i]=False
        elif longueur == 2 :
            split = re.split(' ',line)
            new_liste[i] = split[0] + ' ' + split[1]
        elif longueur > 2 :
            new_liste[i] = ""
            liste_bool[i]=False

reste_modif()





# 4) On réintègre ces deux nouvelles colonnes

copy['German_Noun']=np.array(new_liste)
copy['is_taken']=np.array(liste_bool)





# 5) Améliorations diverses apportées au csv, et sauvegardes petit à petit

# Ajout d'une autre colonne contenant les noms communs sans leurs articles
nom_sans_article = [nom[4:] for nom in new_liste]
copy['Nom_recherché']=nom_sans_article

output_csv = "/output/big_csv/big_df.csv"
copy.to_csv(output_csv, sep='\t',encoding="utf-8")



# Ajout d'une colonne avec un identifiant afin de relier le mot tel qu'il apparaît dans les listes de vocabulaire thématique à la chaîne de caractères non nettoyée produite lors de l'OCR.
identifiant = [str("{:04d}".format(i)) for i in range(len(copy))]
copy['identifiant']=identifiant

output_csv = "/output/big_csv/big_df_identifiants.csv"
copy.to_csv(output_csv, sep='\t',encoding="utf-8")



# Ajout du numéro des vraies pages dans le livre (afin de pouvoir y rechercher directement, en dernier reccours). Cela est complémentaire aux numéros de pages relatifs
dico_TOC = {"Monde":104,"Sciences_exactes":117, "Zoologie_Botanique":133,"Alimentation":294,"Agriculture":310,"Vetement":319}

page_livre = []
temp_themes = list(copy['Thème'])

for i, page in enumerate(copy["Page"]):
    page=int(page)
    th = temp_themes[i]
    p_th = dico_TOC[th]
    vrai_page = p_th + page
    page_livre.append(vrai_page)
    
copy['Page_livre']=np.array(page_livre)

output_csv = "/output/big_csv/big_df_identifiants_pageslivre.csv"
copy.to_csv(output_csv, sep='\t',encoding="utf-8")

