    def put_file(self, in_path, out_path):
        super(Connection, self).put_file(in_path, out_path)
        out_path = self._shell._unquote(out_path)
        display.vvv('PUT "%s" TO "%s"' % (in_path, out_path), host=self._winrm_host)
        if not os.path.exists(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound('file or module does not exist: "%s"' % to_native(in_path))

        script_template = u'''
            begin {{
                $path = '{0}'

                $DebugPreference = "Continue"
                $ErrorActionPreference = "Stop"
                Set-StrictMode -Version 2

                $fd = [System.IO.File]::Create($path)

                $sha1 = [System.Security.Cryptography.SHA1CryptoServiceProvider]::Create()

                $bytes = @() #initialize for empty file case
            }}
            process {{
               $bytes = [System.Convert]::FromBase64String($input)
               $sha1.TransformBlock($bytes, 0, $bytes.Length, $bytes, 0) | Out-Null
               $fd.Write($bytes, 0, $bytes.Length)
            }}
            end {{
                $sha1.TransformFinalBlock($bytes, 0, 0) | Out-Null

                $hash = [System.BitConverter]::ToString($sha1.Hash).Replace("-", "").ToLowerInvariant()

                $fd.Close()

                Write-Output "{{""sha1"":""$hash""}}"
            }}
        '''

        script = script_template.format(self._shell._escape(out_path))
        cmd_parts = self._shell._encode_script(script, as_list=True, strict_mode=False, preserve_rc=False)

        result = self._winrm_exec(cmd_parts[0], cmd_parts[1:], stdin_iterator=self._put_file_stdin_iterator(in_path, out_path))
        # TODO: improve error handling
        if result.status_code != 0:
            raise AnsibleError(to_native(result.std_err))

        put_output = json.loads(result.std_out)
        remote_sha1 = put_output.get("sha1")

        if not remote_sha1:
            raise AnsibleError("Remote sha1 was not returned")

        local_sha1 = secure_hash(in_path)

        if not remote_sha1 == local_sha1:
            raise AnsibleError("Remote sha1 hash {0} does not match local hash {1}".format(to_native(remote_sha1), to_native(local_sha1)))