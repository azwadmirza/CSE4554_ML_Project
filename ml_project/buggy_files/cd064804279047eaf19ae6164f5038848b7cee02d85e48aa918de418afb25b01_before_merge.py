    def get_ticker(self, pair: str) -> dict:
        data = _API.get_ticker(pair.replace('_', '-'))
        if not data['success']:
            raise RuntimeError('{message} params=({pair})'.format(
                message=data['message'],
                pair=pair))
        return {
            'bid': float(data['result']['Bid']),
            'ask': float(data['result']['Ask']),
            'last': float(data['result']['Last']),
        }