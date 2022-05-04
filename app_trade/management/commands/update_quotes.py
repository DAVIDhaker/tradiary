import requests
from django.conf import settings
from django.core.management import BaseCommand
from app_trade.models import Pair


class Command(BaseCommand):
    def execute(self, *args, **options):
        for pair in Pair.objects.all():
            print(f'{pair} fetching... ', end='')

            quote_data = requests.get(
                'https://pro-api.coinmarketcap.com/v1/tools/price-conversion',
                headers={
                    'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_TOKEN
                },
                params={
                    'amount': 1,
                    'symbol': pair.second_asset,
                    'convert': pair.base_asset
                }
            ).json()

            pair.current_quote = quote_data['data']['quote'][pair.base_asset.market_symbol]['price']
            pair.save()

            print(f'{pair.current_quote=}')
