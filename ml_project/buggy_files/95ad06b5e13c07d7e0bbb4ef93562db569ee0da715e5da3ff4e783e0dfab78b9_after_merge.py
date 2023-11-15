    def update_orders_dict_using_additional_data_dict(self, order_data_dict, additional_data_keys, additional_data_dict):
        if order_data_dict:
            self.data_dict_sanity_check(order_data_dict, treat_data_dict_as='layer_orders')

        # FIXME: here we need to check whether the two dictionaries are in fact 'compatible' with respect to sample names
        #        they describe.
        self.data_dict_sanity_check(additional_data_dict, data_keys_list=additional_data_keys, treat_data_dict_as='layers')

        sum_stackbar_items = {}
        for data_key in additional_data_keys:
            if '!' in data_key:
                stackbar_name = data_key.split('!')[0]

                if stackbar_name not in sum_stackbar_items:
                    sum_stackbar_items[stackbar_name] = {}

                for layer in additional_data_dict:
                    if layer not in sum_stackbar_items[stackbar_name]:
                        sum_stackbar_items[stackbar_name][layer] = 0.0

                    if additional_data_dict[layer][data_key]:
                        sum_stackbar_items[stackbar_name][layer] += float(additional_data_dict[layer][data_key])

        for data_key in additional_data_keys:
            if '!' in data_key:
                predicted_key_type = "stackedbar"
                stacked_bar_name, item_name = data_key.split('!')
                data_key_name = '%s [%s]' % (stacked_bar_name, item_name)
            else:
                type_class = utils.get_predicted_type_of_items_in_a_dict(additional_data_dict, data_key)
                predicted_key_type = type_class.__name__ if type_class else 'unknown'
                data_key_name = data_key

            if predicted_key_type == "stackedbar":
                stackbar_name = data_key.split('!')[0]
                layer_name_layer_data_tuples = []
                for layer in additional_data_dict:
                    if additional_data_dict[layer][data_key]:
                        if sum_stackbar_items[stackbar_name][layer] == 0:
                            layer_name_layer_data_tuples.append((0, layer))
                        else:
                            layer_name_layer_data_tuples.append(((float(additional_data_dict[layer][data_key]) / (1.0 * sum_stackbar_items[stackbar_name][layer])), layer))
                    else:
                        layer_name_layer_data_tuples.append((self.nulls_per_type[predicted_key_type], layer))
            else:
                layer_name_layer_data_tuples = [(additional_data_dict[layer][data_key] if additional_data_dict[layer][data_key] else self.nulls_per_type[predicted_key_type], layer) for layer in additional_data_dict]

            order_data_dict['>> ' + data_key_name] = {'newick': None, 'basic': ','.join([t[1] for t in sorted(layer_name_layer_data_tuples)])}
            order_data_dict['>> ' + data_key_name + ' (reverse)'] = {'newick': None, 'basic': ','.join([t[1] for t in sorted(layer_name_layer_data_tuples, reverse=True)])}

        return order_data_dict