    def is_valid_asset_pair(assets_dict, amount_positive=True):
        if 'first' not in assets_dict or 'second' not in assets_dict:
            return False
        if 'amount' not in assets_dict['first'] or 'type' not in assets_dict['first']:
            return False
        if 'amount' not in assets_dict['second'] or 'type' not in assets_dict['second']:
            return False

        if not MarketBlock.has_required_types([('amount', (int, long)), ('type', str)], assets_dict['first']):
            return False
        if not MarketBlock.has_required_types([('amount', (int, long)), ('type', str)], assets_dict['second']):
            return False

        if amount_positive and (assets_dict['first']['amount'] <= 0 or assets_dict['second']['amount'] <= 0):
            return False

        return True