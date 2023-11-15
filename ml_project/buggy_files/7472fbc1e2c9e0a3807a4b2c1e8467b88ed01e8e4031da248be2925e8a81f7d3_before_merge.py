    def is_valid_asset_pair(assets_dict):
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

        return True