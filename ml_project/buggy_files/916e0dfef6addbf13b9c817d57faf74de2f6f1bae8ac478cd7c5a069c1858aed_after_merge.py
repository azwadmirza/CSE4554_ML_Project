  def Handle(self, args, token=None):
    try:
      flow_obj = aff4.FACTORY.Open(args.operation_id,
                                   aff4_type=discovery.Interrogate,
                                   token=token)

      complete = not flow_obj.GetRunner().IsRunning()
    except aff4.InstantiationError:
      raise InterrogateOperationNotFoundError("Operation with id %s not found" %
                                              args.operation_id)

    result = ApiGetInterrogateOperationStateResult()
    if complete:
      result.state = ApiGetInterrogateOperationStateResult.State.FINISHED
    else:
      result.state = ApiGetInterrogateOperationStateResult.State.RUNNING

    return result