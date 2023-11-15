        async def on_close(response: Response) -> None:
            response.elapsed = datetime.timedelta(seconds=await timer.async_elapsed())
            if hasattr(stream, "aclose"):
                with map_exceptions(HTTPCORE_EXC_MAP, request=request):
                    await stream.aclose()