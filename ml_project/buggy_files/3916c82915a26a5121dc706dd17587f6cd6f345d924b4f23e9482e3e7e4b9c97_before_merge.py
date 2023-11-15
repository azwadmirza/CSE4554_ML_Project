    def exists(self, path):
        path = self._escape(self._unquote(path))
        script = '''
            If (Test-Path "%s")
            {
                $res = 0;
            }
            Else
            {
                $res = 1;
            }
            Write-Output "$res";
            Exit $res;
         ''' % path
        return self._encode_script(script)