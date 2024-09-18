from io import BytesIO
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base import Backtest
class ConBacktester(Backtest):
    def __init__(self, conf_file, instrument, start, end, granularity, price, window,  tc=0.00007):
        super().__init__(conf_file, instrument, start, end, granularity, price)
        self.tc = tc
        self.window=window
        self.preprocess_data()

    def preprocess_data(self):
        if self.data is None:
            raise ValueError("Data not loaded. Call get_data() first.")

        self.data['returns'] = np.log(self.data['price'] / self.data['price'].shift(1))
        self.data.dropna(inplace=True)

    def test_strategy(self):
        try:
            if self.data is None or self.data.empty:
                raise ValueError("Data is None or empty after preprocessing.")

            data = self.data.copy()  # Create a copy to avoid modifying the original data

            data['position'] = -np.sign(data['returns'].rolling(self.window).mean())
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

    def optimize_parameter(self, window_range):
        ''' Finds the optimal strategy (global maximum) given the window parameter range. '''
        windows = range(*window_range)
        results = []
        for window in windows:
            self.window = window  # Mettre à jour la fenêtre

            performance, _ = self.test_strategy()  # Appeler test_strategy sans argument
            results.append(performance)

        best_perf = np.max(results)  # best performance
        opt = windows[np.argmax(results)]  # optimal parameter

        # create a df with many results
        self.results_overview = pd.DataFrame(data={"window": windows, "performance": results})

        # Réinitialiser à la meilleure fenêtre trouvée
        self.window = opt
        self.get_data()
        self.test_strategy()

        return opt, best_perf

    def plot_optimization_results(self):
        if self.results_overview is None:
            raise ValueError("No optimization results available. Run optimize_parameter() first.")

        plt.figure(figsize=(10, 6))
        plt.plot(self.results_overview['window'], self.results_overview['performance'])
        plt.title('Performance vs Window Size')
        plt.xlabel('Window Size')
        plt.ylabel('Performance')
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return graphic