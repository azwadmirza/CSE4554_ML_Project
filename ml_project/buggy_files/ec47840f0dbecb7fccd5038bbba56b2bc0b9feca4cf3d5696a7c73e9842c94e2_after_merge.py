    def program(self, chip_erase=None, progress_cb=None, smart_flash=True, fast_verify=False, keep_unwritten=True):
        """! @brief Determine fastest method of flashing and then run flash programming.

        Data must have already been added with add_data().
        
        @param self
        @param chip_erase A value of True forces chip erase, False forces sector erase, and a
            value of None means that the estimated fastest method should be used.
        @param progress_cb A callable that accepts a single parameter of the percentage complete.
        @param smart_flash If True, FlashBuilder will scan target memory to attempt to avoid
            programming contents that are not changing with this program request. False forces
            all requested data to be programmed.
        @param fast_verify If smart_flash is enabled and the target supports the CRC32 analyzer,
            this parameter controls whether positive results from the analyzer will be accepted.
            In other words, pages with matching CRCs will be marked as the same. There is a small,
            but non-zero, chance that the CRCs match even though the data is different, but the
            odds of this happing are low: ~1/(2^32) = ~2.33*10^-8%.
        @param keep_unwritten Depending on the sector versus page size and the amount of data
            written, there may be ranges of flash that would be erased but not written with new
            data. This parameter sets whether the existing contents of those unwritten ranges will
            be read from memory and restored while programming.
        """

        # Send notification that we're about to program flash.
        self.flash.target.notify(Notification(event=Target.EVENT_PRE_FLASH_PROGRAM, source=self))

        # Examples
        # - lpc4330     -Non 0 base address
        # - nRF51       -UICR location far from flash (address 0x10001000)
        # - LPC1768     -Different sized pages
        program_start = time()

        if progress_cb is None:
            progress_cb = _stub_progress

        # There must be at least 1 flash operation
        if len(self.flash_operation_list) == 0:
            LOG.warning("No pages were programmed")
            return

        # Convert the list of flash operations into flash sectors and pages
        self._build_sectors_and_pages(keep_unwritten)
        assert len(self.sector_list) != 0 and len(self.sector_list[0].page_list) != 0
        self.flash_operation_list = None # Don't need this data in memory anymore.
        
        # If smart flash was set to false then mark all pages
        # as requiring programming
        if not smart_flash:
            self._mark_all_pages_for_programming()
        
        # If the flash algo doesn't support erase all, disable chip erase.
        if not self.flash.is_erase_all_supported:
            chip_erase = False

        # If the first page being programmed is not the first page
        # in flash then don't use a chip erase unless explicitly directed to.
        if self.page_list[0].addr > self.flash_start:
            if chip_erase is None:
                chip_erase = False
            elif chip_erase is True:
                LOG.warning('Chip erase used when flash address 0x%x is not the same as flash start 0x%x',
                    self.page_list[0].addr, self.flash_start)

        chip_erase_count, chip_erase_program_time = self._compute_chip_erase_pages_and_weight()
        sector_erase_min_program_time = self._compute_sector_erase_pages_weight_min()

        # If chip_erase hasn't been specified determine if chip erase is faster
        # than page erase regardless of contents
        if (chip_erase is None) and (chip_erase_program_time < sector_erase_min_program_time):
            chip_erase = True

        # If chip erase isn't True then analyze the flash
        if chip_erase is not True:
            sector_erase_count, page_program_time = self._compute_sector_erase_pages_and_weight(fast_verify)

        # If chip erase hasn't been set then determine fastest method to program
        if chip_erase is None:
            LOG.debug("Chip erase count %i, sector erase est count %i" % (chip_erase_count, sector_erase_count))
            LOG.debug("Chip erase weight %f, sector erase weight %f" % (chip_erase_program_time, page_program_time))
            chip_erase = chip_erase_program_time < page_program_time

        if chip_erase:
            if self.flash.is_double_buffering_supported and self.enable_double_buffering:
                LOG.debug("Using double buffer chip erase program")
                flash_operation = self._chip_erase_program_double_buffer(progress_cb)
            else:
                flash_operation = self._chip_erase_program(progress_cb)
        else:
            if self.flash.is_double_buffering_supported and self.enable_double_buffering:
                LOG.debug("Using double buffer sector erase program")
                flash_operation = self._sector_erase_program_double_buffer(progress_cb)
            else:
                flash_operation = self._sector_erase_program(progress_cb)

        # Cleanup flash algo and reset target after programming.
        self.flash.cleanup()
        self.flash.target.reset_and_halt()

        program_finish = time()
        self.perf.program_time = program_finish - program_start
        self.perf.program_type = flash_operation

        erase_byte_count = 0
        erase_sector_count = 0
        actual_program_byte_count = 0
        actual_program_page_count = 0
        skipped_byte_count = 0
        skipped_page_count = 0
        for page in self.page_list:
            if (page.same is True) or (page.erased and chip_erase):
                skipped_byte_count += page.size
                skipped_page_count += 1
            else:
                actual_program_byte_count += page.size
                actual_program_page_count += 1
        for sector in self.sector_list:
            if sector.are_any_pages_not_same():
                erase_byte_count += sector.size
                erase_sector_count += 1
        
        self.perf.total_byte_count = self.program_byte_count
        self.perf.program_byte_count = actual_program_byte_count
        self.perf.program_page_count = actual_program_page_count
        self.perf.erase_byte_count = erase_byte_count
        self.perf.erase_sector_count = erase_sector_count
        self.perf.skipped_byte_count = skipped_byte_count
        self.perf.skipped_page_count = skipped_page_count
        
        if self.log_performance:
            if chip_erase:
                LOG.info("Erased chip, programmed %d bytes (%s), skipped %d bytes (%s) at %.02f kB/s",
                    actual_program_byte_count, get_page_count(actual_program_page_count),
                    skipped_byte_count, get_page_count(skipped_page_count),
                    ((self.program_byte_count/1024) / self.perf.program_time))
            else:
                LOG.info("Erased %d bytes (%s), programmed %d bytes (%s), skipped %d bytes (%s) at %.02f kB/s", 
                    erase_byte_count, get_sector_count(erase_sector_count),
                    actual_program_byte_count, get_page_count(actual_program_page_count),
                    skipped_byte_count, get_page_count(skipped_page_count),
                    ((self.program_byte_count/1024) / self.perf.program_time))

        # Send notification that we're done programming flash.
        self.flash.target.notify(Notification(event=Target.EVENT_POST_FLASH_PROGRAM, source=self))

        return self.perf