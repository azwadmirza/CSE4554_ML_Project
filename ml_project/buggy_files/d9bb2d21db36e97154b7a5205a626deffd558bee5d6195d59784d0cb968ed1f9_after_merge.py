  def BuildTable(self, start_row, end_row, request):
    """Renders the table."""
    depth = request.REQ.get("depth", 0)

    flow_urn = self.state.get("value", request.REQ.get("value"))
    if flow_urn is None:
      client_id = request.REQ.get("client_id")
      if not client_id:
        return

      flow_urn = rdf_client.ClientURN(client_id).Add("flows")

    flow_root = aff4.FACTORY.Open(flow_urn, mode="r", token=request.token)
    root_children_paths = sorted(flow_root.ListChildren(),
                                 key=lambda x: x.age,
                                 reverse=True)
    additional_rows = (depth == 0 and len(root_children_paths) > end_row)

    if not depth:
      root_children_paths = root_children_paths[start_row:end_row]

    # TODO(user): should be able to specify aff4_type=flow.GRRFlow
    # here.  Currently this doesn't work because symlinks get filtered out.
    # This is an aff4.FACTORY.MultiOpen's bug.
    root_children = aff4.FACTORY.MultiOpen(root_children_paths,
                                           token=request.token)
    root_children = sorted(root_children,
                           key=self._GetCreationTime,
                           reverse=True)
    level2_children = dict(aff4.FACTORY.MultiListChildren(
        [f.urn for f in root_children],
        token=request.token))

    self.size = len(root_children)

    row_index = start_row
    for flow_obj in root_children:
      if level2_children.get(flow_obj.urn, None):
        row_type = "branch"
      else:
        row_type = "leaf"

      row = {}
      last = flow_obj.Get(flow_obj.Schema.LAST)
      if last:
        row["Last Active"] = last

      if isinstance(flow_obj, flow.GRRFlow):
        row_name = (flow_obj.symlink_urn or flow_obj.urn).Basename()
        try:
          if flow_obj.Get(flow_obj.Schema.CLIENT_CRASH):
            row["State"] = "CLIENT_CRASHED"
          else:
            row["State"] = flow_obj.state.context.state

          row["Flow Name"] = flow_obj.state.context.args.flow_name
          row["Creation Time"] = flow_obj.state.context.create_time
          row["Creator"] = flow_obj.state.context.creator
        except AttributeError:
          row["Flow Name"] = "Failed to open flow."

      elif isinstance(flow_obj, hunts.GRRHunt):
        row_name = flow_obj.urn.Dirname()
        row["Flow Name"] = "Hunt"

      else:
        # A logs collection, skip, it will be rendered separately
        continue

      self.columns[1].AddElement(
          # If flow object is symlinked, we want to use symlink path in the
          # table. This way UI logic can make reasonable assumptions about
          # client's flows URNs.
          row_index,
          flow_obj.symlink_urn or flow_obj.urn,
          depth,
          row_type,
          row_name)

      self.AddRow(row, row_index)
      row_index += 1

    return additional_rows