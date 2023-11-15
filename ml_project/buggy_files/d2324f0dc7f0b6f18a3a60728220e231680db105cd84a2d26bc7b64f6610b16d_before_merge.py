    def _register_compressor(self, params, optimizer_params, compression_params):
        """Register compressor for BytePS

        params : mx.gluon.ParameterDict 
        optimizer_params : dict
        compression_params : dict
        """
        intra_compressor = Compression.none
        if not compression_params:
            return intra_compressor

        if "fp16" in compression_params:
            intra_compressor = Compression.fp16

        if "compressor" not in compression_params:
            warnings.warn("Compressor is not defined")
            return intra_compressor

        check_list = ["compressor", "ef", "momentum"]

        for _, param in params.items():
            # generic
            for item in check_list:
                if item in compression_params:
                    if isinstance(compression_params[item], str):
                        setattr(param, "byteps_%s_type" %
                                item, compression_params[item])
                    else:
                        raise TypeError("%s should be str" % item)

            # need parameter
            compressor = compression_params["compressor"]
            if compressor == "onebit":
                setattr(param, "byteps_compressor_onebit_scaling", str(
                    compression_params.get("scaling", False)))
            elif compressor == "topk" or compressor == "randomk" or compressor == "multibit":
                # raise KeyError if 'k' is not found
                setattr(param, "byteps_compressor_k",
                        compression_params["k"])

            if "momentum" in compression_params:
                setattr(param, "byteps_momentum_mu",
                        optimizer_params["momentum"])

        # change
        if "momentum" in compression_params:
            # 1bit compressor use an additional momentum for weight decay
            if compressor == "onebit" and "wd" in optimizer_params:
                intra_compressor = Compression.wdmom(
                    intra_compressor, optimizer_params["momentum"], optimizer_params["wd"])
                del optimizer_params["wd"]

            del optimizer_params['momentum']

        return intra_compressor