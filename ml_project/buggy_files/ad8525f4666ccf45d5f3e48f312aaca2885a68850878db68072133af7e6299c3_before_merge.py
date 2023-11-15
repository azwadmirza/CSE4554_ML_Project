def delete(instance: str, no_prompt: Optional[bool], drop_db: Optional[bool]):
    loop = asyncio.get_event_loop()
    if no_prompt is None:
        interactive = None
    else:
        interactive = not no_prompt
    loop.run_until_complete(remove_instance(instance, interactive, drop_db))