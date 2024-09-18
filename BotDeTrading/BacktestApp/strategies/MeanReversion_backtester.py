from .base import Backtest
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import pandas as pd
class MeanRBacktester(Backtest):
    def __init__(self, conf_file, instrument, start, end, granularity, price, SMA, dev, tc=0.00007):
        super().__init__(conf_file, instrument, start, end, granularity, price)
        self.tc = tc
        self.SMA = SMA
        self.dev = dev
        self.get_data()

    def preprocess_data(self):
        if self.data is None:
            raise ValueError("Data not loaded. Call get_data() first.")

        # Filtrer les données pour l'instrument spécifique
        instrument_data = self.data[self.data['instrument'] == self.instrument]

        # Calculer la SMA et les bandes
        self.data["SMA"] = instrument_data['price'].rolling(self.SMA).mean()
        std = instrument_data['price'].rolling(self.SMA).std()
        self.data["Lower"] = self.data["SMA"] - std * self.dev
        self.data["Upper"] = self.data["SMA"] + std * self.dev

        self.data.dropna(inplace=True)

      # print(f"Data after preprocessing: {self.data.head()}")  # Pour le débogage


    def test_strategy(self):
        try:

            self.preprocess_data()
            if self.data is None or self.data.empty:
                self.get_data()
                self.preprocess_data()

            data = self.data[self.data['instrument'] == self.instrument].copy()

            data["distance"] = data.price - data.SMA
            data["position"] = np.where(data.price < data.Lower, 1, np.nan)
            data["position"] = np.where(data.price > data.Upper, -1, data["position"])
            data["position"] = np.where(data.distance * data.distance.shift(1) < 0, 0, data["position"])
            data["position"] = data.position.ffill().fillna(0)
            data["strategy"] = data.position.shift(1) * data["returns"]
            data.dropna(inplace=True)

            data["trades"] = data.position.diff().fillna(0).abs()
            data["strategy"] = data.strategy - data.trades * self.tc

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

    def optimize_parameters(self, SMA_range, dev_range):
        combinations = list(product(range(*SMA_range), range(*dev_range)))
        results = []
        for comb in combinations:
            self.SMA=comb[0]
            self.dev=comb[1]
            performance, outperformance = self.test_strategy()
            results.append((self.SMA, self.dev, performance))
            print(self.SMA, self.dev, performance)

        results_df = pd.DataFrame(results, columns=['SMA', 'dev', 'performance'])
        best_result = results_df.loc[results_df['performance'].idxmax()]

        self.SMA = int(best_result['SMA'])
        self.dev = int(best_result['dev'])
        self.results_overview = results_df
        self.test_strategy()
        return (self.SMA, self.dev), best_result['performance']

