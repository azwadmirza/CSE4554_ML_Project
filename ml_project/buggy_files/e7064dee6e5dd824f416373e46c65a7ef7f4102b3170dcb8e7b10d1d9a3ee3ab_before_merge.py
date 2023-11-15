    async def run_behaviors(self, behaviors: Tuple[BehaviorAPI, ...]) -> None:
        async with contextlib.AsyncExitStack() as stack:
            futures: List[asyncio.Task[Any]] = [
                create_task(self.manager.wait_finished(), 'Connection/run_behaviors/wait_finished')]
            for behavior in behaviors:
                if behavior.should_apply_to(self):
                    behavior_exit = await stack.enter_async_context(behavior.apply(self))
                    futures.append(behavior_exit)

            self.behaviors_applied.set()
            # If wait_first() is called, cleanup_tasks() will be a no-op, but if any post_apply()
            # calls raise an exception, it will ensure we don't leak pending tasks that would
            # cause asyncio to complain.
            async with cleanup_tasks(*futures):
                try:
                    for behavior in behaviors:
                        behavior.post_apply()
                    await wait_first(futures, max_wait_after_cancellation=2)
                except PeerConnectionLost:
                    # Any of our behaviors may propagate a PeerConnectionLost, which is to be
                    # expected as many Connection APIs used by them can raise that. To avoid a
                    # DaemonTaskExit since we're returning silently, ensure we're cancelled.
                    self.manager.cancel()