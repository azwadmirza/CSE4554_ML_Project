def given(
    *_given_arguments: Union[SearchStrategy, InferType],
    **_given_kwargs: Union[SearchStrategy, InferType]
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """A decorator for turning a test function that accepts arguments into a
    randomized test.

    This is the main entry point to Hypothesis.
    """

    def run_test_as_given(test):
        if inspect.isclass(test):
            # Provide a meaningful error to users, instead of exceptions from
            # internals that assume we're dealing with a function.
            raise InvalidArgument("@given cannot be applied to a class.")
        given_arguments = tuple(_given_arguments)
        given_kwargs = dict(_given_kwargs)

        original_argspec = getfullargspec(test)

        check_invalid = is_invalid_test(
            test.__name__, original_argspec, given_arguments, given_kwargs
        )

        # If the argument check found problems, return a dummy test function
        # that will raise an error if it is actually called.
        if check_invalid is not None:
            return check_invalid

        # Because the argument check succeeded, we can convert @given's
        # positional arguments into keyword arguments for simplicity.
        if given_arguments:
            assert not given_kwargs
            for name, strategy in zip(
                reversed(original_argspec.args), reversed(given_arguments)
            ):
                given_kwargs[name] = strategy
        # These have been converted, so delete them to prevent accidental use.
        del given_arguments

        argspec = new_given_argspec(original_argspec, given_kwargs)

        # Use type information to convert "infer" arguments into appropriate strategies.
        if infer in given_kwargs.values():
            hints = get_type_hints(test)
        for name in [name for name, value in given_kwargs.items() if value is infer]:
            if name not in hints:
                # As usual, we want to emit this error when the test is executed,
                # not when it's decorated.

                @impersonate(test)
                @define_function_signature(test.__name__, test.__doc__, argspec)
                def wrapped_test(*arguments, **kwargs):
                    __tracebackhide__ = True
                    raise InvalidArgument(
                        "passed %s=infer for %s, but %s has no type annotation"
                        % (name, test.__name__, name)
                    )

                return wrapped_test

            given_kwargs[name] = st.from_type(hints[name])

        @impersonate(test)
        @define_function_signature(test.__name__, test.__doc__, argspec)
        def wrapped_test(*arguments, **kwargs):
            # Tell pytest to omit the body of this function from tracebacks
            __tracebackhide__ = True

            test = wrapped_test.hypothesis.inner_test

            if getattr(test, "is_hypothesis_test", False):
                raise InvalidArgument(
                    (
                        "You have applied @given to the test %s more than once, which "
                        "wraps the test several times and is extremely slow. A "
                        "similar effect can be gained by combining the arguments "
                        "of the two calls to given. For example, instead of "
                        "@given(booleans()) @given(integers()), you could write "
                        "@given(booleans(), integers())"
                    )
                    % (test.__name__,)
                )

            settings = wrapped_test._hypothesis_internal_use_settings

            random = get_random_for_wrapped_test(test, wrapped_test)

            processed_args = process_arguments_to_given(
                wrapped_test, arguments, kwargs, given_kwargs, argspec, settings,
            )
            arguments, kwargs, test_runner, search_strategy = processed_args

            runner = getattr(search_strategy, "runner", None)
            if isinstance(runner, TestCase) and test.__name__ in dir(TestCase):
                msg = (
                    "You have applied @given to the method %s, which is "
                    "used by the unittest runner but is not itself a test."
                    "  This is not useful in any way." % test.__name__
                )
                fail_health_check(settings, msg, HealthCheck.not_a_test_method)
            if bad_django_TestCase(runner):  # pragma: no cover
                # Covered by the Django tests, but not the pytest coverage task
                raise InvalidArgument(
                    "You have applied @given to a method on %s, but this "
                    "class does not inherit from the supported versions in "
                    "`hypothesis.extra.django`.  Use the Hypothesis variants "
                    "to ensure that each example is run in a separate "
                    "database transaction." % qualname(type(runner))
                )

            state = StateForActualGivenExecution(
                test_runner, search_strategy, test, settings, random, wrapped_test,
            )

            reproduce_failure = wrapped_test._hypothesis_internal_use_reproduce_failure

            # If there was a @reproduce_failure decorator, use it to reproduce
            # the error (or complain that we couldn't). Either way, this will
            # always raise some kind of error.
            if reproduce_failure is not None:
                expected_version, failure = reproduce_failure
                if expected_version != __version__:
                    raise InvalidArgument(
                        (
                            "Attempting to reproduce a failure from a different "
                            "version of Hypothesis. This failure is from %s, but "
                            "you are currently running %r. Please change your "
                            "Hypothesis version to a matching one."
                        )
                        % (expected_version, __version__)
                    )
                try:
                    state.execute_once(
                        ConjectureData.for_buffer(decode_failure(failure)),
                        print_example=True,
                        is_final=True,
                    )
                    raise DidNotReproduce(
                        "Expected the test to raise an error, but it "
                        "completed successfully."
                    )
                except StopTest:
                    raise DidNotReproduce(
                        "The shape of the test data has changed in some way "
                        "from where this blob was defined. Are you sure "
                        "you're running the same test?"
                    )
                except UnsatisfiedAssumption:
                    raise DidNotReproduce(
                        "The test data failed to satisfy an assumption in the "
                        "test. Have you added it since this blob was "
                        "generated?"
                    )

            # There was no @reproduce_failure, so start by running any explicit
            # examples from @example decorators.
            errors = list(
                execute_explicit_examples(state, wrapped_test, arguments, kwargs)
            )
            with local_settings(state.settings):
                if len(errors) > 1:
                    # If we're not going to report multiple bugs, we would have
                    # stopped running explicit examples at the first failure.
                    assert state.settings.report_multiple_bugs
                    for fragments, err in errors:
                        for f in fragments:
                            report(f)
                        tb_lines = traceback.format_exception(
                            type(err), err, err.__traceback__
                        )
                        report("".join(tb_lines))
                    msg = "Hypothesis found %d failures in explicit examples."
                    raise MultipleFailures(msg % (len(errors)))
                elif errors:
                    fragments, the_error_hypothesis_found = errors[0]
                    for f in fragments:
                        report(f)
                    raise the_error_hypothesis_found

            # If there were any explicit examples, they all ran successfully.
            # The next step is to use the Conjecture engine to run the test on
            # many different inputs.

            if not (
                Phase.reuse in settings.phases or Phase.generate in settings.phases
            ):
                return

            try:
                if isinstance(runner, TestCase) and hasattr(runner, "subTest"):
                    subTest = runner.subTest
                    try:
                        runner.subTest = fake_subTest
                        state.run_engine()
                    finally:
                        runner.subTest = subTest
                else:
                    state.run_engine()
            except BaseException as e:
                # The exception caught here should either be an actual test
                # failure (or MultipleFailures), or some kind of fatal error
                # that caused the engine to stop.

                generated_seed = wrapped_test._hypothesis_internal_use_generated_seed
                with local_settings(settings):
                    if not (state.failed_normally or generated_seed is None):
                        if running_under_pytest:
                            report(
                                "You can add @seed(%(seed)d) to this test or "
                                "run pytest with --hypothesis-seed=%(seed)d "
                                "to reproduce this failure." % {"seed": generated_seed}
                            )
                        else:
                            report(
                                "You can add @seed(%d) to this test to "
                                "reproduce this failure." % (generated_seed,)
                            )
                    # The dance here is to avoid showing users long tracebacks
                    # full of Hypothesis internals they don't care about.
                    # We have to do this inline, to avoid adding another
                    # internal stack frame just when we've removed the rest.
                    #
                    # Using a variable for our trimmed error ensures that the line
                    # which will actually appear in tracebacks is as clear as
                    # possible - "raise the_error_hypothesis_found".
                    the_error_hypothesis_found = e.with_traceback(
                        get_trimmed_traceback()
                    )
                    raise the_error_hypothesis_found

        def _get_fuzz_target() -> Callable[
            [Union[bytes, bytearray, memoryview, BinaryIO]], Optional[bytes]
        ]:
            # Because fuzzing interfaces are very performance-sensitive, we use a
            # somewhat more complicated structure here.  `_get_fuzz_target()` is
            # called by the `HypothesisHandle.fuzz_one_input` property, allowing
            # us to defer our collection of the settings, random instance, and
            # reassignable `inner_test` (etc) until `fuzz_one_input` is accessed.
            #
            # We then share the performance cost of setting up `state` between
            # many invocations of the target.  We explicitly force `deadline=None`
            # for performance reasons, saving ~40% the runtime of an empty test.
            test = wrapped_test.hypothesis.inner_test
            settings = Settings(
                parent=wrapped_test._hypothesis_internal_use_settings, deadline=None
            )
            random = get_random_for_wrapped_test(test, wrapped_test)
            _args, _kwargs, test_runner, search_strategy = process_arguments_to_given(
                wrapped_test, (), {}, given_kwargs, argspec, settings,
            )
            assert not _args
            assert not _kwargs
            state = StateForActualGivenExecution(
                test_runner, search_strategy, test, settings, random, wrapped_test,
            )
            digest = function_digest(test)

            def fuzz_one_input(
                buffer: Union[bytes, bytearray, memoryview, BinaryIO]
            ) -> Optional[bytes]:
                # This inner part is all that the fuzzer will actually run,
                # so we keep it as small and as fast as possible.
                if isinstance(buffer, io.IOBase):
                    buffer = buffer.read()
                assert isinstance(buffer, (bytes, bytearray, memoryview))
                data = ConjectureData.for_buffer(buffer)
                try:
                    state.execute_once(data)
                except (StopTest, UnsatisfiedAssumption):
                    return None
                except BaseException:
                    if settings.database is not None:
                        settings.database.save(digest, bytes(data.buffer))
                    raise
                return bytes(data.buffer)

            fuzz_one_input.__doc__ = HypothesisHandle.fuzz_one_input.__doc__
            return fuzz_one_input

        # After having created the decorated test function, we need to copy
        # over some attributes to make the switch as seamless as possible.

        for attrib in dir(test):
            if not (attrib.startswith("_") or hasattr(wrapped_test, attrib)):
                setattr(wrapped_test, attrib, getattr(test, attrib))
        wrapped_test.is_hypothesis_test = True
        if hasattr(test, "_hypothesis_internal_settings_applied"):
            # Used to check if @settings is applied twice.
            wrapped_test._hypothesis_internal_settings_applied = True
        wrapped_test._hypothesis_internal_use_seed = getattr(
            test, "_hypothesis_internal_use_seed", None
        )
        wrapped_test._hypothesis_internal_use_settings = (
            getattr(test, "_hypothesis_internal_use_settings", None) or Settings.default
        )
        wrapped_test._hypothesis_internal_use_reproduce_failure = getattr(
            test, "_hypothesis_internal_use_reproduce_failure", None
        )
        wrapped_test.hypothesis = HypothesisHandle(test, _get_fuzz_target)
        return wrapped_test

    return run_test_as_given