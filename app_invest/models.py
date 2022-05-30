from datetime import timedelta
from decimal import Decimal
from typing import Optional

from django.db import models
from django.utils import timezone


class Investition(models.Model):
    """
    For calculation of success investitions and X's
    """
    buy_trade = models.ForeignKey(
        'app_trade.Trade',
        on_delete=models.PROTECT,
        verbose_name='Buy trade',
        related_name='investition_buys',
    )
    sell_trade = models.ForeignKey(
        'app_trade.Trade',
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        verbose_name='Sell trade',
        related_name='investition_sells',
    )

    @property
    def duration(self) -> Optional[timedelta]:
        """
        How many days and hour passed between buy and sell or buy order and now if investition is not fixed
        """

        if self.buy_trade and self.sell_trade:
            return self.sell_trade.transaction_date - self.buy_trade.transaction_date
        else:
            return timezone.now() - self.buy_trade.transaction_date

    @property
    def fixed_grow_percentage(self) -> Optional[Decimal]:
        """Fixed profit percentage in base asset"""
        if self.buy_trade and self.sell_trade:
            return (self.sell_trade.total / self.buy_trade.total - 1) * 100

    @property
    def fixed_grow_amount(self) -> Optional[float]:
        """Fixed profit in base asset"""
        if self.sell_trade and self.buy_trade:
            return float(self.sell_trade.total - self.buy_trade.total)

    @property
    def calculated_grow_amount(self) -> Optional[Decimal]:
        if not self.sell_trade and self.buy_trade.pair.current_quote:
            return (
                self.buy_trade.amount * self.buy_trade.pair.current_quote
                - self.buy_trade.amount * self.buy_trade.price
            )

    @property
    def calculated_grow_percentage(self) -> Optional[Decimal]:
        if not self.sell_trade and self.buy_trade.pair.current_quote:
            return (
                (
                    (self.buy_trade.amount * self.buy_trade.pair.current_quote)
                    / (self.buy_trade.amount * self.buy_trade.price)
                    - 1
                ) * 100
            )
