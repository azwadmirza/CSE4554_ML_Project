    def _store_dry_order(self, dry_order: Dict) -> None:
        closed_order = dry_order.copy()
        if closed_order["type"] in ["market", "limit"]:
            closed_order.update({
                "status": "closed",
                "filled": closed_order["amount"],
                "remaining": 0
                })
        if closed_order["type"] in ["stop_loss_limit"]:
            closed_order["info"].update({"stopPrice": closed_order["price"]})
        self._dry_run_open_orders[closed_order["id"]] = closed_order