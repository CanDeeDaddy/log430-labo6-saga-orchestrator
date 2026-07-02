"""
Handler: decrease stock
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import config
import requests
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class DecreaseStockHandler(Handler):
    """ Handle the stock check-out of a given list of products and quantities. Trigger rollback of previous steps in case of failure. """

    def __init__(self, order_id, order_item_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_item_data = order_item_data
        super().__init__()

    def run(self):
        """Call StoreManager to check out from stock"""
        try:
            response = requests.put(f'{config.API_GATEWAY_URL}/store-manager-api/stocks',
                json={
                    "items": self.order_item_data,
                    "operation": "-"
                },
                headers={'Content-Type': 'application/json'}
            )
            response_ok = response.ok
            if response_ok:
                self.logger.debug("Transition d'état: DecreaseStock -> STOCK_DECREASED")
                return OrderSagaState.STOCK_DECREASED
            else:
                self.logger.error(f"DecreaseStock a échoué : {response.status_code} - {response.text}")
                return self.rollback()

        except Exception as e:
            self.logger.error("DecreaseStock a échoué : " + str(e))
            return self.rollback()

    def rollback(self):
        """ Call StoreManager to delete order if stock decrease fails """
        try:
            requests.delete(f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}')
        except Exception as e:
            self.logger.error("Rollback DecreaseStock (suppression commande) a échoué : " + str(e))

        self.logger.debug(f"Transition d'état: DecreaseStockFailure -> ORDER_DELETED")
        return OrderSagaState.ORDER_DELETED