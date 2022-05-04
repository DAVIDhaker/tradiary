from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import render
from django.db import models

from app_invest.models import Investition


admin.site.site_header = \
admin.site.site_title  = \
admin.site.index_title = 'Tradiary'


class Fake(models.Model):
    class Meta:
        verbose_name = 'Average price'
        verbose_name_plural = verbose_name
        managed = False


@admin.register(Fake)
class APIDocsLinkView(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        return [
            url('', self.render, name='app_invest_fake_changelist')
        ]

    def render(self, request):
        data = {}
        processing_investitions = Investition.objects.filter(sell_trade__isnull=True)

        totals = {
            'spend_base_asset': {},
            'spend_base_asset_per_token': {},
            'calculated_grow_in_base_asset': {},
            'inputs': len(processing_investitions),
        }

        for investition in processing_investitions:
            pair_name = str(investition.buy_trade.pair)

            buy = {
                'amount': investition.buy_trade.amount,
                'price': investition.buy_trade.price
            }

            if pair_name in data:
                data[pair_name]['buys'].append(buy)
            else:
                data[pair_name] = {
                    'base_asset': investition.buy_trade.pair.base_asset,
                    'second_asset': investition.buy_trade.pair.second_asset,
                    'buys': [buy],
                    'pair': investition.buy_trade.pair
                }

        pairs = data.keys()

        for pair in pairs:
            min_price = None
            max_price = None
            base_asset_amount = 0
            second_asset_amount = 0
            base_asset_name = str(data[pair]['pair'].base_asset)
            second_asset_name = str(data[pair]['pair'].second_asset)


            for buy in data[pair]['buys']:
                if max_price is None or buy['price'] > max_price:
                    max_price = buy['price']

                if min_price is None or buy['price'] < min_price:
                    min_price = buy['price']

                base_asset_amount += buy['price'] * buy['amount']
                second_asset_amount += buy['amount']

            data[pair].update({
                'min_price': float(min_price),
                'max_price': float(max_price),
                'invest_asset_amount': float(second_asset_amount),
                'base_asset_spend_total': float(base_asset_amount),
                'active_inputs': len(data[pair]['buys']),
                'average_price': float(base_asset_amount / second_asset_amount),
                'calculated_grow': None,
            })

            if base_asset_name in totals['spend_base_asset']:
                totals['spend_base_asset'][base_asset_name] += data[pair]['base_asset_spend_total']
            else:
                totals['spend_base_asset'][base_asset_name] = data[pair]['base_asset_spend_total']

            if base_asset_name not in totals['spend_base_asset_per_token']:
                totals['spend_base_asset_per_token'][base_asset_name] = {}

            totals['spend_base_asset_per_token'][base_asset_name][second_asset_name] = float(base_asset_amount)

            if data[pair]['pair'].current_quote:
                grow_percentage = (
                    data[pair]['invest_asset_amount'] * float(data[pair]['pair'].current_quote)
                    / data[pair]['base_asset_spend_total']
                    - 1
                ) * 100

                grow_amount = \
                    data[pair]['invest_asset_amount'] * float(data[pair]['pair'].current_quote) \
                    - data[pair]['base_asset_spend_total']

                data[pair]['calculated_grow'] = \
                    f'{float(grow_percentage):+.2f}% / {float(grow_amount):+} {data[pair]["pair"].base_asset}'

                if base_asset_name in totals['calculated_grow_in_base_asset']:
                    totals['calculated_grow_in_base_asset'][base_asset_name] += grow_amount
                else:
                    totals['calculated_grow_in_base_asset'][base_asset_name] = grow_amount

        base_asset_distribution = {}

        # for base_asset in totals['spend_base_asset_per_token']:
        #     totals[base_asset]

        for pair in pairs:
            base_asset_name = str(data[pair]['pair'].base_asset)
            second_asset_name = str(data[pair]['pair'].second_asset)

            data[pair]['percentage_of_total'] = (
                totals['spend_base_asset_per_token'][base_asset_name][second_asset_name]
                / totals['spend_base_asset'][base_asset_name]
            ) * 100

        totals['calculated_grow_in_base_asset'] = [*totals['calculated_grow_in_base_asset'].items()]
        totals['spend_base_asset'] = [*totals['spend_base_asset'].items()]

        return render(request, 'admin/investitions/average_price.html', context={
            'data': data.values(),
            'totals': totals,
            'cl': {
                'opts': Fake._meta
            },
            'opts': Fake._meta,
        })

