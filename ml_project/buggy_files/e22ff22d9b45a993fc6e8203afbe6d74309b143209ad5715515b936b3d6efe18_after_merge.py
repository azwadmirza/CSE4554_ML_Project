def _setup_x(adata, layer):
    if layer is not None:
        assert (
            layer in adata.layers.keys()
        ), "{} is not a valid key in adata.layers".format(layer)
        logger.info('Using data from adata.layers["{}"]'.format(layer))
        x_loc = "layers"
        x_key = layer
        x = adata.layers[x_key]
    else:
        logger.info("Using data from adata.X")
        x_loc = "X"
        x_key = "None"
        x = adata.X

    if _check_nonnegative_integers(x) is False:
        logger_data_loc = (
            "adata.X" if layer is None else "adata.layers[{}]".format(layer)
        )
        warnings.warn(
            "{} does not contain unnormalized count data. Are you sure this is what you want?".format(
                logger_data_loc
            )
        )

    return x_loc, x_key