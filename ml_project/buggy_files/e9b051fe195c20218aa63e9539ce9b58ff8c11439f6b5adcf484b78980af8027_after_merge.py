def api_method(f):
    def wrapper(api, *args, **kwargs):
        quiet = kwargs.pop("quiet", False)
        old_curdir = get_cwd()
        old_output = api.user_io.out
        quiet_output = ConanOutput(StringIO(), color=api.color) if quiet else None
        try:
            api.create_app(quiet_output=quiet_output)
            log_command(f.__name__, kwargs)
            with environment_append(api.app.cache.config.env_vars):
                return f(api, *args, **kwargs)
        except Exception as exc:
            if quiet_output:
                old_output.write(quiet_output._stream.getvalue())
                old_output.flush()
            msg = exception_message_safe(exc)
            try:
                log_exception(exc, msg)
            except BaseException:
                pass
            raise
        finally:
            os.chdir(old_curdir)
    return wrapper