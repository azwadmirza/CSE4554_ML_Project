    def convert_search_space(spec: Dict, join: bool = False) -> Dict:
        spec = flatten_dict(spec, prevent_delimiter=True)
        resolved_vars, domain_vars, grid_vars = parse_spec_vars(spec)

        if grid_vars:
            raise ValueError(
                "Grid search parameters cannot be automatically converted "
                "to a BayesOpt search space.")

        def resolve_value(domain: Domain) -> Tuple[float, float]:
            sampler = domain.get_sampler()
            if isinstance(sampler, Quantized):
                logger.warning(
                    "BayesOpt search does not support quantization. "
                    "Dropped quantization.")
                sampler = sampler.get_sampler()

            if isinstance(domain, Float):
                if domain.sampler is not None:
                    logger.warning(
                        "BayesOpt does not support specific sampling methods. "
                        "The {} sampler will be dropped.".format(sampler))
                    return (domain.lower, domain.upper)

            raise ValueError("BayesOpt does not support parameters of type "
                             "`{}`".format(type(domain).__name__))

        # Parameter name is e.g. "a/b/c" for nested dicts
        bounds = {
            "/".join(path): resolve_value(domain)
            for path, domain in domain_vars
        }

        if join:
            spec.update(bounds)
            bounds = spec

        return bounds