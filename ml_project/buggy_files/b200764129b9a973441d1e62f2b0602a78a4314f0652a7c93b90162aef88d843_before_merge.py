def run_asyncio_eth1_component(component_type: Type['AsyncioIsolatedComponent']) -> None:
    import asyncio
    from p2p.asyncio_utils import wait_first
    loop = asyncio.get_event_loop()
    got_sigint = asyncio.Event()
    loop.add_signal_handler(signal.SIGINT, got_sigint.set)
    loop.add_signal_handler(signal.SIGTERM, got_sigint.set)

    async def run() -> None:
        component, connect_to_endpoints = _setup_standalone_component(
            component_type, APP_IDENTIFIER_ETH1)
        async with _run_eventbus_for_component(component, connect_to_endpoints) as event_bus:
            async with _run_asyncio_component_in_proc(component, event_bus) as component_task:
                sigint_task = asyncio.create_task(got_sigint.wait())
                await wait_first([component_task, sigint_task], max_wait_after_cancellation=2)

    loop.run_until_complete(run())