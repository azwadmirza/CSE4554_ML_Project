    async def _send_command(self, command, **kwargs):
        resp = await self.protocol.send_and_receive(messages.command(command, **kwargs))
        inner = resp.inner()

        if inner.sendError == scr.SendError.NoError:
            return

        print(scr.SendError.Name(inner.sendError))
        raise exceptions.CommandError(
            f"{CommandInfo_pb2.Command.Name(command)} failed: "
            f"SendError={scr.SendError.Name(inner.sendError)}, "
            "HandlerReturnStatus="
            f"{scr.HandlerReturnStatus.Name(inner.handlerReturnStatus)}"
        )