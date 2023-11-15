def sys_stdout_write_wrapper(s, stream=stdout_byte_stream):
    stream.write(five.to_bytes(s))