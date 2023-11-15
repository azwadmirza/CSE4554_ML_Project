    def periodic_read(self):
        _log.debug("scraping device: " + self.device_name)
        
        try:
            results = self.interface.scrape_all()
        except Exception as ex:
            _log.exception(ex)
            return
        
        # XXX: Does a warning need to be printed?
        if not results:
            return

        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
        
        headers = {
            headers_mod.DATE: now,
        }
            

        for point, value in results.iteritems():
            topics = self.get_paths_for_point(point)
            for topic in topics:
                message = [value, self.meta_data[point]] 
                self.vip.pubsub.publish('pubsub', topic, 
                                        headers=headers, 
                                        message=message)
         
        message = [results, self.meta_data] 
        self.vip.pubsub.publish('pubsub', 
                                self.all_path_depth, 
                                headers=headers, 
                                message=message)
         
        self.vip.pubsub.publish('pubsub', 
                                self.all_path_breadth, 
                                headers=headers, 
                                message=message)