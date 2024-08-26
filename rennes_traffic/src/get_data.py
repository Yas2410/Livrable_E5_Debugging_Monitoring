import pandas as pd
import requests


class GetData(object):

    def __init__(self, url) -> None:
        self.url = url

        response = requests.get(self.url)
        self.data = response.json()

    def processing_one_point(self, data_dict: dict):
        # Création du DataFrame temporaire à partir du dictionnaire "data_dict"
        temp = pd.DataFrame({
        # Avec suppression de "traffic_status" bug sur l'affichage de la légende # noqa
        # On va donc garder cette clé mais ajouter la condition None à la fonction  # noqa
        # qui va servir de valeur par défaut si la clé est inexistante, sans renvoyer d'erreurs # noqa
            key: [data_dict.get(key, None)] for key in ['datetime',
                                                        'traffic_status',
                                                        'geo_point_2d',
                                                        'averagevehiclespeed',
                                                        'traveltime', 'trafficstatus']  # noqa
        })

        temp = temp.rename(columns={'traffic_status': 'traffic'})

        # Ici, on va également avoir une KeyError si on laisse "lattitude" et "longitude"  # noqa
        # On remplace donc comme dans le fichier json, par "lat" et "lon"
        if 'geo_point_2d' in temp.columns and temp['geo_point_2d'].notna().any():
            temp['lat'] = temp.geo_point_2d.map(lambda x: x.get('lat', None) if isinstance(x, dict) else None)  # noqa
            temp['lon'] = temp.geo_point_2d.map(lambda x: x.get('lon', None) if isinstance(x, dict) else None)  # noqa
        else:
            temp['lat'] = None
            temp['lon'] = None

        del temp['geo_point_2d']

        return temp

    def call(self):

        res_df = pd.DataFrame({})

        for data_dict in self.data:
            temp_df = self.processing_one_point(data_dict)
            res_df = pd.concat([res_df, temp_df], ignore_index=True)

        res_df = res_df[res_df.traffic != 'unknown']

        return res_df
