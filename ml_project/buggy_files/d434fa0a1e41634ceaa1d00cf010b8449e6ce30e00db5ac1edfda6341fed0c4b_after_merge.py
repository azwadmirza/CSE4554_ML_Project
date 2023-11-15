    async def run() -> None:
        component, connect_to_endpoints = _setup_standalone_component(
            component_type, APP_IDENTIFIER_ETH1)
        async with _run_eventbus_for_component(component, connect_to_endpoints) as event_bus:
            async with _run_asyncio_component_in_proc(component, event_bus) as component_task:
                sigint_task = asyncio.create_task(got_sigint.wait())
                tasks = [component_task, sigint_task]
                try:
                    await wait_first(tasks, max_wait_after_cancellation=2)
                except asyncio.TimeoutError:
                    logger.warning(
                        "Timed out waiting for tasks to terminate after cancellation: %s",
                        tasks
                    )