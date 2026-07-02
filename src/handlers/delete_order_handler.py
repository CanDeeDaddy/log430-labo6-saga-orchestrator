"""
Handler: delete order
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import config
import requests
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class DeleteOrderHandler(Handler):
    """ Handle order deletion. """

    def __init__(self, order_id):
        """ Constructor method """
        self.order_id = order_id
        super().__init__()

    def run(self):
        """Call StoreManager to delete order"""
        try:
            response = requests.delete(f'{config.API_GATEWAY_URL}/store-manager-api/orders/{self.order_id}')
            if not response.ok:
                self.logger.error(f"DeleteOrder a échoué : {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error("DeleteOrder a échoué : " + str(e))

        self.logger.debug(f"Transition d'état: DeleteOrder -> ORDER_DELETED")
        return OrderSagaState.ORDER_DELETED

    def rollback(self):
        """
        (rollback not applicable for DeleteOrder)
        """
        # Nous héritons de la classe abstraite Handler, et par conséquent, l'implémentation de la méthode rollback() est obligatoire.
        pass