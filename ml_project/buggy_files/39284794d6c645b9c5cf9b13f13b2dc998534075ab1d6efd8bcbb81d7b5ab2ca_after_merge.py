    def _process_exception(resp, **kwargs):
        unit = kwargs.get("unit")
        if unit == 0:
            err = {
                "message": "Broadcast message, ignoring errors!!!"
            }
        else:
            if isinstance(resp, ExceptionResponse):
                err = {
                    'original_function_code': "{} ({})".format(
                        resp.original_code, hex(resp.original_code)),
                    'error_function_code': "{} ({})".format(
                        resp.function_code, hex(resp.function_code)),
                    'exception code': resp.exception_code,
                    'message': ModbusExceptions.decode(resp.exception_code)
                }
            elif isinstance(resp, ModbusIOException):
                err = {
                    'original_function_code': "{} ({})".format(
                        resp.fcode, hex(resp.fcode)),
                    'error': resp.message
                }
            else:
                err = {
                    'error': str(resp)
                }
        return err