    def query_balances(self, requested_save_data=False):
        balances = {}
        problem_free = True
        for exchange in self.connected_exchanges:
            exchange_balances, msg = getattr(self, exchange).query_balances()
            # If we got an error, disregard that exchange but make sure we don't save data
            if not exchange_balances:
                problem_free = False
            else:
                balances[exchange] = exchange_balances

        result, error_or_empty = self.blockchain.query_balances()
        if error_or_empty == '':
            balances['blockchain'] = result['totals']
        else:
            problem_free = False

        result = self.query_fiat_balances()
        if result != {}:
            balances['banks'] = result

        combined = combine_stat_dicts([v for k, v in balances.items()])
        total_usd_per_location = [(k, dict_get_sumof(v, 'usd_value')) for k, v in balances.items()]

        # calculate net usd value
        net_usd = FVal(0)
        for k, v in combined.items():
            net_usd += FVal(v['usd_value'])

        stats = {
            'location': {
            },
            'net_usd': net_usd
        }
        for entry in total_usd_per_location:
            name = entry[0]
            total = entry[1]
            stats['location'][name] = {
                'usd_value': total,
                'percentage_of_net_value': (total / net_usd).to_percentage(),
            }

        for k, v in combined.items():
            combined[k]['percentage_of_net_value'] = (v['usd_value'] / net_usd).to_percentage()

        result_dict = merge_dicts(combined, stats)

        allowed_to_save = requested_save_data or self.data.should_save_balances()
        if problem_free and allowed_to_save:
            self.data.save_balances_data(result_dict)

        # After adding it to the saved file we can overlay additional data that
        # is not required to be saved in the history file
        try:
            details = self.data.accountant.details
            for asset, (tax_free_amount, average_buy_value) in details.items():
                if asset not in result_dict:
                    continue

                result_dict[asset]['tax_free_amount'] = tax_free_amount
                result_dict[asset]['average_buy_value'] = average_buy_value

                current_price = result_dict[asset]['usd_value'] / result_dict[asset]['amount']
                if average_buy_value != FVal(0):
                    result_dict[asset]['percent_change'] = (
                        ((current_price - average_buy_value) / average_buy_value) * 100
                    )
                else:
                    result_dict[asset]['percent_change'] = 'INF'

        except AttributeError:
            pass

        return result_dict