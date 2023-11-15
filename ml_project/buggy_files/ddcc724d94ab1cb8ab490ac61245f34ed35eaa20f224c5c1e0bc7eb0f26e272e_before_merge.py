  def Layout(self, request, response):
    """Render the toolbar."""
    self.ParseRequest(request)

    try:
      client_id = rdfvalue.RDFURN(self.aff4_path).Split(2)[0]
      update_flow_urn = flow.GRRFlow.StartFlow(
          client_id=client_id,
          flow_name="UpdateVFSFile",
          token=request.token,
          vfs_file_urn=rdfvalue.RDFURN(self.aff4_path),
          attribute=self.attribute_to_refresh)

      update_flow = aff4.FACTORY.Open(update_flow_urn,
                                      aff4_type="UpdateVFSFile",
                                      token=request.token)
      self.flow_urn = str(update_flow.state.get_file_flow_urn)
    except IOError as e:
      raise IOError("Sorry. This path cannot be refreshed due to %s" % e)

    if self.flow_urn:
      response = super(UpdateAttribute, self).Layout(request, response)
      return self.CallJavascript(response,
                                 "UpdateAttribute.Layout",
                                 aff4_path=self.aff4_path,
                                 flow_urn=self.flow_urn,
                                 attribute_to_refresh=self.attribute_to_refresh,
                                 poll_time=self.poll_time)