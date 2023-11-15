    def convert_search_space(spec: Dict) -> Dict:
        spec = flatten_dict(spec, prevent_delimiter=True)
        resolved_vars, domain_vars, grid_vars = parse_spec_vars(spec)

        if grid_vars:
            raise ValueError(
                "Grid search parameters cannot be automatically converted "
                "to a SkOpt search space.")

        def resolve_value(domain: Domain) -> Union[Tuple, List]:
            sampler = domain.get_sampler()
            if isinstance(sampler, Quantized):
                logger.warning("SkOpt search does not support quantization. "
                               "Dropped quantization.")
                sampler = sampler.get_sampler()

            if isinstance(domain, Float):
                if domain.sampler is not None:
                    logger.warning(
                        "SkOpt does not support specific sampling methods."
                        " The {} sampler will be dropped.".format(sampler))
                return domain.lower, domain.upper

            if isinstance(domain, Integer):
                if domain.sampler is not None:
                    logger.warning(
                        "SkOpt does not support specific sampling methods."
                        " The {} sampler will be dropped.".format(sampler))
                return domain.lower, domain.upper

            if isinstance(domain, Categorical):
                return domain.categories

            raise ValueError("SkOpt does not support parameters of type "
                             "`{}`".format(type(domain).__name__))

        # Parameter name is e.g. "a/b/c" for nested dicts
        space = {
            "/".join(path): resolve_value(domain)
            for path, domain in domain_vars
        }

        return space