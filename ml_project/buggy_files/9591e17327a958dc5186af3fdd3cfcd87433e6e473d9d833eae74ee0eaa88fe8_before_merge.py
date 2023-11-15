    def endElement(self, name):
        if name == 'nmaprun':
            self._curscan = None
        elif name == 'host':
            # masscan -oX output has no "state" tag
            if self._curhost.get('state', 'up') == 'up' and (
                    not self._needports
                    or 'ports' in self._curhost) and (
                        not self._needopenports
                        or self._curhost.get('openports', {}).get('count')):
                if 'openports' not in self._curhost:
                    self._curhost['openports'] = {'count': 0}
                self._pre_addhost()
                self._addhost()
            self._curhost = None
        elif name == 'hostnames':
            self._curhost['hostnames'] = self._curhostnames
            self._curhostnames = None
        elif name == 'extraports':
            self._curhost.setdefault(
                'extraports', {}).update(self._curextraports)
            self._curextraports = None
        elif name == 'port':
            self._curhost.setdefault('ports', []).append(self._curport)
            if self._curport.get("state_state") == 'open':
                openports = self._curhost.setdefault('openports', {})
                openports['count'] = openports.get('count', 0) + 1
                protoopenports = openports.setdefault(
                    self._curport['protocol'], {})
                protoopenports['count'] = protoopenports.get('count', 0) + 1
                protoopenports.setdefault('ports', []).append(
                    self._curport['port'])
            self._curport = None
        elif name == 'script':
            if self._curport is not None:
                current = self._curport
            elif self._curhost is not None:
                current = self._curhost
            else:
                # We do not want to handle script tags outside host or
                # port tags (usually scripts running on prerule /
                # postrule)
                self._curscript = None
                if self._curtablepath:
                    utils.LOGGER.warning("self._curtablepath should be empty, "
                                         "got [%r]", self._curtablepath)
                self._curtable = {}
                return
            if self._curscript['id'] in SCREENSHOTS_SCRIPTS:
                fname = SCREENSHOTS_SCRIPTS[self._curscript['id']](
                    self._curscript
                )
                if fname is not None:
                    exceptions = []
                    for full_fname in [fname,
                                       os.path.join(
                                           os.path.dirname(self._fname),
                                           fname)]:
                        try:
                            with open(full_fname) as fdesc:
                                data = fdesc.read()
                                trim_result = utils.trim_image(data)
                                if trim_result:
                                    # When trim_result is False, the image no
                                    # longer exists after trim
                                    if trim_result is not True:
                                        # Image has been trimmed
                                        data = trim_result
                                    current['screenshot'] = "field"
                                    current['screendata'] = self._to_binary(
                                        data
                                    )
                                    screenwords = utils.screenwords(data)
                                    if screenwords is not None:
                                        current['screenwords'] = screenwords
                        except Exception:
                            exceptions.append((sys.exc_info(), full_fname))
                        else:
                            exceptions = []
                            break
                    for exc_info, full_fname in exceptions:
                        utils.LOGGER.warning(
                            "Screenshot: exception (scanfile %r, file %r)",
                            self._fname, full_fname, exc_info=exc_info,
                        )
            if ignore_script(self._curscript):
                self._curscript = None
                return
            infokey = self._curscript.get('id', None)
            infokey = ALIASES_TABLE_ELEMS.get(infokey, infokey)
            if self._curtable:
                if self._curtablepath:
                    utils.LOGGER.warning("self._curtablepath should be empty, "
                                         "got [%r]", self._curtablepath)
                if infokey in CHANGE_TABLE_ELEMS:
                    self._curtable = CHANGE_TABLE_ELEMS[infokey](self._curtable)
                self._curscript[infokey] = self._curtable
                self._curtable = {}
            elif infokey in ADD_TABLE_ELEMS:
                infos = ADD_TABLE_ELEMS[infokey]
                if isinstance(infos, utils.REGEXP_T):
                    infos = infos.search(self._curscript.get('output', ''))
                    if infos is not None:
                        infosdict = infos.groupdict()
                        if infosdict:
                            self._curscript[infokey] = infosdict
                        else:
                            infos = list(infos.groups())
                            if infos:
                                self._curscript[infokey] = infos
                elif hasattr(infos, "__call__"):
                    infos = infos(self._curscript)
                    if infos is not None:
                        self._curscript[infokey] = infos
            current.setdefault('scripts', []).append(self._curscript)
            self._curscript = None
        elif name in ['table', 'elem']:
            if self._curscript.get('id') in IGNORE_TABLE_ELEMS:
                return
            if name == 'elem':
                lastlevel = self._curtable
                for k in self._curtablepath[:-1]:
                    if k is None:
                        lastlevel = lastlevel[-1]
                    else:
                        lastlevel = lastlevel[k]
                k = self._curtablepath[-1]
                if isinstance(k, int):
                    lastlevel.append(self._curdata)
                else:
                    lastlevel[k] = self._curdata
                if k == 'cpe':
                    self._add_cpe_to_host()
                # stop recording characters
                self._curdata = None
            self._curtablepath.pop()
        elif name == 'hostscript' and 'scripts' in self._curhost:
            # "fake" port element, without a "protocol" key and with the
            # magic value -1 for the "port" key.
            self._curhost.setdefault('ports', []).append({
                "port": -1,
                "scripts": self._curhost.pop('scripts')
            })
        elif name == 'trace':
            self._curhost.setdefault('traces', []).append(self._curtrace)
            self._curtrace = None
        elif name == 'cpe':
            self._add_cpe_to_host()