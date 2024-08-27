from flask import Flask, render_template, request
import plotly.io as pio

# Ajout du module Flask monitoring Dashboard
import flask_monitoringdashboard as dashboard


# Ajout du module logging pour déboggage du code
import logging

from keras.models import load_model  # type: ignore

from src.get_data import GetData
from src.utils import create_figure, prediction_from_model

app = Flask(__name__)

# Configuration du module Logging
app.logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Si utilisation d'un fichier de config pour se connecter au dashboard
dashboard.config.init_from(file='/config.cfg')

try:
    data_retriever = GetData(url="https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/exports/json?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B")
    # Ajout de la méthode call, sinon renvoi d'erreur : "TypeError: 'GetData' object is not callable"  # noqa
    data = data_retriever.call()
    app.logger.debug("Données récupérées avec succès.")
except Exception as e:
    app.logger.warning(f"Un problème est survenu lors de la récupération des données : {e}")

# Ajout d"un try/except au cas où le modèle ne chargerait pas
try:
    app.logger.info('Essai du chargement du modèle...')
    model = load_model('model.h5')
    app.logger.info('Le modèle a été chargé avec succès')
except Exception as e:
    app.logger.error(f"Erreur lors du chargement du modèle : {e}")
    model = None


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        try:
            fig_map = create_figure(data)
            graph_json = pio.to_json(fig_map)

            # BUG : Ajouter .get ET passer
            # "selected_hour" à "cat_predict" sinon erreur
            selected_hour = request.form.get('hour')

            cat_predict = prediction_from_model(model, selected_hour)

            color_pred_map = {0: ["Prédiction : Libre", "green"],
                            1: ["Prédiction : Dense", "orange"],
                            2: ["Prédiction : Bloqué", "red"]}

            # BUG : Le fichier html ne se nomme pas "home" mais "index"
            # Ajouter aussi selected_hour
            app.logger.debug(f"Prédiction effectuée pour l'heure sélectionnée : {selected_hour}")
            return render_template('index.html',
                                graph_json=graph_json,
                                text_pred=color_pred_map[cat_predict][0],
                                color_pred=color_pred_map[cat_predict][1],
                                selected_hour=selected_hour)
        except Exception as e:

            app.logger.error(f"Erreur pendant le traitement d'une requête POST : {e}")
            return f"Une erreur est survenue : {str(e)}", 500
    
    else:
        try:
            fig_map = create_figure(data)
            graph_json = pio.to_json(fig_map)
            # BUG : Le fichier html ne se nomme pas "home" mais "index"
            return render_template('index.html', graph_json=graph_json)
        except Exception as e:
            app.logger.error(f"Erreur pendant le traitement de la requête GET : {e}")
            return f"Une erreur est survenue : {str(e)}", 500

# Ajout des paramètres pour la configuration du dashboard
dashboard.config.enable_logging = True
# dashboard.config.init_from(file='/config.cfg')
# Flask monitoring dashboard : Liaison du tableau de bord à l'application Flask
dashboard.bind(app)
dashboard.config.monitor_level = 3

if __name__ == '__main__':
    app.run(debug=True)


@app.before_request
def before_request_logging():
    app.logger.debug(f"Détails de la requête - Méthode : {request.method}, Chemin : {request.path}")

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Exception non gérée: {e}", exc_info=True)
    return render_template("error.html"), 500
