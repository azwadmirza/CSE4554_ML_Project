    def run(self):
        """Run the Python code!"""

        # Create a module to serve as __main__
        main_mod = types.ModuleType('__main__')

        from_pyc = self.arg0.endswith((".pyc", ".pyo"))
        main_mod.__file__ = self.arg0
        if from_pyc:
            main_mod.__file__ = main_mod.__file__[:-1]
        if self.package is not None:
            main_mod.__package__ = self.package
        main_mod.__loader__ = self.loader
        if self.spec is not None:
            main_mod.__spec__ = self.spec

        main_mod.__builtins__ = BUILTINS

        sys.modules['__main__'] = main_mod

        # Set sys.argv properly.
        sys.argv = self.args

        try:
            # Make a code object somehow.
            if from_pyc:
                code = make_code_from_pyc(self.arg0)
            else:
                code = make_code_from_py(self.arg0)
        except CoverageException:
            raise
        except Exception as exc:
            msg = "Couldn't run {filename!r} as Python code: {exc.__class__.__name__}: {exc}"
            raise CoverageException(msg.format(filename=self.arg0, exc=exc))

        # Execute the code object.
        # Return to the original directory in case the test code exits in
        # a non-existent directory.
        cwd = os.getcwd()
        try:
            exec(code, main_mod.__dict__)
        except SystemExit:                          # pylint: disable=try-except-raise
            # The user called sys.exit().  Just pass it along to the upper
            # layers, where it will be handled.
            raise
        except Exception:
            # Something went wrong while executing the user code.
            # Get the exc_info, and pack them into an exception that we can
            # throw up to the outer loop.  We peel one layer off the traceback
            # so that the coverage.py code doesn't appear in the final printed
            # traceback.
            typ, err, tb = sys.exc_info()

            # PyPy3 weirdness.  If I don't access __context__, then somehow it
            # is non-None when the exception is reported at the upper layer,
            # and a nested exception is shown to the user.  This getattr fixes
            # it somehow? https://bitbucket.org/pypy/pypy/issue/1903
            getattr(err, '__context__', None)

            # Call the excepthook.
            try:
                if hasattr(err, "__traceback__"):
                    err.__traceback__ = err.__traceback__.tb_next
                sys.excepthook(typ, err, tb.tb_next)
            except SystemExit:                      # pylint: disable=try-except-raise
                raise
            except Exception:
                # Getting the output right in the case of excepthook
                # shenanigans is kind of involved.
                sys.stderr.write("Error in sys.excepthook:\n")
                typ2, err2, tb2 = sys.exc_info()
                err2.__suppress_context__ = True
                if hasattr(err2, "__traceback__"):
                    err2.__traceback__ = err2.__traceback__.tb_next
                sys.__excepthook__(typ2, err2, tb2.tb_next)
                sys.stderr.write("\nOriginal exception was:\n")
                raise ExceptionDuringRun(typ, err, tb.tb_next)
            else:
                sys.exit(1)
        finally:
            os.chdir(cwd)