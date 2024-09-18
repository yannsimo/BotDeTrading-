from datetime import timedelta

import numpy as np
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments


class OandaDataProvider:
    def __init__(self, access_token, account_id):
        self.api = API(access_token=access_token, environment="practice")
        self.account_id = account_id

    def get_historical_data(self, instrument, start, end, granularity, price):
        print("je suis aussi vide pareil!")
        try:
            print("C'est bizarre 1 ")
            params = {
                "from": pd.to_datetime(start).isoformat(),
                "to": pd.to_datetime(end).isoformat(),
                "granularity": granularity,
                "price": price
            }
            print("C'est bizarre 2 ")
            r = instruments.InstrumentsCandles(instrument=instrument, params=params)
            self.api.request(r)
            print("je suis aussi vide pareil!")
            data = []
            for candle in r.response['candles']:
                if candle['complete']:
                    data.append({
                        'time': pd.to_datetime(candle['time']),
                        'price': float(candle[price]['c'])
                    })

            df = pd.DataFrame(data)
            if df.empty:
                raise ValueError("Aucune donnée n'a été récupérée.")

            df.set_index('time', inplace=True)
            df["returns"] = np.log(df.price / df.price.shift(1))

            print(f"Données récupérées avec succès. Shape: {df.shape}")
            return df
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            raise ValueError("Aucune donnée n'a pu être récupérée. Vérifiez vos paramètres et votre connexion.")

