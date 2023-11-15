    def dry_run_order(self, pair: str, ordertype: str, side: str, amount: float,
                      rate: float, params: Dict = {}) -> Dict[str, Any]:
        order_id = f'dry_run_{side}_{randint(0, 10**6)}'
        dry_order = {
            "id": order_id,
            'pair': pair,
            'price': rate,
            'amount': amount,
            "cost": amount * rate,
            'type': ordertype,
            'side': side,
            'remaining': amount,
            'datetime': arrow.utcnow().isoformat(),
            'status': "closed" if ordertype == "market" else "open",
            'fee': None,
            "info": {}
        }
        self._store_dry_order(dry_order)
        # Copy order and close it - so the returned order is open unless it's a market order
        return dry_order