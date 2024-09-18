from django.shortcuts import render
from django.http import HttpResponse
from BacktestApp.strategies.con_backtester import ConBacktester
from BacktestApp.strategies.Mom_backtester import MomBacktester
from BacktestApp.strategies.Sma_backtester import SmaBacktester
from BacktestApp.strategies.MeanReversion_backtester import MeanRBacktester
from .forms import BacktestForm
import logging

logger = logging.getLogger(__name__)

def backtest_view(request):
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            try:
                strategy = form.cleaned_data['strategy']
                common_params = {
                    'conf_file': "oanda.cfg",
                    'instrument': form.cleaned_data['instrument'],
                    'start': form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
                    'end': form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
                    'granularity': form.cleaned_data['granularity'],
                    'price': form.cleaned_data['price']
                }

                action = request.POST.get('action')

                if strategy == 'contrarian':
                    window = form.cleaned_data['window']
                    backtester = ConBacktester(**common_params, window=window)
                elif strategy == 'momentum':
                    lookback_period = form.cleaned_data['lookback_period']
                    backtester = MomBacktester(**common_params, lookback_period=lookback_period)
                elif strategy == 'sma':
                    Sma_S = form.cleaned_data['Sma_S']
                    Sma_L = form.cleaned_data['Sma_L']
                    backtester = SmaBacktester(**common_params, SMA_S=Sma_S, SMA_L=Sma_L)
                elif strategy == 'mean_reversion':
                    SMA = form.cleaned_data['SMA']
                    dev = form.cleaned_data['dev']
                    backtester = MeanRBacktester(**common_params, SMA=SMA, dev=dev)

                logger.info(f"Backtester créé pour la stratégie: {strategy}")

                if action == "optimize":
                    optimization_plot = None
                    if strategy == 'contrarian':
                        opt_params, best_perf = backtester.optimize_parameter((1, 50, 1))
                        optimization_plot = backtester.plot_results()
                    elif strategy == 'momentum':
                        opt_params, best_perf = backtester.optimize_parameter((5, 100, 5))
                        optimization_plot = backtester.plot_results()
                    elif strategy == 'sma':
                        opt_params, best_perf = backtester.optimize_parameters((5, 100, 5), (20, 200, 10))
                        optimization_plot = backtester.plot_results()
                    elif strategy == 'mean_reversion':
                        opt_params, best_perf = backtester.optimize_parameters((10, 200, 10), (1, 6, 1))
                        optimization_plot = backtester.plot_results()

                    return render(request, 'backtester/optimization_results.html', {
                        'strategy': strategy,
                        'optimal_params': opt_params,
                        'best_performance': best_perf,
                        'optimization_plot': optimization_plot,
                    })
                else:
                    # Exécution de la stratégie
                    performance, outperformance = backtester.test_strategy()
                    logger.info(f"Performance: {performance}, Outperformance: {outperformance}")

                    # Génération du graphique
                    plot_image = backtester.plot_results()

                    # Rendu des résultats dans un template
                    return render(request, 'backtester/results.html', {
                        'strategy': strategy,
                        'performance': performance,
                        'outperformance': outperformance,
                        'plot_image': plot_image,
                    })

            except Exception as e:
                logger.error(f"Erreur lors du backtesting: {str(e)}", exc_info=True)
                return HttpResponse(f"Erreur lors du backtesting: {str(e)}")
    else:
        form = BacktestForm()

    return render(request, 'backtester/backtest_form.html', {'form': form})