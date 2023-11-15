    def update_orders_dict_using_additional_data_dict(self, order_data_dict, additional_data_keys, additional_data_dict):
        if order_data_dict:
            self.data_dict_sanity_check(order_data_dict, treat_data_dict_as='layer_orders')

        self.data_dict_sanity_check(additional_data_dict, data_keys_list=additional_data_keys, treat_data_dict_as='layers')

        # FIXME: here we need to check whether the two dictionaries are in fact 'compatible' with respect to sample names
        #        they describe.

        for data_key in additional_data_keys:
            if '!' in data_key:
                # we don't order stacked bar charts
                continue

            # predict the type for proper assignment of 'null' values
            if '!' in data_key:
                predicted_key_type = "stackedbar"
            else:
                type_class = utils.get_predicted_type_of_items_in_a_dict(additional_data_dict, data_key)
                predicted_key_type = type_class.__name__ if type_class else 'unknown'

            layer_name_layer_data_tuples = [(additional_data_dict[layer][data_key] if additional_data_dict[layer][data_key] else self.nulls_per_type[predicted_key_type], layer) for layer in additional_data_dict]
            order_data_dict['>> ' + data_key] = {'newick': None, 'basic': ','.join([t[1] for t in sorted(layer_name_layer_data_tuples)])}
            order_data_dict['>> ' + data_key + ' (reverse)'] = {'newick': None, 'basic': ','.join([t[1] for t in sorted(layer_name_layer_data_tuples, reverse=True)])}

        return order_data_dict