async def make_process_uncacheable(uncacheable_process: UncacheableProcess) -> Process:
    uuid = await Get(
        UUID, UUIDRequest, UUIDRequest.scoped(cast(UUIDScope, uncacheable_process.scope.value))
    )

    process = uncacheable_process.process
    env = dict(process.env)

    # This is a slightly hacky way to force the process to run: since the env var
    #  value is unique, this input combination will never have been seen before,
    #  and therefore never cached. The two downsides are:
    #  1. This leaks into the process' environment, albeit with a funky var name that is
    #     unlikely to cause problems in practice.
    #  2. This run will be cached even though it can never be re-used.
    # TODO: A more principled way of forcing rules to run?
    env["__PANTS_FORCE_PROCESS_RUN__"] = str(uuid)

    return dataclasses.replace(process, env=FrozenDict(env))