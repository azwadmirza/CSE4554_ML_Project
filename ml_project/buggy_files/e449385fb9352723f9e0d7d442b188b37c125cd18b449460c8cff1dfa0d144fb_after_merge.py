        def run(data):
            with self.settings:
                with BuildContext(data, is_final=is_final):
                    import random as rnd_module
                    rnd_module.seed(0)
                    args, kwargs = data.draw(self.search_strategy)
                    if expected_failure is not None:
                        text_repr[0] = arg_string(test, args, kwargs)

                    if print_example:
                        report(
                            lambda: 'Falsifying example: %s(%s)' % (
                                test.__name__, arg_string(test, args, kwargs)))
                    elif current_verbosity() >= Verbosity.verbose:
                        report(
                            lambda: 'Trying example: %s(%s)' % (
                                test.__name__, arg_string(test, args, kwargs)))

                    if self.collector is None or not collect:
                        return test(*args, **kwargs)
                    else:  # pragma: no cover
                        try:
                            self.collector.start()
                            return test(*args, **kwargs)
                        finally:
                            self.collector.stop()