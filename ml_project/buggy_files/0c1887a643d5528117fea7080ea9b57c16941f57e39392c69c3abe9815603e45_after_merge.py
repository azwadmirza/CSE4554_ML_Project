async def run_background_asyncio_services(services: Sequence[ServiceAPI]) -> None:
    async with contextlib.AsyncExitStack() as stack:
        managers = tuple([
            await stack.enter_async_context(background_asyncio_service(service))
            for service in services
        ])
        # If any of the services terminate, we do so as well.
        await wait_first_asyncio([
            asyncio.create_task(manager.wait_finished())
            for manager in managers
        ])