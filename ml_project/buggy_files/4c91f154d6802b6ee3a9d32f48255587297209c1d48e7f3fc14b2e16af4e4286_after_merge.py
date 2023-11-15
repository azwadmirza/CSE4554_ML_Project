    def recognize(self, audio):
        """ Audio decoding - more info could be found at https://launchpad.net/adecaptcha """
        #print "!!!CAPTCHA :", audio
        try:
            cfg_file = os.path.join(os.path.split(clslib.__file__)[0], 'ulozto.cfg')
            text = clslib.classify_audio_file(audio, cfg_file)
            return text

        except NameError:
            self.log_error(_("Unable to decode audio captcha"),
                           _("Please install adecaptcha library from https://github.com/izderadicka/adecaptcha"))