    def get_ticker_history(self, pair: str, tick_interval: int) -> List[Dict]:
        if tick_interval == 1:
            interval = 'oneMin'
        elif tick_interval == 5:
            interval = 'fiveMin'
        else:
            raise ValueError('Cannot parse tick_interval: {}'.format(tick_interval))

        data = _API_V2.get_candles(pair.replace('_', '-'), interval)
        # This sanity check is necessary because bittrex returns nonsense sometimes
        for prop in ['C', 'V', 'O', 'H', 'L', 'T']:
            for tick in data['result']:
                if prop not in tick.keys():
                    logger.warning('Required property {} not present in response'.format(prop))
                    return []

        if not data['success']:
            raise RuntimeError('{message} params=({pair})'.format(
                message=data['message'],
                pair=pair))

        return data['result']