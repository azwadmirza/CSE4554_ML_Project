    async def _press_key(self, key: str, action: InputAction) -> None:
        async def _do_press(keycode: Tuple[int, int], hold: bool):
            await self.protocol.send_and_receive(
                messages.send_hid_event(keycode[0], keycode[1], True)
            )

            if hold:
                # Hardcoded hold time for one second
                await asyncio.sleep(1)

            await self.protocol.send_and_receive(
                messages.send_hid_event(keycode[0], keycode[1], False)
            )

        keycode = _KEY_LOOKUP.get(key)
        if not keycode:
            raise Exception(f"unsupported key: {key}")

        if action == InputAction.SingleTap:
            await _do_press(keycode, False)
        elif action == InputAction.DoubleTap:
            await _do_press(keycode, False)
            await _do_press(keycode, False)
        elif action == InputAction.Hold:
            await _do_press(keycode, True)
        else:
            raise Exception(f"unsupported input action: {action}")