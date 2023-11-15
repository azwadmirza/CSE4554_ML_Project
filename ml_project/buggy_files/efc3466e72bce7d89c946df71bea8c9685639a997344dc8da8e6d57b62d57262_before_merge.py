    def writeConfig(self, error=False, path=None):
        '''Backup old config if exist and write updated config.ini'''
        print('Writing config file...', end=' ')
        config = configparser.RawConfigParser()

        config.add_section('Network')
        config.set('Network', 'useProxy', self.useProxy)
        config.set('Network', 'proxyAddress', self.proxyAddress)
        config.set('Network', 'useragent', self.useragent)
        config.set('Network', 'useRobots', self.useRobots)
        config.set('Network', 'timeout', self.timeout)
        config.set('Network', 'retry', self.retry)
        config.set('Network', 'retrywait', self.retryWait)
        config.set('Network', 'downloadDelay', self.downloadDelay)
        config.set('Network', 'checkNewVersion', self.checkNewVersion)
        config.set('Network', 'enableSSLVerification', self.enableSSLVerification)

        config.add_section('Debug')
        config.set('Debug', 'logLevel', self.logLevel)
        config.set('Debug', 'enableDump', self.enableDump)
        config.set('Debug', 'skipDumpFilter', self.skipDumpFilter)
        config.set('Debug', 'dumpMediumPage', self.dumpMediumPage)
        config.set('Debug', 'dumpTagSearchPage', self.dumpTagSearchPage)
        config.set('Debug', 'debugHttp', self.debugHttp)

        config.add_section('IrfanView')
        config.set('IrfanView', 'IrfanViewPath', self.IrfanViewPath)
        config.set('IrfanView', 'startIrfanView', self.startIrfanView)
        config.set('IrfanView', 'startIrfanSlide', self.startIrfanSlide)
        config.set('IrfanView', 'createDownloadLists', self.createDownloadLists)

        config.add_section('Settings')
        config.set('Settings', 'downloadListDirectory', self.downloadListDirectory)
        config.set('Settings', 'useList', self.useList)
        config.set('Settings', 'processFromDb', self.processFromDb)
        config.set('Settings', 'overwrite', self.overwrite)
        config.set('Settings', 'daylastupdated', self.dayLastUpdated)
        config.set('Settings', 'rootdirectory', self.rootDirectory)
        config.set('Settings', 'alwaysCheckFileSize', self.alwaysCheckFileSize)
        config.set('Settings', 'checkUpdatedLimit', self.checkUpdatedLimit)
        config.set('Settings', 'downloadAvatar', self.downloadAvatar)
        config.set('Settings', 'useBlacklistTags', self.useBlacklistTags)
        config.set('Settings', 'useSuppressTags', self.useSuppressTags)
        config.set('Settings', 'tagsLimit', self.tagsLimit)
        config.set('Settings', 'writeImageInfo', self.writeImageInfo)
        config.set('Settings', 'writeImageJSON', self.writeImageJSON)
        config.set('Settings', 'dateDiff', self.dateDiff)
        config.set('Settings', 'backupOldFile', self.backupOldFile)
        config.set('Settings', 'enableInfiniteLoop', self.enableInfiniteLoop)
        config.set('Settings', 'verifyImage', self.verifyImage)
        config.set('Settings', 'writeUrlInDescription', self.writeUrlInDescription)
        config.set('Settings', 'urlBlacklistRegex', self.urlBlacklistRegex)
        config.set('Settings', 'dbPath', self.dbPath)
        config.set('Settings', 'useBlacklistMembers', self.useBlacklistMembers)
        config.set('Settings', 'setLastModified', self.setLastModified)
        config.set('Settings', 'useLocalTimezone', self.useLocalTimezone)

        config.add_section('Filename')
        config.set('Filename', 'filenameFormat', self.filenameFormat)
        config.set('Filename', 'filenameMangaFormat', self.filenameMangaFormat)
        config.set('Filename', 'filenameInfoFormat', self.filenameInfoFormat)
        config.set('Filename', 'avatarNameFormat', self.avatarNameFormat)
        config.set('Filename', 'tagsSeparator', self.tagsSeparator)
        config.set('Filename', 'createMangaDir', self.createMangaDir)
        config.set('Filename', 'useTagsAsDir', self.useTagsAsDir)
        config.set('Filename', 'urlDumpFilename', self.urlDumpFilename)

        config.add_section('Authentication')
        config.set('Authentication', 'username', self.username)
        config.set('Authentication', 'password', self.password)
        config.set('Authentication', 'cookie', self.cookie)
        config.set('Authentication', 'refresh_token', self.refresh_token)

        config.add_section('Pixiv')
        config.set('Pixiv', 'numberOfPage', self.numberOfPage)
        config.set('Pixiv', 'R18Mode', self.r18mode)
        config.set('Pixiv', 'DateFormat', self.dateFormat)

        config.add_section('FFmpeg')
        config.set('FFmpeg', 'ffmpeg', self.ffmpeg)
        config.set('FFmpeg', 'ffmpegCodec', self.ffmpegCodec)
        config.set('FFmpeg', 'ffmpegParam', self.ffmpegParam)
        config.set('FFmpeg', 'webpCodec', self.webpCodec)
        config.set('FFmpeg', 'webpParam', self.webpParam)

        config.add_section('Ugoira')
        config.set('Ugoira', 'writeUgoiraInfo', self.writeUgoiraInfo)
        config.set('Ugoira', 'createUgoira', self.createUgoira)
        config.set('Ugoira', 'deleteZipFile', self.deleteZipFile)
        config.set('Ugoira', 'createGif', self.createGif)
        config.set('Ugoira', 'createApng', self.createApng)
        config.set('Ugoira', 'deleteUgoira', self.deleteUgoira)
        config.set('Ugoira', 'createWebm', self.createWebm)
        config.set('Ugoira', 'createWebp', self.createWebp)

        if path is not None:
            configlocation = path
        else:
            configlocation = 'config.ini'

        try:
            # with codecs.open('config.ini.bak', encoding = 'utf-8', mode = 'wb') as configfile:
            with open(configlocation + '.tmp', 'w') as configfile:
                config.write(configfile)
            if os.path.exists(configlocation):
                if error:
                    backupName = configlocation + '.error-' + str(int(time.time()))
                    print("Backing up old config (error exist!) to " + backupName)
                    shutil.move(configlocation, backupName)
                else:
                    print("Backing up old config to config.ini.bak")
                    shutil.move(configlocation, configlocation + '.bak')
            os.rename(configlocation + '.tmp', configlocation)
        except BaseException:
            self.__logger.exception('Error at writeConfig()')
            raise

        print('done.')