    def get_ticker(self, pair: str, refresh: Optional[bool] = True) -> dict:
        if refresh or pair not in self.cached_ticker.keys():
            data = _API.get_ticker(pair.replace('_', '-'))
            if not data['success']:
                Bittrex._validate_response(data)
                raise OperationalException('{message} params=({pair})'.format(
                    message=data['message'],
                    pair=pair))

            if not data.get('result') or\
                    not all(key in data.get('result', {}) for key in ['Bid', 'Ask', 'Last']):
                raise ContentDecodingError('{message} params=({pair})'.format(
                    message='Got invalid response from bittrex',
                    pair=pair))
            # Update the pair
            self.cached_ticker[pair] = {
                'bid': float(data['result']['Bid']),
                'ask': float(data['result']['Ask']),
                'last': float(data['result']['Last']),
            }
        return self.cached_ticker[pair]