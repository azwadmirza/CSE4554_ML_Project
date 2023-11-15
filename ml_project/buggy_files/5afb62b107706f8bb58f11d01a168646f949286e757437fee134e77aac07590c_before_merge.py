            def map_f(values, f):
                return lib.map_infer_mask(values, f, mask.view(np.uint8))