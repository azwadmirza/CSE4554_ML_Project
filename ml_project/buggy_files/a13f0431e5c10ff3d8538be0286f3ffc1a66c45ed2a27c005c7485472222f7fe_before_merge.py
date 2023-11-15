    def dt_op_builder(df, *args, **kwargs):
        prop_val = getattr(df.squeeze().dt, property_name)
        if isinstance(prop_val, pandas.Series):
            return prop_val.to_frame()
        else:
            return pandas.DataFrame([prop_val])