# Dictionnaire contenant l'ensemble des noms communs des diverses listes de vocabulaire thématique

import unicodedata
import regex as re
import os

input_base = "/data/voc_themes_choisis"
input_autre = "/data/voc_themes_autres"

dico_themes = {}

for input in [input_base,input_autre]:
    for file in os.listdir(input):
        theme = file[:-4]
        path_file = os.path.join(input,file)
        voc = open(path_file, mode='r', encoding='utf-8').read()
        voc = re.split("\n",voc)
        voc = [line[4:] for line in voc]
        dico_themes[theme]=voc

# Dictionnaire des oeuvres
		
from collections import Counter

input = "/data/p_theme"

dico_oeuvres = {}

for work in os.listdir(input):
    d_theme = {}
    for theme in os.listdir(os.path.join(input,work)):
        d_mot = {}
        for mot in os.listdir(os.path.join(input,work,theme)):
            n = len(os.listdir(os.path.join(input,work,theme,mot)))
            d_mot[mot]=n
        d_theme[theme]=Counter(d_mot)
    dico_oeuvres[work]=dico_theme
    

# Dictionnaire des oeuvres n°2

input = "/data/p_theme"

dico_oeuvres = {}

for work in os.listdir(input):
    d_theme = {}
    for theme in os.listdir(os.path.join(input,work)):
        d_mot = {}
        for mot in os.listdir(os.path.join(input,work,theme)):
            n = len(os.listdir(os.path.join(input,work,theme,mot)))
            d_mot[mot]=n
        d_theme[theme]=Counter(d_mot)
    dico_oeuvres[work]=d_theme

# Dictionnaire des mots polysémiques


# Générer le LaTeX des mots polysémiques, en ordre alphabétique

# ChatGPT
def write_polysemous_words_to_latex(polysemous_words, filename):
    with open(filename, "w") as f:
        for work, words in polysemous_words.items():
            f.write(f"\\section*{{Polysemous words in {work}}}\n")
            f.write("\\begin{itemize}\n")
            
            # Sort the words alphabetically
            sorted_words = sorted(words.items())
            
            for word, themes in sorted_words:
                themes_str = re.sub('_',' ',', '.join(themes))
                f.write(f"  \\item \\textbf{{{word}}}: {themes_str}\n")
            
            f.write("\\end{itemize}\n")

    
out = /latex/mots_polysemiques_alphabetique.txt"
write_polysemous_words_to_latex(dico_polysemie,out)


    
    
# rajout oeuvre