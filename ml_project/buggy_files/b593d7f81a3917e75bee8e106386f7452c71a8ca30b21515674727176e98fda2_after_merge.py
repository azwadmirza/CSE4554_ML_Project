    def _hook_var_ser(hook_self):
        def ser(self, include_data=True):
            """Serializes a variable into a JSON object"""

            var_msg = {}
            var_msg['torch_type'] = re.search(
                "<class '(.*)'>", str(self.__class__)).group(1)
            var_msg['requires_grad'] = self.requires_grad
            var_msg['volatile'] = self.volatile
            var_msg['data'] = self.data.ser(include_data)
            if self.grad is not None:
                var_msg['grad'] = self.grad.ser(include_data)
            else:
                var_msg['grad'] = None
            var_msg['id'] = self.id
            if(type(self.owners[0]) is int):
                var_msg['owners'] = self.owners
            else:
                var_msg['owners'] = list(map(lambda x: x.id, self.owners))
            var_msg['is_pointer'] = not include_data
            return json.dumps(var_msg)

        def deser(self, obj_msg):
            """Deserializes a JSON object into a variable"""

            if 'data' in obj_msg.keys():
                data_msg = json.loads(obj_msg['data'])
                tensor_type = hook_self.types_guard(data_msg['torch_type'])
                data_obj = tensor_type.deser(tensor_type, data_msg)
                # data_obj = hook_self.build_tensor(data_msg, tensor_type)
                data = hook_self.local_worker.handle_register(
                    data_obj, data_msg)

            if 'grad' in obj_msg.keys():
                if obj_msg['grad'] is not None:

                    grad_msg = json.loads(obj_msg['grad'])

                    var_type = hook_self.types_guard(grad_msg['torch_type'])
                    grad_obj = hook_self._build_var(grad_msg, var_type)

                    grad = hook_self.local_worker.handle_register(grad_obj, grad_msg,
                                                                  force_attach_to_worker=False,
                                                                  temporary=True)
                else:
                    grad = None

            # nn.parameter.Parameter does not accept "volatile" as an input param.
            # https://pytorch.org/docs/0.3.1/autograd.html#variable
            if(self == torch.nn.parameter.Parameter):
                var = self(data, requires_grad=obj_msg['requires_grad'])
            else:
                var = self(data, volatile=obj_msg['volatile'],
                           requires_grad=obj_msg['requires_grad'])

            # var.grad = grad
            if(grad is not None):
                setattr(var, 'grad', grad)
            else:
                var.grad = None

            # this returns grad because garbage collection seems to do something really strange
            # if grad isn't returned here. It re-initializes the gradient somehow but in a way
            # where it's not registered (which is bad)
            return var

        torch.autograd.variable.Variable.ser = ser
        torch.autograd.variable.Variable.deser = deser