from django import forms

class BacktestForm(forms.Form):
    STRATEGY_CHOICES = [
        ('contrarian', 'Contrarian Strategy'),
        ('momentum', 'Momentum Strategy'),
        ('mean_reversion', 'Mean Reversion Strategy'),
        ('sma', 'Stratégie des Moyennes Mobiles')
    ]

    INSTRUMENT_CHOICES = [
        # Paires de devises (Forex)
        ('EUR_USD', 'EUR/USD'), ('USD_JPY', 'USD/JPY'), ('GBP_USD', 'GBP/USD'),
        ('USD_CHF', 'USD/CHF'), ('USD_CAD', 'USD/CAD'), ('AUD_USD', 'AUD/USD'),
        ('NZD_USD', 'NZD/USD'), ('EUR_GBP', 'EUR/GBP'), ('EUR_JPY', 'EUR/JPY'),
        ('GBP_JPY', 'GBP/JPY'), ('CHF_JPY', 'CHF/JPY'), ('EUR_CHF', 'EUR/CHF'),
        ('EUR_CAD', 'EUR/CAD'), ('AUD_CAD', 'AUD/CAD'), ('CAD_JPY', 'CAD/JPY'),
        ('NZD_JPY', 'NZD/JPY'), ('GBP_CHF', 'GBP/CHF'), ('AUD_JPY', 'AUD/JPY'),
        ('EUR_AUD', 'EUR/AUD'), ('GBP_AUD', 'GBP/AUD'), ('AUD_NZD', 'AUD/NZD'),
        ('USD_MXN', 'USD/MXN'), ('USD_ZAR', 'USD/ZAR'), ('USD_HKD', 'USD/HKD'),
        ('USD_TRY', 'USD/TRY'), ('USD_NOK', 'USD/NOK'), ('USD_SEK', 'USD/SEK'),
        ('USD_DKK', 'USD/DKK'), ('USD_SGD', 'USD/SGD'),

        # Crypto-monnaies
        ('BTC_USD', 'BTC/USD'), ('ETH_USD', 'ETH/USD'), ('XRP_USD', 'XRP/USD'),
        ('BCH_USD', 'BCH/USD'), ('ADA_USD', 'ADA/USD'), ('DOGE_USD', 'DOGE/USD'),

        # Indices
        ('SPX500', 'S&P 500'), ('DJI30', 'Dow Jones 30'), ('NASDAQ', 'NASDAQ 100'),
        ('FTSE100', 'FTSE 100'), ('DAX30', 'DAX 30'), ('CAC40', 'CAC 40'),

        # Commodités
        ('XAU_USD', 'Gold/USD'), ('XAG_USD', 'Silver/USD'), ('WTI_USD', 'WTI Crude Oil/USD'),
        ('BRENT_USD', 'Brent Crude Oil/USD'),
    ]

    GRANULARITY_CHOICES = [
        ('S5', '5 seconds'), ('S10', '10 seconds'), ('S15', '15 seconds'), ('S30', '30 seconds'),
        ('M1', '1 minute'), ('M2', '2 minutes'), ('M4', '4 minutes'), ('M5', '5 minutes'),
        ('M10', '10 minutes'), ('M15', '15 minutes'), ('M30', '30 minutes'),
        ('H1', 'Hourly'), ('H2', '2 hours'), ('H3', '3 hours'), ('H4', '4 hours'),
        ('H6', '6 hours'), ('H8', '8 hours'), ('H12', '12 hours'),
        ('D', 'Daily'), ('W', 'Weekly'), ('M', 'Monthly')
    ]

    strategy = forms.ChoiceField(choices=STRATEGY_CHOICES)
    instrument = forms.ChoiceField(choices=INSTRUMENT_CHOICES, initial='EUR_USD')
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    granularity = forms.ChoiceField(choices=GRANULARITY_CHOICES)
    price = forms.ChoiceField(choices=[('M', 'Midpoint'), ('B', 'Bid'), ('A', 'Ask')])

    # Champs spécifiques aux stratégies
    window = forms.IntegerField(min_value=1, max_value=100, initial=5, required=False)
    lookback_period = forms.IntegerField(min_value=1, max_value=100, initial=14, required=False)
    Sma_S = forms.IntegerField(min_value=1, max_value=100, initial=14, required=False)
    Sma_L = forms.IntegerField(min_value=1, max_value=200, initial=50, required=False)
    SMA = forms.IntegerField(min_value=1, max_value=200, initial=50, required=False)
    dev = forms.FloatField(min_value=0.1, max_value=3.0, initial=2.0, required=False)
    threshold = forms.FloatField(min_value=0, max_value=1, initial=0.1, required=False)

    def clean(self):
        cleaned_data = super().clean()
        strategy = cleaned_data.get("strategy")

        if strategy == 'contrarian':
            if not cleaned_data.get("window"):
                raise forms.ValidationError("Window is required for Contrarian strategy.")
        elif strategy == 'momentum':
            if not cleaned_data.get("lookback_period"):
                raise forms.ValidationError("Lookback period is required for Momentum strategy.")
        elif strategy == 'mean_reversion':
            if not cleaned_data.get("SMA") or not cleaned_data.get("dev"):
                raise forms.ValidationError("SMA and dev are required for Mean Reversion strategy.")
        elif strategy == 'sma':
            if not cleaned_data.get("Sma_S") or not cleaned_data.get("Sma_L"):
                raise forms.ValidationError("Sma_S and Sma_L are required for SMA strategy.")

        return cleaned_data