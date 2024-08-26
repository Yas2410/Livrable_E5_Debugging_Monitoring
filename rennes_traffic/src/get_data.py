import pandas as pd
import requests


class GetData(object):

    def __init__(self, url) -> None:
        self.url = url

        response = requests.get(self.url)
        self.data = response.json()

    def processing_one_point(self, data_dict: dict):
        # Création du DataFrame temporaire à partir du dictionnaire "data_dict"
        temp = pd.DataFrame(
            {
                key: [data_dict[key]]
                for key in [
                    'datetime',
                    # 'traffic_status', N'existe pas dans le json ("voir json_analysis.py")  # noqa
                    'geo_point_2d',
                    'averagevehiclespeed',
                    'traveltime',
                    'trafficstatus'
                ]
            }
    )  # noqa

        # De même ici, on renomme "traffic_status" sans underscore en "traffic"
        temp = temp.rename(columns={'trafficstatus': 'traffic'})

        # Ici, on va également avoir une KeyError si on laisse "lattitude" et "longitude"  # noqa
        # On remplace donc comme dans le fichier json, par "lat" et "lon"
        temp['lat'] = temp.geo_point_2d.map(lambda x: x['lat'])
        temp['lon'] = temp.geo_point_2d.map(lambda x: x['lon'])

        # Suppression de la colonne "geo_point_2d"
        del temp['geo_point_2d']

        return temp

    def __call__(self):

        res_df = pd.DataFrame({})

        for data_dict in self.data:

            temp_df = self.processing_one_point(data_dict)
            res_df = pd.concat([res_df, temp_df], ignore_index=True)

            res_df = res_df[res_df.traffic != 'unknown']

            return res_df
