    def readConfig(self):

        self.config_lock.acquire()

        self.sections['transfers']['downloads'] = []

        if exists(os.path.join(self.data_dir, 'transfers.pickle')):
            # <1.2.13 stored transfers inside the main config
            try:
                handle = open(os.path.join(self.data_dir, 'transfers.pickle'), 'rb')
            except IOError as inst:
                log.addwarning(_("Something went wrong while opening your transfer list: %(error)s") % {'error': str(inst)})
            else:
                try:
                    self.sections['transfers']['downloads'] = pickle.load(handle)
                except (IOError, EOFError, ValueError) as inst:
                    log.addwarning(_("Something went wrong while reading your transfer list: %(error)s") % {'error': str(inst)})
            try:
                handle.close()
            except Exception:
                pass

        path, fn = os.path.split(self.filename)
        try:
            if not os.path.isdir(path):
                os.makedirs(path)
        except OSError as msg:
            log.addwarning("Can't create directory '%s', reported error: %s" % (path, msg))

        try:
            if not os.path.isdir(self.data_dir):
                os.makedirs(self.data_dir)
        except OSError as msg:
            log.addwarning("Can't create directory '%s', reported error: %s" % (path, msg))

        # Transition from 1.2.16 -> 1.4.0
        # Do the cleanup early so we don't get the annoying
        # 'Unknown config option ...' message
        self.removeOldOption("transfers", "pmqueueddir")
        self.removeOldOption("server", "lastportstatuscheck")
        self.removeOldOption("server", "serverlist")
        self.removeOldOption("userinfo", "descrutf8")
        self.removeOldOption("ui", "enabletrans")
        self.removeOldOption("ui", "mozembed")
        self.removeOldOption("ui", "open_in_mozembed")
        self.removeOldOption("ui", "tooltips")
        self.removeOldOption("ui", "transalpha")
        self.removeOldOption("ui", "transfilter")
        self.removeOldOption("ui", "transtint")
        self.removeOldOption("language", "language")
        self.removeOldOption("language", "setlanguage")
        self.removeOldSection("language")

        # Transition from 1.4.1 -> 1.4.2
        self.removeOldOption("columns", "downloads")
        self.removeOldOption("columns", "uploads")

        # Remove old encoding settings (1.4.3)
        self.removeOldOption("server", "enc")
        self.removeOldOption("server", "fallbackencodings")
        self.removeOldOption("server", "roomencoding")
        self.removeOldOption("server", "userencoding")

        # Remove soundcommand config, replaced by GSound (1.4.3)
        self.removeOldOption("ui", "soundcommand")

        # Checking for unknown section/options
        unknown1 = [
            'login', 'passw', 'enc', 'downloaddir', 'uploaddir', 'customban',
            'descr', 'pic', 'logsdir', 'roomlogsdir', 'privatelogsdir',
            'incompletedir', 'autoreply', 'afterfinish', 'downloadregexp',
            'afterfolder', 'default', 'chatfont', 'npothercommand', 'npplayer',
            'npformat', 'private_timestamp', 'rooms_timestamp', 'log_timestamp'
        ]

        unknown2 = {
            'ui': [
                "roomlistcollapsed", "tab_select_previous", "tabclosers",
                "tab_colors", "tab_reorderable", "buddylistinchatrooms", "trayicon",
                "showaway", "usernamehotspots", "exitdialog",
                "tab_icons", "spellcheck", "modes_order", "modes_visible",
                "chat_hidebuttons", "tab_status_icons", "notexists",
                "soundenabled", "speechenabled", "enablefilters", "width",
                "height", "xposition", "yposition", "labelmain", "labelrooms",
                "labelprivate", "labelinfo", "labelbrowse", "labelsearch"
            ],
            'words': [
                "completion", "censorwords", "replacewords", "autoreplaced",
                "censored", "characters", "tab", "cycle", "dropdown",
                "roomnames", "buddies", "roomusers", "commands",
                "aliases", "onematch"
            ]
        }

        for i in self.parser.sections():
            for j in self.parser.options(i):
                val = self.parser.get(i, j, raw=1)
                if i not in self.sections:
                    log.addwarning(_("Unknown config section '%s'") % i)
                elif j not in self.sections[i] and not (j == "filter" or i in ('plugins',)):
                    log.addwarning(_("Unknown config option '%(option)s' in section '%(section)s'") % {'option': j, 'section': i})
                elif j in unknown1 or (i in unknown2 and j not in unknown2[i]):
                    if val is not None and val != "None":
                        self.sections[i][j] = val
                    else:
                        self.sections[i][j] = None
                else:
                    try:
                        self.sections[i][j] = eval(val, {})
                    except Exception:
                        self.sections[i][j] = None
                        log.addwarning("CONFIG ERROR: Couldn't decode '%s' section '%s' value '%s'" % (str(j), str(i), str(val)))

        # Convert fs-based shared to virtual shared (pre 1.4.0)
        def _convert_to_virtual(x):
            if isinstance(x, tuple):
                return x
            virtual = x.replace('/', '_').replace('\\', '_').strip('_')
            log.addwarning("Renaming shared folder '%s' to '%s'. A rescan of your share is required." % (x, virtual))
            return (virtual, x)

        self.sections["transfers"]["shared"] = [_convert_to_virtual(x) for x in self.sections["transfers"]["shared"]]
        self.sections["transfers"]["buddyshared"] = [_convert_to_virtual(x) for x in self.sections["transfers"]["buddyshared"]]

        sharedfiles = None
        bsharedfiles = None
        sharedfilesstreams = None
        bsharedfilesstreams = None
        wordindex = None
        bwordindex = None
        fileindex = None
        bfileindex = None
        sharedmtimes = None
        bsharedmtimes = None

        shelves = [
            os.path.join(self.data_dir, "files.db"),
            os.path.join(self.data_dir, "buddyfiles.db"),
            os.path.join(self.data_dir, "streams.db"),
            os.path.join(self.data_dir, "buddystreams.db"),
            os.path.join(self.data_dir, "wordindex.db"),
            os.path.join(self.data_dir, "buddywordindex.db"),
            os.path.join(self.data_dir, "fileindex.db"),
            os.path.join(self.data_dir, "buddyfileindex.db"),
            os.path.join(self.data_dir, "mtimes.db"),
            os.path.join(self.data_dir, "buddymtimes.db")
        ]

        _opened_shelves = []
        _errors = []
        for shelvefile in shelves:
            try:
                _opened_shelves.append(shelve.open(shelvefile, protocol=pickle.HIGHEST_PROTOCOL))
            except Exception:
                _errors.append(shelvefile)
                try:
                    os.unlink(shelvefile)
                    _opened_shelves.append(shelve.open(shelvefile, flag='n', protocol=pickle.HIGHEST_PROTOCOL))
                except Exception as ex:
                    print(("Failed to unlink %s: %s" % (shelvefile, ex)))

        sharedfiles = _opened_shelves.pop(0)
        bsharedfiles = _opened_shelves.pop(0)
        sharedfilesstreams = _opened_shelves.pop(0)
        bsharedfilesstreams = _opened_shelves.pop(0)
        wordindex = _opened_shelves.pop(0)
        bwordindex = _opened_shelves.pop(0)
        fileindex = _opened_shelves.pop(0)
        bfileindex = _opened_shelves.pop(0)
        sharedmtimes = _opened_shelves.pop(0)
        bsharedmtimes = _opened_shelves.pop(0)

        if _errors:
            log.addwarning(_("Failed to process the following databases: %(names)s") % {'names': '\n'.join(_errors)})

            files = self.clearShares(
                sharedfiles, bsharedfiles, sharedfilesstreams, bsharedfilesstreams,
                wordindex, bwordindex, fileindex, bfileindex, sharedmtimes, bsharedmtimes
            )

            if files is not None:
                sharedfiles, bsharedfiles, sharedfilesstreams, bsharedfilesstreams, wordindex, bwordindex, fileindex, bfileindex, sharedmtimes, bsharedmtimes = files

            log.addwarning(_("Shared files database seems to be corrupted, rescan your shares"))

        self.sections["transfers"]["sharedfiles"] = sharedfiles
        self.sections["transfers"]["sharedfilesstreams"] = sharedfilesstreams
        self.sections["transfers"]["wordindex"] = wordindex
        self.sections["transfers"]["fileindex"] = fileindex
        self.sections["transfers"]["sharedmtimes"] = sharedmtimes

        self.sections["transfers"]["bsharedfiles"] = bsharedfiles
        self.sections["transfers"]["bsharedfilesstreams"] = bsharedfilesstreams
        self.sections["transfers"]["bwordindex"] = bwordindex
        self.sections["transfers"]["bfileindex"] = bfileindex
        self.sections["transfers"]["bsharedmtimes"] = bsharedmtimes

        # Setting the port range in numerical order
        self.sections["server"]["portrange"] = (min(self.sections["server"]["portrange"]), max(self.sections["server"]["portrange"]))

        self.config_lock.release()