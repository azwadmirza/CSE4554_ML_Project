    async def schedule_segment(
            self,
            parent_header: BlockHeader,
            gap_length: int,
            skeleton_peer: TChainPeer) -> None:
        """
        :param parent_header: the parent of the gap to fill
        :param gap_length: how long is the header gap
        :param skeleton_peer: the peer that provided the parent_header - will not use to fill gaps
        """
        await self.wait(self._filler_header_tasks.add((
            (parent_header, gap_length, skeleton_peer),
        )))