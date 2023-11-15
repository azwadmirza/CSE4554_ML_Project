        async def _do_press(keycode: Tuple[int, int], hold: bool):
            await self.protocol.send(
                messages.send_hid_event(keycode[0], keycode[1], True)
            )

            if hold:
                # Hardcoded hold time for one second
                await asyncio.sleep(1)

            await self.protocol.send(
                messages.send_hid_event(keycode[0], keycode[1], False)
            )