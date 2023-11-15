    def compute(self, data, weight_funcs=None, fill_value=None, with_uncert=False, **kwargs):

        del kwargs

        return get_sample_from_neighbour_info('nn',
                                              self.target_geo_def.shape,
                                              data,
                                              self.cache["valid_input_index"],
                                              self.cache["valid_output_index"],
                                              self.cache["index_array"],
                                              distance_array=self.cache[
                                                  "distance_array"],
                                              weight_funcs=weight_funcs,
                                              fill_value=fill_value,
                                              with_uncert=with_uncert)