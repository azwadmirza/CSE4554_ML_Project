async def run_background_trio_services(services: Sequence[ServiceAPI]) -> None:
    await _run_background_services(services, background_trio_service)