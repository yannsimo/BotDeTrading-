from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tpqoa
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class Backtest(tpqoa.tpqoa):
    def __init__(self,  conf_file, instrument, start, end, granularity, price):
        super().__init__(conf_file)
        self.instrument = instrument
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
        self.granularity = granularity
        self.price = price
        self.data = None
        self.results = None
        self.get_data()

    def get_data(self):
        try:
            df = self.get_history(instrument=self.instrument,
                                  start=self.start,
                                  end=self.end,
                                  granularity=self.granularity,
                                  price=self.price,
                                  localize=False).c.dropna().to_frame()
            df.rename(columns={"c": "price"}, inplace=True)
            df['instrument'] = self.instrument  # Ajoutez cette ligne
            df["returns"] = np.log(df.price / df.price.shift(1))
            self.data = df
            print(f"Données récupérées avec succès. Shape: {self.data.shape}")
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            raise ValueError("Aucune donnée n'a pu être récupérée. Vérifiez vos paramètres et votre connexion.")
    @abstractmethod
    def test_strategy(self):
        pass

    def plot_results(self):
        if self.results is None:
            raise ValueError("No results to plot. Run test_strategy() first.")

        plt.figure(figsize=(12, 8))
        plt.plot(self.results.index, self.results['creturns'], label='Buy and Hold')
        plt.plot(self.results.index, self.results['cstrategy'], label='Strategy')
        plt.title(f"{self.instrument} - Strategy Performance")
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns')
        plt.legend()

        # Save the plot to a BytesIO object
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode the image to base64
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic