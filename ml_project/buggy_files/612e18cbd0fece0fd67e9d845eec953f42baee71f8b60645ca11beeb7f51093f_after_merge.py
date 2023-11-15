    def save_attribs(self):
        """ Save specific attributes for Retry """
        attribs = {}
        for attrib in NzoAttributeSaver:
            attribs[attrib] = getattr(self, attrib)
        logging.debug("Saving attributes %s for %s", attribs, self.final_name)
        sabnzbd.save_data(attribs, ATTRIB_FILE, self.workpath)