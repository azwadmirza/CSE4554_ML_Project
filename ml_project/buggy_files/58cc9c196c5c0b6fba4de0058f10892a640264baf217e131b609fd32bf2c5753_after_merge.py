def execute_explicit_examples(state, wrapped_test, arguments, kwargs):
    original_argspec = getfullargspec(state.test)

    for example in reversed(getattr(wrapped_test, "hypothesis_explicit_examples", ())):
        example_kwargs = dict(original_argspec.kwonlydefaults or {})
        if example.args:
            if len(example.args) > len(original_argspec.args):
                raise InvalidArgument(
                    "example has too many arguments for test. "
                    "Expected at most %d but got %d"
                    % (len(original_argspec.args), len(example.args))
                )
            example_kwargs.update(
                dict(zip(original_argspec.args[-len(example.args) :], example.args))
            )
        else:
            example_kwargs.update(example.kwargs)
        if Phase.explicit not in state.settings.phases:
            continue
        example_kwargs.update(kwargs)

        with local_settings(state.settings):
            fragments_reported = []
            try:
                with with_reporter(fragments_reported.append):
                    state.execute_once(
                        ArtificialDataForExample(example_kwargs),
                        is_final=True,
                        print_example=True,
                    )
            except UnsatisfiedAssumption:
                # Odd though it seems, we deliberately support explicit examples that
                # are then rejected by a call to `assume()`.  As well as iterative
                # development, this is rather useful to replay Hypothesis' part of
                # a saved failure when other arguments are supplied by e.g. pytest.
                # See https://github.com/HypothesisWorks/hypothesis/issues/2125
                pass
            except BaseException as err:
                # In order to support reporting of multiple failing examples, we yield
                # each of the (report text, error) pairs we find back to the top-level
                # runner.  This also ensures that user-facing stack traces have as few
                # frames of Hypothesis internals as possible.
                err = err.with_traceback(get_trimmed_traceback())

                # One user error - whether misunderstanding or typo - we've seen a few
                # times is to pass strategies to @example() where values are expected.
                # Checking is easy, and false-positives not much of a problem, so:
                if any(
                    isinstance(arg, SearchStrategy)
                    for arg in example.args + tuple(example.kwargs.values())
                ):
                    new = HypothesisWarning(
                        "The @example() decorator expects to be passed values, but "
                        "you passed strategies instead.  See https://hypothesis."
                        "readthedocs.io/en/latest/reproducing.html for details."
                    )
                    new.__cause__ = err
                    err = new

                yield (fragments_reported, err)
                if state.settings.report_multiple_bugs:
                    continue
                break
            finally:
                if fragments_reported:
                    assert fragments_reported[0].startswith("Falsifying example")
                    fragments_reported[0] = fragments_reported[0].replace(
                        "Falsifying example", "Falsifying explicit example", 1
                    )

            if fragments_reported:
                verbose_report(fragments_reported[0].replace("Falsifying", "Trying", 1))
                for f in fragments_reported[1:]:
                    verbose_report(f)