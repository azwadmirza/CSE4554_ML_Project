    def _convert_ebook_format(self):
        error_message = None
        doLock = threading.Lock()
        doLock.acquire()
        index = self.current
        doLock.release()
        file_path = self.queue[index]['file_path']
        bookid = self.queue[index]['bookid']
        format_old_ext = u'.' + self.queue[index]['settings']['old_book_format'].lower()
        format_new_ext = u'.' + self.queue[index]['settings']['new_book_format'].lower()

        # check to see if destination format already exists -
        # if it does - mark the conversion task as complete and return a success
        # this will allow send to kindle workflow to continue to work
        if os.path.isfile(file_path + format_new_ext):
            log.info("Book id %d already converted to %s", bookid, format_new_ext)
            cur_book = db.session.query(db.Books).filter(db.Books.id == bookid).first()
            self.queue[index]['path'] = file_path
            self.queue[index]['title'] = cur_book.title
            self._handleSuccess()
            return file_path + format_new_ext
        else:
            log.info("Book id %d - target format of %s does not exist. Moving forward with convert.", bookid, format_new_ext)

        # check if converter-executable is existing
        if not os.path.exists(config.config_converterpath):
            # ToDo Text is not translated
            self._handleError(u"Convertertool %s not found" % config.config_converterpath)
            return

        try:
            # check which converter to use kindlegen is "1"
            if format_old_ext == '.epub' and format_new_ext == '.mobi':
                if config.config_ebookconverter == 1:
                    '''if os.name == 'nt':
                        command = config.config_converterpath + u' "' + file_path + u'.epub"'
                        if sys.version_info < (3, 0):
                            command = command.encode(sys.getfilesystemencoding())
                    else:'''
                    command = [config.config_converterpath, file_path + u'.epub']
                    quotes = [1]
            if config.config_ebookconverter == 2:
                # Linux py2.7 encode as list without quotes no empty element for parameters
                # linux py3.x no encode and as list without quotes no empty element for parameters
                # windows py2.7 encode as string with quotes empty element for parameters is okay
                # windows py 3.x no encode and as string with quotes empty element for parameters is okay
                # separate handling for windows and linux
                quotes = [1,2]
                '''if os.name == 'nt':
                    command = config.config_converterpath + u' "' + file_path + format_old_ext + u'" "' + \
                              file_path + format_new_ext + u'" ' + config.config_calibre
                    if sys.version_info < (3, 0):
                        command = command.encode(sys.getfilesystemencoding())
                else:'''
                command = [config.config_converterpath, (file_path + format_old_ext),
                    (file_path + format_new_ext)]
                quotes_index = 3
                if config.config_calibre:
                    parameters = config.config_calibre.split(" ")
                    for param in parameters:
                        command.append(param)
                        quotes.append(quotes_index)
                        quotes_index += 1
            p = process_open(command, quotes)
            # p = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
        except OSError as e:
            self._handleError(_(u"Ebook-converter failed: %(error)s", error=e))
            return

        if config.config_ebookconverter == 1:
            nextline = p.communicate()[0]
            # Format of error message (kindlegen translates its output texts):
            # Error(prcgen):E23006: Language not recognized in metadata.The dc:Language field is mandatory.Aborting.
            conv_error = re.search(r".*\(.*\):(E\d+):\s(.*)", nextline, re.MULTILINE)
            # If error occoures, store error message for logfile
            if conv_error:
                error_message = _(u"Kindlegen failed with Error %(error)s. Message: %(message)s",
                                  error=conv_error.group(1), message=conv_error.group(2).strip())
            log.debug("convert_kindlegen: %s", nextline)
        else:
            while p.poll() is None:
                nextline = p.stdout.readline()
                if os.name == 'nt' and sys.version_info < (3, 0):
                    nextline = nextline.decode('windows-1252')
                elif os.name == 'posix' and sys.version_info < (3, 0):
                    nextline = nextline.decode('utf-8')
                log.debug(nextline.strip('\r\n'))
                # parse progress string from calibre-converter
                progress = re.search(r"(\d+)%\s.*", nextline)
                if progress:
                    self.UIqueue[index]['progress'] = progress.group(1) + ' %'

        # process returncode
        check = p.returncode
        calibre_traceback = p.stderr.readlines()
        for ele in calibre_traceback:
            if sys.version_info < (3, 0):
                ele = ele.decode('utf-8')
            log.debug(ele.strip('\n'))
            if not ele.startswith('Traceback') and not ele.startswith('  File'):
                error_message = "Calibre failed with error: %s" % ele.strip('\n')

        # kindlegen returncodes
        # 0 = Info(prcgen):I1036: Mobi file built successfully
        # 1 = Info(prcgen):I1037: Mobi file built with WARNINGS!
        # 2 = Info(prcgen):I1038: MOBI file could not be generated because of errors!
        if (check < 2 and config.config_ebookconverter == 1) or \
            (check == 0 and config.config_ebookconverter == 2):
            cur_book = db.session.query(db.Books).filter(db.Books.id == bookid).first()
            if os.path.isfile(file_path + format_new_ext):
                new_format = db.Data(name=cur_book.data[0].name,
                                         book_format=self.queue[index]['settings']['new_book_format'].upper(),
                                         book=bookid, uncompressed_size=os.path.getsize(file_path + format_new_ext))
                cur_book.data.append(new_format)
                db.session.commit()
                self.queue[index]['path'] = cur_book.path
                self.queue[index]['title'] = cur_book.title
                if config.config_use_google_drive:
                    os.remove(file_path + format_old_ext)
                self._handleSuccess()
                return file_path + format_new_ext
            else:
                error_message = format_new_ext.upper() + ' format not found on disk'
        log.info("ebook converter failed with error while converting book")
        if not error_message:
            error_message = 'Ebook converter failed with unknown error'
        self._handleError(error_message)
        return