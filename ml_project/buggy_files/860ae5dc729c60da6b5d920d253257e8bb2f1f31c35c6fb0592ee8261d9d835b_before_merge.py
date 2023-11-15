  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a PCAP file-like object.

    Args:
      parser_mediator: A parser mediator object (instance of ParserMediator).
      file_object: A file-like object.

    Raises:
      UnableToParseFile: when the file cannot be parsed.
    """
    data = file_object.read(dpkt.pcap.FileHdr.__hdr_len__)

    try:
      file_header = dpkt.pcap.FileHdr(data)
      packet_header_class = dpkt.pcap.PktHdr

    except (dpkt.NeedData, dpkt.UnpackError) as exception:
      raise errors.UnableToParseFile(
          u'[{0:s}] unable to parse file: {1:s} with error: {2:s}'.format(
              self.NAME, parser_mediator.GetDisplayName(), exception))

    if file_header.magic == dpkt.pcap.PMUDPCT_MAGIC:
      try:
        file_header = dpkt.pcap.LEFileHdr(data)
        packet_header_class = dpkt.pcap.LEPktHdr

      except (dpkt.NeedData, dpkt.UnpackError) as exception:
        raise errors.UnableToParseFile(
            u'[{0:s}] unable to parse file: {1:s} with error: {2:s}'.format(
                self.NAME, parser_mediator.GetDisplayName(), exception))

    elif file_header.magic != dpkt.pcap.TCPDUMP_MAGIC:
      raise errors.UnableToParseFile(u'Unsupported file signature')

    packet_number = 1
    connections = {}
    other_list = []
    trunc_list = []

    data = file_object.read(dpkt.pcap.PktHdr.__hdr_len__)
    while data:
      packet_header = packet_header_class(data)
      timestamp = packet_header.tv_sec + (packet_header.tv_usec / 1000000.0)
      packet_data = file_object.read(packet_header.caplen)

      ethernet_frame = dpkt.ethernet.Ethernet(packet_data)

      if ethernet_frame.type == dpkt.ethernet.ETH_TYPE_IP:
        self._ParseIPPacket(
            connections, trunc_list, packet_number, timestamp,
            len(ethernet_frame), ethernet_frame.data)

      else:
        packet_values = [
            timestamp, packet_number, ethernet_frame, len(ethernet_frame)]
        other_list.append(packet_values)

      packet_number += 1
      data = file_object.read(dpkt.pcap.PktHdr.__hdr_len__)

    other_streams = self._ParseOtherStreams(other_list, trunc_list)

    for stream_object in sorted(
        connections.values(), key=operator.attrgetter(u'start_time')):

      if not stream_object.protocol == u'ICMP':
        stream_object.Clean()

      event_objects = [
          PcapEvent(
              min(stream_object.timestamps),
              eventdata.EventTimestamp.START_TIME, stream_object),
          PcapEvent(
              max(stream_object.timestamps),
              eventdata.EventTimestamp.END_TIME, stream_object)]

      parser_mediator.ProduceEvents(event_objects)

    for stream_object in other_streams:
      event_objects = [
          PcapEvent(
              min(stream_object.timestamps),
              eventdata.EventTimestamp.START_TIME, stream_object),
          PcapEvent(
              max(stream_object.timestamps),
              eventdata.EventTimestamp.END_TIME, stream_object)]
      parser_mediator.ProduceEvents(event_objects)