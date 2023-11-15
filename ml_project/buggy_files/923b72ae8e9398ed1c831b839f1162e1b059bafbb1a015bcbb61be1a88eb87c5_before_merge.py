    def inner_f(*args, **kwargs):
        extra_args = len(args) - len(all_args)
        if extra_args > 0:
            plural = "s" if extra_args > 1 else ""
            article = "" if plural else "a "
            warnings.warn(
                "Pass the following variable{} as {}keyword arg{}: {}. "
                "From version 0.12, the only valid positional argument "
                "will be `data`, and passing other arguments without an "
                "explcit keyword will result in an error or misinterpretation."
                .format(plural, article, plural,
                        ", ".join(kwonly_args[:extra_args])),
                FutureWarning
            )
        kwargs.update({k: arg for k, arg in zip(sig.parameters, args)})
        return f(**kwargs)