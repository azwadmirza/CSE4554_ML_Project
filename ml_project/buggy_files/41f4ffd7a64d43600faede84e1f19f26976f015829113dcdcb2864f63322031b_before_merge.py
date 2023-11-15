    def __init__(self, value="C", secs=0.5, octave=4, sampleRate=44100,
                 bits=16, name='', autoLog=True, loops=0, stereo=True,
                 hamming=False):
        """
        """
        self.name = name  # only needed for autoLogging
        self.autoLog = autoLog

        if stereo == True:
            stereoChans = 2
        else:
            stereoChans = 0
        if bits == 16:
            # for pygame bits are signed for 16bit, signified by the minus
            bits = -16

        # check initialisation
        if not mixer.get_init():
            pygame.mixer.init(sampleRate, bits, stereoChans, 3072)

        inits = mixer.get_init()
        if inits is None:
            init()
            inits = mixer.get_init()
        self.sampleRate, self.format, self.isStereo = inits

        if hamming:
            logging.warning("Hamming was requested using the 'pygame' sound "
                            "library but hamming is not supported there.")
        self.hamming = False

        # try to create sound
        self._snd = None
        # distinguish the loops requested from loops actual because of
        # infinite tones (which have many loops but none requested)
        # -1 for infinite or a number of loops
        self.requestedLoops = self.loops = int(loops)
        self.setSound(value=value, secs=secs, octave=octave, hamming=False)