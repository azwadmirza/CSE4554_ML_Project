    def get_open_trades() -> List[Any]:
        """
        Query trades from persistence layer
        """
        return Trade.get_trades(Trade.is_open.is_(True)).all()