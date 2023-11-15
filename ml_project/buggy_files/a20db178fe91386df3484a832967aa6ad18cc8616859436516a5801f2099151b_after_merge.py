    def fetch_file(self, in_path, out_path):
        super(Connection, self).fetch_file(in_path, out_path)
        in_path = self._shell._unquote(in_path)
        out_path = out_path.replace('\\', '/')
        # consistent with other connection plugins, we assume the caller has created the target dir
        display.vvv('FETCH "%s" TO "%s"' % (in_path, out_path), host=self._winrm_host)
        buffer_size = 2**19  # 0.5MB chunks
        out_file = None
        try:
            offset = 0
            while True:
                try:
                    script = '''
                        $path = '%(path)s'
                        If (Test-Path -Path $path -PathType Leaf)
                        {
                            $buffer_size = %(buffer_size)d
                            $offset = %(offset)d

                            $stream = New-Object -TypeName IO.FileStream($path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
                            $stream.Seek($offset, [System.IO.SeekOrigin]::Begin) > $null
                            $buffer = New-Object -TypeName byte[] $buffer_size
                            $bytes_read = $stream.Read($buffer, 0, $buffer_size)
                            if ($bytes_read -gt 0) {
                                $bytes = $buffer[0..($bytes_read - 1)]
                                [System.Convert]::ToBase64String($bytes)
                            }
                            $stream.Close() > $null
                        }
                        ElseIf (Test-Path -Path $path -PathType Container)
                        {
                            Write-Host "[DIR]";
                        }
                        Else
                        {
                            Write-Error "$path does not exist";
                            Exit 1;
                        }
                    ''' % dict(buffer_size=buffer_size, path=self._shell._escape(in_path), offset=offset)
                    display.vvvvv('WINRM FETCH "%s" to "%s" (offset=%d)' % (in_path, out_path, offset), host=self._winrm_host)
                    cmd_parts = self._shell._encode_script(script, as_list=True, preserve_rc=False)
                    result = self._winrm_exec(cmd_parts[0], cmd_parts[1:])
                    if result.status_code != 0:
                        raise IOError(to_native(result.std_err))
                    if result.std_out.strip() == '[DIR]':
                        data = None
                    else:
                        data = base64.b64decode(result.std_out.strip())
                    if data is None:
                        break
                    else:
                        if not out_file:
                            # If out_path is a directory and we're expecting a file, bail out now.
                            if os.path.isdir(to_bytes(out_path, errors='surrogate_or_strict')):
                                break
                            out_file = open(to_bytes(out_path, errors='surrogate_or_strict'), 'wb')
                        out_file.write(data)
                        if len(data) < buffer_size:
                            break
                        offset += len(data)
                except Exception:
                    traceback.print_exc()
                    raise AnsibleError('failed to transfer file to "%s"' % to_native(out_path))
        finally:
            if out_file:
                out_file.close()