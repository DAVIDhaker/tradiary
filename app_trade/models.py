from datetime import timedelta, timezone
from decimal import Decimal
from typing import Optional

from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import datetime


class Asset(models.Model):
    market_symbol = models.CharField(max_length=32, verbose_name='Market symbol')

    def __str__(self):
        return self.market_symbol

    class Meta:
        ordering = 'market_symbol',


class Pair(models.Model):
    base_asset = models.ForeignKey(
        'Asset',
        on_delete=models.PROTECT,
        verbose_name='Base asset',
        related_name='pair_bases'
    )
    second_asset = models.ForeignKey(
        'Asset',
        on_delete=models.PROTECT,
        verbose_name='Second asset',
        related_name='pair_seconds'
    )
    current_quote = models.DecimalField(
        decimal_places=8,
        max_digits=23,
        null=True,
        blank=True,
        verbose_name='Current quote'
    )

    def __str__(self):
        return f'{self.base_asset}/{self.second_asset}'

    class Meta:
        ordering = 'base_asset', 'second_asset'


class Trade(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'

    transaction_date = models.DateTimeField(verbose_name='Date of making transaction')
    pair = models.ForeignKey('Pair', on_delete=models.PROTECT, verbose_name='Pair', related_name='trades')
    side = models.CharField(choices=(
        (BUY, 'Buy'),
        (SELL, 'Sell')
    ), max_length=4)
    price = models.DecimalField(max_digits=32, decimal_places=20, verbose_name='Price of asset')
    amount = models.DecimalField(max_digits=32, decimal_places=20, verbose_name='Amount of asset')

    @property
    def total(self):
        return self.price * self.amount

    def __str__(self):
        action = {
            self.BUY: 'Bought',
            self.SELL: 'Sold'
        }[self.side]

        return f'{action} {float(self.amount)} {self.pair.second_asset} ' \
               f'for {float(self.amount * self.price)} {self.pair.base_asset}'



# class Transaction(models.Model):
#     """
#     Operations of incomes or outcomes of capital.
#     """
#
#     INCOME = 'INCOME'
#     OUTCOME = 'OUTCOME'
#
#     at = models.DateTimeField(verbose_name='Happens at')
#     type = models.CharField(max_length=3, choices=((INCOME, 'Income'), (OUTCOME, 'Outcome')), verbose_name='Type')
#     asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name='Asset')
#     amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='Amount')
#
#     def __str__(self):
#         type = self.type
#         return f'{type}'
