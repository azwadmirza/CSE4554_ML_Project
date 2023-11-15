def given(
    *given_arguments,  # type: Union[SearchStrategy, InferType]
    **given_kwargs  # type: Union[SearchStrategy, InferType]
):
    # type: (...) -> Callable[[Callable[..., None]], Callable[..., None]]
    """A decorator for turning a test function that accepts arguments into a
    randomized test.

    This is the main entry point to Hypothesis.
    """
    def run_test_with_generator(test):
        if hasattr(test, '_hypothesis_internal_test_function_without_warning'):
            # Pull out the original test function to avoid the warning we
            # stuck in about using @settings without @given.
            test = test._hypothesis_internal_test_function_without_warning
        if inspect.isclass(test):
            # Provide a meaningful error to users, instead of exceptions from
            # internals that assume we're dealing with a function.
            raise InvalidArgument('@given cannot be applied to a class.')
        generator_arguments = tuple(given_arguments)
        generator_kwargs = dict(given_kwargs)

        original_argspec = getfullargspec(test)

        check_invalid = is_invalid_test(
            test.__name__, original_argspec,
            generator_arguments, generator_kwargs)

        if check_invalid is not None:
            return check_invalid

        for name, strategy in zip(reversed(original_argspec.args),
                                  reversed(generator_arguments)):
            generator_kwargs[name] = strategy

        argspec = new_given_argspec(original_argspec, generator_kwargs)

        @impersonate(test)
        @define_function_signature(
            test.__name__, test.__doc__, argspec
        )
        def wrapped_test(*arguments, **kwargs):
            # Tell pytest to omit the body of this function from tracebacks
            __tracebackhide__ = True

            test = wrapped_test.hypothesis.inner_test

            if getattr(test, 'is_hypothesis_test', False):
                note_deprecation((
                    'You have applied @given to test: %s more than once. In '
                    'future this will be an error. Applying @given twice '
                    'wraps the test twice, which can be extremely slow. A '
                    'similar effect can be gained by combining the arguments '
                    'of the two calls to given. For example, instead of '
                    '@given(booleans()) @given(integers()), you could write '
                    '@given(booleans(), integers())') % (test.__name__, )
                )

            settings = wrapped_test._hypothesis_internal_use_settings

            random = get_random_for_wrapped_test(test, wrapped_test)

            if infer in generator_kwargs.values():
                hints = get_type_hints(test)
            for name in [name for name, value in generator_kwargs.items()
                         if value is infer]:
                if name not in hints:
                    raise InvalidArgument(
                        'passed %s=infer for %s, but %s has no type annotation'
                        % (name, test.__name__, name))
                generator_kwargs[name] = st.from_type(hints[name])

            processed_args = process_arguments_to_given(
                wrapped_test, arguments, kwargs, generator_arguments,
                generator_kwargs, argspec, test, settings
            )
            arguments, kwargs, test_runner, search_strategy = processed_args

            runner = getattr(search_strategy, 'runner', None)
            if isinstance(runner, TestCase) and test.__name__ in dir(TestCase):
                msg = ('You have applied @given to the method %s, which is '
                       'used by the unittest runner but is not itself a test.'
                       '  This is not useful in any way.' % test.__name__)
                fail_health_check(settings, msg, HealthCheck.not_a_test_method)
            if bad_django_TestCase(runner):  # pragma: no cover
                # Covered by the Django tests, but not the pytest coverage task
                raise InvalidArgument(
                    'You have applied @given to a method on %s, but this '
                    'class does not inherit from the supported versions in '
                    '`hypothesis.extra.django`.  Use the Hypothesis variants '
                    'to ensure that each example is run in a separate '
                    'database transaction.' % qualname(type(runner))
                )

            state = StateForActualGivenExecution(
                test_runner, search_strategy, test, settings, random,
                had_seed=wrapped_test._hypothesis_internal_use_seed
            )

            reproduce_failure = \
                wrapped_test._hypothesis_internal_use_reproduce_failure

            if reproduce_failure is not None:
                expected_version, failure = reproduce_failure
                if expected_version != __version__:
                    raise InvalidArgument((
                        'Attempting to reproduce a failure from a different '
                        'version of Hypothesis. This failure is from %s, but '
                        'you are currently running %r. Please change your '
                        'Hypothesis version to a matching one.'
                    ) % (expected_version, __version__))
                try:
                    state.execute(ConjectureData.for_buffer(
                        decode_failure(failure)),
                        print_example=True, is_final=True,
                    )
                    raise DidNotReproduce(
                        'Expected the test to raise an error, but it '
                        'completed successfully.'
                    )
                except StopTest:
                    raise DidNotReproduce(
                        'The shape of the test data has changed in some way '
                        'from where this blob was defined. Are you sure '
                        "you're running the same test?"
                    )
                except UnsatisfiedAssumption:
                    raise DidNotReproduce(
                        'The test data failed to satisfy an assumption in the '
                        'test. Have you added it since this blob was '
                        'generated?'
                    )

            execute_explicit_examples(
                test_runner, test, wrapped_test, settings, arguments, kwargs
            )

            if settings.max_examples <= 0:
                return

            if not (
                Phase.reuse in settings.phases or
                Phase.generate in settings.phases
            ):
                return

            try:
                if isinstance(runner, TestCase) and hasattr(runner, 'subTest'):
                    subTest = runner.subTest
                    try:
                        setattr(runner, 'subTest', fake_subTest)
                        state.run()
                    finally:
                        setattr(runner, 'subTest', subTest)
                else:
                    state.run()
            except BaseException as e:
                generated_seed = \
                    wrapped_test._hypothesis_internal_use_generated_seed
                with local_settings(settings):
                    if not (state.failed_normally or generated_seed is None):
                        if running_under_pytest:
                            report(
                                'You can add @seed(%(seed)d) to this test or '
                                'run pytest with --hypothesis-seed=%(seed)d '
                                'to reproduce this failure.' % {
                                    'seed': generated_seed})
                        else:
                            report(
                                'You can add @seed(%d) to this test to '
                                'reproduce this failure.' % (generated_seed,))
                    # The dance here is to avoid showing users long tracebacks
                    # full of Hypothesis internals they don't care about.
                    # We have to do this inline, to avoid adding another
                    # internal stack frame just when we've removed the rest.
                    if PY2:
                        # Python 2 doesn't have Exception.with_traceback(...);
                        # instead it has a three-argument form of the `raise`
                        # statement.  Which is a SyntaxError on Python 3.
                        exec(
                            'raise type(e), e, get_trimmed_traceback()',
                            globals(), locals()
                        )
                    # On Python 3, we swap out the real traceback for our
                    # trimmed version.  Using a variable ensures that the line
                    # which will actually appear in trackbacks is as clear as
                    # possible - "raise the_error_hypothesis_found".
                    the_error_hypothesis_found = \
                        e.with_traceback(get_trimmed_traceback())
                    raise the_error_hypothesis_found

        for attrib in dir(test):
            if not (attrib.startswith('_') or hasattr(wrapped_test, attrib)):
                setattr(wrapped_test, attrib, getattr(test, attrib))
        wrapped_test.is_hypothesis_test = True
        if hasattr(test, '_hypothesis_internal_settings_applied'):
            # Used to check if @settings is applied twice.
            wrapped_test._hypothesis_internal_settings_applied = True
        wrapped_test._hypothesis_internal_use_seed = getattr(
            test, '_hypothesis_internal_use_seed', None
        )
        wrapped_test._hypothesis_internal_use_settings = getattr(
            test, '_hypothesis_internal_use_settings', None
        ) or Settings.default
        wrapped_test._hypothesis_internal_use_reproduce_failure = getattr(
            test, '_hypothesis_internal_use_reproduce_failure', None
        )
        wrapped_test.hypothesis = HypothesisHandle(test)
        return wrapped_test
    return run_test_with_generator