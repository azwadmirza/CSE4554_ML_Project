    def code(self):
        """Return the processed JavaScript code of this script.

        Adorns the source code with GM_* methods for Greasemonkey
        compatibility and wraps it in an IIFE to hide it within a
        lexical scope. Note that this means line numbers in your
        browser's debugger/inspector will not match up to the line
        numbers in the source script directly.
        """
        template = jinja.js_environment.get_template('greasemonkey_wrapper.js')
        return template.render(
            scriptName=javascript.string_escape(
                "/".join([self.namespace or '', self.name])),
            scriptInfo=self._meta_json(),
            scriptMeta=javascript.string_escape(self.script_meta),
            scriptSource=self._code)