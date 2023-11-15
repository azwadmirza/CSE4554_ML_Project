    def _sector_erase(self, addresses):
        flash = None
        currentRegion = None

        for spec in addresses:
            # Convert the spec into a start and end address.
            page_addr, end_addr = self._convert_spec(spec)
            
            while page_addr < end_addr:
                # Look up the flash memory region for the current address.
                region = self._session.target.memory_map.get_region_for_address(page_addr)
                if region is None:
                    LOG.warning("address 0x%08x is not within a memory region", page_addr)
                    break
                if not region.is_flash:
                    LOG.warning("address 0x%08x is not in flash", page_addr)
                    break
            
                # Handle switching regions.
                if region is not currentRegion:
                    # Clean up previous flash.
                    if flash is not None:
                        flash.cleanup()
                
                    currentRegion = region
                    flash = region.flash
                    flash.init(flash.Operation.ERASE)
        
                # Get page info for the current address.
                page_info = flash.get_page_info(page_addr)
                if not page_info:
                    # Should not fail to get page info within a flash region.
                    raise RuntimeError("sector address 0x%08x within flash region '%s' is invalid" % (page_addr, region.name))
                
                # Align first page address.
                delta = page_addr % page_info.size
                if delta:
                    LOG.warning("sector address 0x%08x is unaligned", page_addr)
                    page_addr -= delta
        
                # Erase this page.
                LOG.info("Erasing sector 0x%08x (%d bytes)", page_addr, page_info.size)
                flash.erase_sector(page_addr)
                
                page_addr += page_info.size

        if flash is not None:
            flash.cleanup()