    def _send_command(
        self,
        command,
        delay_factor=None,
        start=None,
        expect_string=None,
        read_output=None,
        receive=False,
    ):

        if not expect_string:
            expect_string = self._XML_MODE_PROMPT

        if read_output is None:
            read_output = ""

        if not delay_factor:
            delay_factor = self._READ_DELAY

        if not start:
            start = time.time()

        output = read_output

        last_read = ""

        if not read_output and not receive:
            # because the XML agent is able to process only one single request over the same SSH
            # session at a time first come first served
            self._lock_xml_agent(start)
            try:
                max_loops = self.timeout / delay_factor
                last_read = self.device.send_command_expect(
                    command,
                    expect_string=expect_string,
                    strip_prompt=False,
                    strip_command=False,
                    delay_factor=delay_factor,
                    max_loops=max_loops,
                )
                output += last_read
            except IOError:
                if (not last_read and self._in_cli_mode()) or (
                    self._cli_prompt in output
                    and "% Invalid input detected at '^' marker." in output
                ):
                    # something happened
                    # e.g. connection with the XML agent died while reading
                    # netmiko throws error and the last output read is empty (ofc)
                    # and in CLI mode
                    #
                    # OR
                    #
                    # Sometimes the XML agent simply exits and all issued commands provide the
                    #  following output (as in CLI mode)
                    # <?
                    #       ^
                    # % Invalid input detected at '^' marker.
                    # RP/0/RSP1/CPU0:edge01.dus01#<xml version="1.0" encoding="UTF-8"?
                    #                             ^
                    # % Invalid input detected at '^' marker.
                    # RP/0/RSP1/CPU0:edge01.dus01#<xml version
                    #
                    # Which of course does not contain the XML and netmiko throws the not found
                    # error therefore we need to re-enter in XML mode
                    self._enter_xml_mode()
                    # and let's issue the command again if still got time
                    if not self._timeout_exceeded(start=start):
                        # if still got time
                        # reiterate the command from the beginning
                        return self._send_command(
                            command,
                            expect_string=expect_string,
                            delay_factor=delay_factor,
                        )
        else:
            output += self._netmiko_recv()  # try to read some more

        if "0xa3679e00" in output or "0xa367da00" in output:
            # when multiple parallel request are made, the device throws one of the the errors:
            # ---
            # ERROR: 0xa3679e00 'XML Service Library' detected the 'fatal' condition
            # 'Multiple concurrent requests are not allowed over the same session.
            # A request is already in progress on this session.'
            #
            # ERROR: 0xa367da00 XML Service Library' detected the 'fatal' condition
            # 'Sending multiple documents is not supported.'
            # ---
            # we could use a mechanism similar to NETCONF and push the requests in queue and serve
            # them sequentially, BUT we are not able to assign unique IDs and identify the
            # request-reply map so will throw an error that does not help too much :(
            raise XMLCLIError("XML agent cannot process parallel requests!", self)

        if not output.strip().endswith("XML>"):
            if "0x44318c06" in output or (
                self._cli_prompt
                and expect_string != self._cli_prompt
                and (
                    output.startswith(self._cli_prompt)
                    or output.endswith(self._cli_prompt)
                )
            ):
                # sometimes the device throws a stupid error like:
                # ERROR: 0x44318c06 'XML-TTY' detected the 'warning' condition
                # 'A Light Weight Messaging library communication function returned an error': No
                # such device or address and the XML agent connection is closed, but the SSH
                # connection is fortunately maintained
                # OR sometimes, the device simply exits from the XML mode without any clue
                # In both cases, we need to re-enter in XML mode...
                # so, whenever the CLI promt is detected, will re-enter in XML mode
                # unless the expected string is the prompt
                self._unlock_xml_agent()
                self._enter_xml_mode()
                # however, the command could not be executed properly, so we need to raise the
                # XMLCLIError exception
                raise XMLCLIError(
                    "Could not properly execute the command. Re-entering XML mode...",
                    self,
                )
            if (
                not output.strip()
            ):  # empty output, means that the device did not start delivering the output
                # but for sure is still in XML mode as netmiko did not throw error
                if not self._timeout_exceeded(start=start):
                    return self._send_command(
                        command, receive=True, start=start
                    )  # let's try receiving more

            raise XMLCLIError(output.strip(), self)

        self._unlock_xml_agent()
        return str(output.replace("XML>", "").strip())