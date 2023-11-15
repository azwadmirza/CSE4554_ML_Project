    def WriteInfo(self, filename):
        info = None
        try:
            # Issue #421 ensure subdir exists.
            PixivHelper.makeSubdirs(filename)

            info = codecs.open(filename, 'wb', encoding='utf-8')
        except IOError:
            info = codecs.open(str(self.imageId) + ".txt", 'wb', encoding='utf-8')
            PixivHelper.GetLogger().exception("Error when saving image info: {0}, file is saved to: {1}.txt".format(filename, self.imageId))

        info.write(u"ArtistID      = {0}\r\n".format(self.parent.artistId))
        info.write(u"ArtistName    = {0}\r\n".format(self.parent.artistName))

        info.write(u"ImageID       = {0}\r\n".format(self.imageId))
        info.write(u"Title         = {0}\r\n".format(self.imageTitle))
        info.write(u"Caption       = {0}\r\n".format(self.body_text))
        # info.write(u"Tags          = " + ", ".join(self.imageTags) + "\r\n")
        if self.is_restricted:
            info.write(u"Image Mode    = {0}, Restricted\r\n".format(self.type))
        else:
            info.write(u"Image Mode    = {0}\r\n".format(self.type))
        info.write(u"Pages         = {0}\r\n".format(self.imageCount))
        info.write(u"Date          = {0}\r\n".format(self.worksDate))
        # info.write(u"Resolution    = " + self.worksResolution + "\r\n")
        # info.write(u"Tools         = " + self.worksTools + "\r\n")
        info.write(u"Like Count    = {0}\r\n".format(self.likeCount))
        info.write(u"Link          = https://www.pixiv.net/fanbox/creator/{0}/post/{1}\r\n".format(self.parent.artistId, self.imageId))
        # info.write("Ugoira Data   = " + str(self.ugoira_data) + "\r\n")
        if len(self.embeddedFiles) > 0:
            info.write("Urls          =\r\n")
            for link in self.embeddedFiles:
                info.write(" - {0}\r\n".format(link))
        info.close()