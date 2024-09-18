from .oanda_provider import OandaDataProvider
   # Si vous avez d'autres fournisseurs

def get_data_provider(provider_name, **kwargs):
    if provider_name == 'oanda':
        return OandaDataProvider(**kwargs)
    else:
        raise ValueError(f"Unknown data provider: {provider_name}")