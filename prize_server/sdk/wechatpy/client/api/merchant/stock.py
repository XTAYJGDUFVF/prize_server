# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from sdk.wechatpy import BaseWeChatAPI


class MerchantStock(BaseWeChatAPI):

    def add(self, product_id, quantity, sku_info=''):
        return self._post(
            'merchant/stock/add',
            data={
                'product_id': product_id,
                'quantity': quantity,
                'sku_info': sku_info
            }
        )

    def reduce(self, product_id, quantity, sku_info=''):
        return self._post(
            'merchant/stock/reduce',
            data={
                'product_id': product_id,
                'quantity': quantity,
                'sku_info': sku_info
            }
        )
