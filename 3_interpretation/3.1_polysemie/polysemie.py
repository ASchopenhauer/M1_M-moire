import unicodedata
import regex as re
import os
from collections import Counter
import shutil





# 1) Dictionnaire contenant l'ensemble des noms communs des diverses listes de vocabulaire thématique


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





# 2) Dictionnaire des oeuvres n°1 (avant l'exclusion des termes polysémiques)
		
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
    dico_oeuvres[work]=d_theme





# 3) Dictionnaire des mots polysémiques

def find_polysemous_words(dict_themes, dict_works):
    result = {}
    
    # Create a reverse lookup dictionary for words to themes
    word_to_themes = {}
    for theme, words in dict_themes.items():
        for word in words:
            if word not in word_to_themes:
                word_to_themes[word] = []
            word_to_themes[word].append(theme)
    
    # Iterate over each work in dict_works
    for work, themes in dict_works.items():
        work_result = {}
        
        # Iterate over each theme in the current work
        for theme, words in themes.items():
            
            # Iterate over each word in the current theme
            for word in words:
                if word in word_to_themes:
                    # Get all themes for the word excluding the current theme
                    all_themes = word_to_themes[word]
                    if len(all_themes) > 1 or theme not in all_themes:
                        work_result[word] = all_themes
        
        if work_result:
            result[work] = work_result
    
    return result

dico_polysemie = find_polysemous_words(dico_themes, dico_oeuvres)





# 4) Générer le LaTeX des mots polysémiques, en ordre alphabétique

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

    
out = "/latex/mots_polysemiques_alphabetique.txt"
write_polysemous_words_to_latex(dico_polysemie,out)





# 5) Création d'un nouveau dossier contenant uniquement les paragraphes où les termes prélevés ne sont pas polysémiques.

input_p = "/data/p_theme"
output_p = "/data/p_theme_nonpoly"

for oeuvre in list(dico_polysemie.keys()):
    l_mots_poly = list(dico_polysemie['GMS'].keys())
    path_oeuvre = os.path.join(input_p,oeuvre)
    for theme in os.listdir(path_oeuvre):
        path_theme = os.path.join(path_oeuvre,theme)
        for mot in os.listdir(path_theme):
            if mot not in l_mots_poly:
                output_mot = os.path.join(output_p,oeuvre,theme,mot)
                os.makedirs(output_mot, exist_ok=True)
                for txt in os.listdir(os.path.join(path_theme,mot)):
                    path_txt = os.path.join(path_theme,mot,txt)
                    shutil.copy(path_txt,output_mot)





# 6) Génération des nouveaux documents LaTeX dédiés à la lecture proche

from bs4 import BeautifulSoup

input_xml = "/data/xml"
dico_xml = {'GMS':"/tg173/tg173.item.xml",'KpV':"/tg196/tg196.item.xml",'MS':"/tg427/tg427.item.xml"}

input_p = "/data/p_theme_nonpoly"
output_tex = "/latex/lecture_proche"

def get_chemin(oeuvre):
    return input_xml + dico_xml[oeuvre]

def oeuvre_xml(chemin_xml):
    with open(chemin_xml) as fp:
        soup = BeautifulSoup(fp, 'xml')
    return soup

def plus_proche_n (p):
    for parent in p.parents:
        if parent.name == 'div' and parent.has_attr('n'):
            return parent['n']

avant_path = "/latex/lecture_proche/Avant.txt"
apres_path = "/latex/lecture_proche/Apres.txt"
avant = open(avant_path, mode='r', encoding='utf-8').read()
apres = open(apres_path, mode='r', encoding='utf-8').read()


