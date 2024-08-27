import requests # type: ignore


#Compréhension du contenu du fichier JSON
json_url = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"

response = requests.get(json_url)

response.raise_for_status()

# Chargement du json
data = response.json()

# Affichage des premières lignes pour comprendre la structure de ce dernier
print("Premiers éléments de la structure JSON:")
print(data[:2])

# Quelles sont les clés disponibles?
if data:
    first_item = data[0]
    print("Clés disponibles dans le premier élément:")
    print(first_item.keys())
