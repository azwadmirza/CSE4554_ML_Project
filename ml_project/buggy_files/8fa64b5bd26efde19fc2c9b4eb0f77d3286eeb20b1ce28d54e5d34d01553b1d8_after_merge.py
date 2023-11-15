    def _build_flash_regions(self):
        """! @brief Converts ROM memory regions to flash regions.
        
        Each ROM region in the `_regions` attribute is converted to a flash region if a matching
        flash algo can be found. If the flash has multiple sector sizes, then separate flash
        regions will be created for each sector size range. The flash algo is converted to a
        pyOCD-compatible flash algo dict by calling _get_pyocd_flash_algo().
        """
        # Must have a default ram.
        if self._default_ram is None:
            LOG.warning("CMSIS-Pack device %s has no default RAM defined, cannot program flash" % self.part_number)
            return
        
        # Create flash algo dicts once we have the full memory map.
        for i, region in enumerate(self._regions):
            # We're only interested in ROM regions here.
            if region.type != MemoryType.ROM:
                continue
            
            # Look for matching flash algo.
            algo = self._find_matching_algo(region)
            if algo is None:
                # Must be a mask ROM or non-programmable flash.
                continue

            # Remove the ROM region that we'll replace with flash region(s).
            del self._regions[i]

            # Load flash algo from .FLM file.
            algoData = self.pack.get_file(algo.attrib['name'])
            packAlgo = PackFlashAlgo(algoData)
            
            # Log details of this flash algo if the debug option is enabled.
            current_session = core.session.Session.get_current()
            if current_session and current_session.options.get("debug.log_flm_info", False):
                LOG.debug("Flash algo info: %s", packAlgo.flash_info)
            
            # Choose the page size. The check for <=32 is to handle some flash algos with incorrect
            # page sizes that are too small and probably represent the phrase size.
            page_size = packAlgo.page_size
            if page_size <= 32:
                page_size = min(s[1] for s in packAlgo.sector_sizes)
            
            # Construct the pyOCD algo using the largest sector size. We can share the same
            # algo for all sector sizes.
            algo = packAlgo.get_pyocd_flash_algo(page_size, self._default_ram)

            # Create a separate flash region for each sector size range.
            for i, sectorInfo in enumerate(packAlgo.sector_sizes):
                start, sector_size = sectorInfo
                if i + 1 >= len(packAlgo.sector_sizes):
                    nextStart = region.length
                else:
                    nextStart, _ = packAlgo.sector_sizes[i + 1]
                
                length = nextStart - start
                start += region.start
                
                # If we don't have a boot memory yet, pick the first flash.
                if not self._saw_startup:
                    isBoot = True
                    self._saw_startup = True
                else:
                    isBoot = region.is_boot_memory
                
                # Construct the flash region.
                rangeRegion = FlashRegion(name=region.name,
                                access=region.access,
                                start=start,
                                length=length,
                                sector_size=sector_size,
                                page_size=page_size,
                                flm=packAlgo,
                                algo=algo,
                                erased_byte_value=packAlgo.flash_info.value_empty,
                                is_default=region.is_default,
                                is_boot_memory=isBoot,
                                is_testable=region.is_testable,
                                alias=region.alias)
                self._regions.append(rangeRegion)