for oeuvre in os.listdir(input_p):
    soup = oeuvre_xml(get_chemin(oeuvre))
    texte_tex = ""
    for theme in os.listdir(os.path.join(input_p,oeuvre)):
        texte_tex += r"\unnumberedchapter{" + re.sub('_','',theme) + "} \n"   # Pour nettoyer les '_'
        for mot in os.listdir(os.path.join(input_p,oeuvre,theme)):
            liste = os.listdir(os.path.join(input_p,oeuvre,theme,mot))
            nb_p = len(liste)
            texte_tex +=  r"\unnumberedsection{" + mot + f" ({nb_p})" + "} \n"
            for p in liste:
                id = p[:-4]
                def cherche_id(tag): 
                    return tag.name == 'p' and tag['xml:id'] == id
                f = soup.body.find(cherche_id) # Jusque là ok ! (vérifié avec prints)
                n = plus_proche_n(f)
                texte_tex +=  "\subsection*{" + id + "} \n"
                texte_tex += r"\textbf{Source : }" + n[28:] + r"\\ " + ' \n\n'
                t = open(os.path.join(input_p,oeuvre,theme,mot,p), mode='r', encoding='utf-8').read()
                texte_tex += r"\textbf{Paragraphe : }" + t + ' \n\n'
    
    output_tex_oeuvre = os.path.join(output_tex,oeuvre,f'{oeuvre}_lecture_proche.txt')    
    open(output_tex_oeuvre,'w').write(avant + texte_tex + apres) # et penser à bien modifier le titre !!! 


    

    
# 7) Second dictionnaire des oeuvres après exclusion du vocabulaire polysémiques

input = "/data/p_theme"

new_dico_oeuvres = {}

for work in os.listdir(input):
    d_theme = {}
    liste_poly = list(dico_polysemie['GMS'].keys())
    for theme in os.listdir(os.path.join(input,work)):
        d_mot = {}
        for mot in os.listdir(os.path.join(input,work,theme)):
            if mot not in liste_poly :
                n = len(os.listdir(os.path.join(input,work,theme,mot)))
                d_mot[mot]=n
        d_theme[theme]=Counter(d_mot)
    new_dico_oeuvres[work]=d_theme
    




# 8) Génération de la nouvelle vue d'ensemble en LaTeX

themes = ['Agriculture', 'Alimentation', 'Botanique', 'Monde', 'Sciences_exactes', 'Vetement', 'Zoologie']

from tabulate import tabulate

def total_terms_in_theme(work, theme): # fonction adaptée puisque maintenant certains thèmes sont vides...
    if data[work][theme] == [] :
        return 0
    else :
        return sum(data.get(work, {}).get(theme, Counter()).values())

def compare_theme_vocabulary(theme): 
    comparison = {}
    for work in data:
        comparison[work] = total_terms_in_theme(work, theme)
    return comparison

table_data = []
for theme in themes:
    row = [re.sub('_',' ', theme)] + list(compare_theme_vocabulary(theme).values())
    table_data.append(row)

# Calculate totals for each work
totals = [sum(total_terms_in_theme(work, theme) for theme in themes) for work in data]
total_row = ['Total'] + totals
# Append the total row to the table data
table_data.append(total_row)
# Define the headers
headers = ['Theme'] + list(data.keys())
# Generate LaTeX table
latex_table = tabulate(table_data, headers, tablefmt="latex")

with open("/latex/comparaison_theme_work_V2.txt"), "w") as f:
    f.write(latex_table)
    
    



# 9) Générer des tableaux LaTeX par thème, pour comparer l'occurrence de mots précis dans chaque oeuvre.

output = "/latex/table_theme"

# ChatGPT  

def compare_terms_across_works(term, theme):
    return {work: data.get(work, {}).get(theme, Counter()).get(term, 0) for work in data}

def get_unique_terms(theme):
    terms = set()
    for work in data:
        terms.update(data.get(work, {}).get(theme, Counter()).keys())
    return terms

def generate_latex_table_for_theme(theme):
    unique_terms = get_unique_terms(theme)
    
    table_data = []
    for term in unique_terms:
        row = [term] + list(compare_terms_across_works(term, theme).values())
        table_data.append(row)

    headers = ['Terme'] + list(data.keys())
    
    # Create the LaTeX table
    latex_table_body = tabulate(table_data, headers, tablefmt="latex")
    
    # Add title and wrap the table in a table environment
    latex_table = f"""
\\begin{{table}}[ht]
\\centering
\\caption{{Tableau des termes pour le thème {theme}}}
\\label{{tab:{theme}}}
{latex_table_body}
\\end{{table}}
    """
    
    return latex_table

# List of themes
themes = ['Agriculture', 'Alimentation', 'Botanique', 'Monde', 'Sciences_exactes', 'Vetement', 'Zoologie']

# Generate and save LaTeX tables for each theme
for theme in themes:
    latex_table = generate_latex_table_for_theme(theme)
    print(f"Table for theme: {theme}")
    print(latex_table)
    
    with open(os.path.join(output,f"{theme}_vocabulary_table.tex"), "w") as f:
        f.write(latex_table)