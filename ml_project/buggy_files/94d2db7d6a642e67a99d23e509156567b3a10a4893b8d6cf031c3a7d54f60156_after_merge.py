    def _sector_erase(self, addresses):
        flash = None
        currentRegion = None

        for spec in addresses:
            # Convert the spec into a start and end address.
            sector_addr, end_addr = self._convert_spec(spec)
            
            while sector_addr < end_addr:
                # Look up the flash memory region for the current address.
                region = self._session.target.memory_map.get_region_for_address(sector_addr)
                if region is None:
                    LOG.warning("address 0x%08x is not within a memory region", sector_addr)
                    break
                if not region.is_flash:
                    LOG.warning("address 0x%08x is not in flash", sector_addr)
                    break
            
                # Handle switching regions.
                if region is not currentRegion:
                    # Clean up previous flash.
                    if flash is not None:
                        flash.cleanup()
                
                    currentRegion = region
                    flash = region.flash
                    flash.init(flash.Operation.ERASE)
        
                # Get sector info for the current address.
                sector_info = flash.get_sector_info(sector_addr)
                if not sector_info:
                    # Should not fail to get sector info within a flash region.
                    raise RuntimeError("sector address 0x%08x within flash region '%s' is invalid" % (sector_addr, region.name))
                
                # Align first page address.
                delta = sector_addr % sector_info.size
                if delta:
                    LOG.warning("sector address 0x%08x is unaligned", sector_addr)
                    sector_addr -= delta
        
                # Erase this page.
                LOG.info("Erasing sector 0x%08x (%d bytes)", sector_addr, sector_info.size)
                flash.erase_sector(sector_addr)
                
                sector_addr += sector_info.size

        if flash is not None:
            flash.cleanup()