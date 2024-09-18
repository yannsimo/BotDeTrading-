from .base import Backtest
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import pandas as pd
class SmaBacktester(Backtest):
    def __init__(self, conf_file, instrument, start, end, granularity, price, SMA_S, SMA_L,  tc=0.00007):
        super().__init__(conf_file, instrument, start, end, granularity, price)
        self.tc = tc
        self.SMA_S=SMA_S
        self.SMA_L=SMA_L


    def preprocess_data(self):
        if self.data is None:
            raise ValueError("Data not loaded. Call get_data() first.")

            # Filtrer les données pour l'instrument spécifique
        instrument_data = self.data[self.data['instrument'] == self.instrument]

        # Calculer les moyennes mobiles
        self.data["SMA_S"] = instrument_data['price'].rolling(self.SMA_S).mean()
        self.data["SMA_L"] = instrument_data['price'].rolling(self.SMA_L).mean()

        self.data.dropna(inplace=True)

       # print(f"Data after preprocessing: {self.data.head()}")  # Pour le débogage

    def test_strategy(self):
        self.preprocess_data()
        try:
            if self.data is None or self.data.empty:
                self.get_data()
                self.preprocess_data()

            data = self.data.copy()  # Create a copy to avoid modifying the original data

            data['position'] = np.where(data["SMA_S"] > data["SMA_L"], 1, -1)
            data['strategy'] = data['position'].shift(1) * data['returns']
            data.dropna(inplace=True)

            data['trades'] = data.position.diff().fillna(0).abs()
            data['strategy'] = data['strategy'] - data['trades'] * self.tc

            data['creturns'] = data['returns'].cumsum().apply(np.exp)
            data['cstrategy'] = data['strategy'].cumsum().apply(np.exp)

            self.results = data

            return self.calculate_performance()
        except Exception as e:
            print(f"Error in test_strategy: {str(e)}")
            raise
    def calculate_performance(self):
        if self.results is None or self.results.empty:
            raise ValueError("No results available. Strategy testing may have failed.")

        performance = self.results['cstrategy'].iloc[-1]
        outperformance = performance - self.results['creturns'].iloc[-1]
        return performance, outperformance

    def optimize_parameters(self, SMA_S_range, SMA_L_range):
        results = []
        for SMA_S in range(*SMA_S_range):
            for SMA_L in range(*SMA_L_range):
                if SMA_S < SMA_L:
                    self.SMA_S = SMA_S
                    self.SMA_L = SMA_L

                    performance, _ = self.test_strategy()
                    results.append((SMA_S, SMA_L, performance))
                    print(SMA_S, SMA_L, performance)
        results_df = pd.DataFrame(results, columns=['SMA_S', 'SMA_L', 'performance'])
        best_result = results_df.loc[results_df['performance'].idxmax()]

        self.SMA_S = int(best_result['SMA_S'])
        self.SMA_L = int(best_result['SMA_L'])
        self.results_overview = results_df
        self.test_strategy()
        return (self.SMA_S, self.SMA_L), best_result['performance']