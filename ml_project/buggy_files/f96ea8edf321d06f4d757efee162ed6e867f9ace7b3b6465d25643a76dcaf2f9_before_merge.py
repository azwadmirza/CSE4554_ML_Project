    def get_open_trades() -> List[Any]:
        """
        Query trades from persistence layer
        """
        return Trade.query.filter(Trade.is_open.is_(True)).all()