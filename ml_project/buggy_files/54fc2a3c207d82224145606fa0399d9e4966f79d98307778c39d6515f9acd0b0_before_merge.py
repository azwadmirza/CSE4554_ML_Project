    def create_flash(self):
        """! @brief Instantiates flash objects for memory regions.
        
        This init task iterates over flash memory regions and for each one creates the Flash
        instance. It uses the flash_algo and flash_class properties of the region to know how
        to construct the flash object.
        """
        for region in self.memory_map.get_regions_of_type(MemoryType.FLASH):
            # If a path to an FLM file was set on the region, examine it first.
            if region.flm is not None:
                flmPath = self.session.find_user_file(None, [region.flm])
                if flmPath is not None:
                    logging.info("creating flash algo from: %s", flmPath)
                    packAlgo = PackFlashAlgo(flmPath)
                    algo = packAlgo.get_pyocd_flash_algo(
                            max(s[1] for s in packAlgo.sector_sizes),
                            self.memory_map.get_first_region_of_type(MemoryType.RAM))
                
                    # If we got a valid algo from the FLM, set it on the region. This will then
                    # be used below.
                    if algo is not None:
                        region.algo = algo
                else:
                    logging.warning("Failed to find FLM file: %s", region.flm)
            
            # If the constructor of the region's flash class takes the flash_algo arg, then we
            # need the region to have a flash algo dict to pass to it. Otherwise we assume the
            # algo is built-in.
            klass = region.flash_class
            argspec = getargspec(klass.__init__)
            if 'flash_algo' in argspec.args:
                if region.algo is not None:
                    obj = klass(self, region.algo)
                else:
                    logging.warning("flash region '%s' has no flash algo" % region.name)
                    continue
            else:
                obj = klass(self)
            
            # Set the region in the flash instance.
            obj.region = region
            
            # Store the flash object back into the memory region.
            region.flash = obj