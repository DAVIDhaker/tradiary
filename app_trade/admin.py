from django.contrib import admin
from django.db.models import Q

from . import models
from app_invest.models import Investition


admin.site.site_header = \
admin.site.site_title  = \
admin.site.index_title = 'Tradiary'


@admin.register(models.Asset)
class AssetAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Pair)
class AssetAdmin(admin.ModelAdmin):
    list_display = 'base_asset', 'second_asset', 'current_quote_'

    def current_quote_(self, obj: models.Pair):
        return f'{float(obj.current_quote)} {obj.base_asset}' if obj.current_quote else None


@admin.register(models.Trade)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_date',
        'pair',
        'side',
        'price',
        'amount',
        'total'
    )


@admin.register(Investition)
class InvestitionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'buy_trade',
        'sell_trade',
        'duration',
        'fixed_grow_',
        'current_grow_',
        'current_investition_price_',
    )

    list_filter = 'buy_trade__pair',

    def fixed_grow_(self, obj: Investition):
        result = []

        if obj.fixed_grow_amount:
            result.append(f'{obj.fixed_grow_amount:+} {obj.buy_trade.pair.base_asset}')

        if obj.fixed_grow_percentage:
            result.append(f'{obj.fixed_grow_percentage:+.2f}%')

        if result:
            return ' / '.join(result)

    def current_grow_(self, obj: Investition):
        result = []

        if not obj.sell_trade and obj.buy_trade.pair.current_quote:
            result.append(
                f'{float(obj.calculated_grow_amount):+} '
                f'{obj.buy_trade.pair.base_asset}'
            )

            result.append(f'{float(obj.calculated_grow_percentage):.2f}%')

        if result:
            return ' / '.join(result)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'buy_trade':
            kwargs['queryset'] = \
                models.Trade.objects\
                .filter(side=models.Trade.BUY)
        elif db_field.name == 'sell_trade':
            kwargs['queryset'] = \
                models.Trade.objects\
                .filter(side=models.Trade.SELL)

        return super(InvestitionAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def current_investition_price_(self, obj: Investition):
        if not obj.sell_trade and obj.buy_trade.pair.current_quote:
            return f'{float(obj.buy_trade.pair.current_quote * obj.buy_trade.amount)} {obj.buy_trade.pair.base_asset}'
