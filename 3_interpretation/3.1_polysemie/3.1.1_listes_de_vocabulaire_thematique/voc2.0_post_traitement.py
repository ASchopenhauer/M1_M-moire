# Nettoyage des listes de vocabulaire thématique

import regex as re
import os

articles = ["der","die","das"]


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

def parentheses(liste):
    reg1 = r"\p{Ll}\(\p{Ll}+\)\p{Ll}" # ex : das Grum(me)t
    reg2 = r"\p{Ll}\(\p{Ll}+\)" # ex : der Springwurm(wickler)
    reg3 = r"\(\p{Lu}\p{Ll}+\)\p{Ll}" # ex : der (Futter)trog
    newliste = []
    reg_par = r'\(|\)'
    reg_chunk = r'\((\p{Ll}|\p{Lu})+\)'
    reg_chunk_elargi = r' \(.+\)'
    for line in liste :
        match1 = re.search(reg1,line)
        match2 = re.search(reg2,line)
        if match1 or match2:            
            newline1 = re.sub(reg_par,'',line) 
            newline2 = re.sub(reg_chunk,'',line)
            newliste.append(newline1)
            newliste.append(newline2)           
        elif re.search(reg3,line):
            newline1 = re.sub(reg_par,'',line)
            newline2 = re.sub(reg_chunk,'',line)
            newline2 = newline2[:4] + newline2[4].upper() + newline2[5:]
            newliste.append(newline1)
            newliste.append(newline2)
        else :
            newline1 = re.sub(reg_chunk_elargi,'',line)
            newliste.append(newline1)
    return newliste

def slash(liste):
    reg1 = r"/(der|die|das)" # deux genres possibles, ex : "der/das", puis das Abbeeren/das Entrappen, der Holzschliff/der Holzstoff
    reg2 = r"-/" # ex : der Hau-/Hackklotz, die Zier-/Profilleiste
    reg3 = r"\p{Ll}/\p{Lu}" # ex : das Weiderecht/Triftrecht, der Wabenhonig/Scheibenhonig
    newliste = []
    for line in liste :
        if re.match(reg1, line[3:]):
            newline = line[:3] + line[7:]
            newliste.append(newline)
        elif re.search(reg1,line):
            split = re.split('/',line,maxsplit=1)
            newline1 = split[0]
            newline2 = split[1]
            newliste.append(newline1)
            newliste.append(newline2)
        elif re.search(reg2,line):
            pass # parce que c'est trop compliqué pour l'instant...
        elif re.search(reg3,line):
            split = re.split('/',line,maxsplit=1)
            newline1 = split[0]
            newline2 = line[:4] + split[1]
            newliste.append(newline1)
            newliste.append(newline2)
        else :
            newline = re.sub('/','',line)
            newliste.append(newline)
    return newliste

def point_virgule(liste):
    newliste = []
    for line in liste :
        if re.search('; ',line):
            split = re.split(r' *; ',line,maxsplit=1)
            newline1 = split[0]
            newliste.append(newline1)
            if split[1][0:3] in articles:
                newline2 = split[1]
                newliste.append(newline2)
        else :
            newline = re.sub(r' *;','',line)
            newliste.append(newline)
    return newliste

def reste(liste):
    reg1 = r"\p{Ll}-"
    newliste = []
    for line in liste:
        spaces = re.finditer(' ',line)
        longueur = len(list(spaces))
        if re.match(reg1,line[-2:]):
            pass
        elif '(' in line and ')' not in line:
            pass
        elif ')' in line and '(' not in line:
            pass
        elif re.match(r'\p{Ll}',line[4:]):
            pass
        elif longueur == 2 :
            split = re.split(' ',line)
            newline = split[0] + ' ' + split[1]
            newliste.append(newline)
        elif longueur > 2 :
            pass
        else:
            newliste.append(line)
    return newliste


def path_output(input):
    tail = os.path.split(input)[1]
    return os.path.join(output_dir,tail)

def pipeline_voc(chemin):
    voc = open(chemin, mode='r', encoding='utf-8').read()
    voc = re.split("\n", voc)
    voc = [ligne for ligne in voc if ligne != ''] # On retire les lignes vides
    voc = [ligne for ligne in voc if ligne[0:3] in articles] # Lignes qui commencent par un article
    voc = [enleve_marque_pluriel(ligne) for ligne in voc] # On retire la marque pluriel
    voc = parentheses(voc)
    voc = slash(voc)
    voc = point_virgule(voc)
    voc = reste(voc)
    chemin_output = path_output(chemin)
    with open(chemin_output, 'w') as output:
        for row in voc:
            output.write(str(row) + '\n')
            

input_dir = "/output/voc_apres_OCR"
output_dir = "/output/voc_apres_regex"

for vocab in os.listdir(input_dir) :
    chemin_vocab = os.path.join(input_dir,vocab)
    pipeline_voc(chemin_vocab)