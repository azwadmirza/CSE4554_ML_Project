    def request(self, name, number=0, *, dir=None, xdr=None):
        resource = self.lookup(name, number)
        if (resource.name, resource.number) in self._requested:
            raise ResourceError("Resource {}#{} has already been requested"
                                .format(name, number))

        def merge_options(subsignal, dir, xdr):
            if isinstance(subsignal.ios[0], Subsignal):
                if dir is None:
                    dir = dict()
                if xdr is None:
                    xdr = dict()
                if not isinstance(dir, dict):
                    raise TypeError("Directions must be a dict, not {!r}, because {!r} "
                                    "has subsignals"
                                    .format(dir, subsignal))
                if not isinstance(xdr, dict):
                    raise TypeError("Data rate must be a dict, not {!r}, because {!r} "
                                    "has subsignals"
                                    .format(xdr, subsignal))
                for sub in subsignal.ios:
                    sub_dir = dir.get(sub.name, None)
                    sub_xdr = xdr.get(sub.name, None)
                    dir[sub.name], xdr[sub.name] = merge_options(sub, sub_dir, sub_xdr)
            else:
                if dir is None:
                    dir = subsignal.ios[0].dir
                if xdr is None:
                    xdr = 0
                if dir not in ("i", "o", "oe", "io", "-"):
                    raise TypeError("Direction must be one of \"i\", \"o\", \"oe\", \"io\", "
                                    "or \"-\", not {!r}"
                                    .format(dir))
                if dir != subsignal.ios[0].dir and \
                        not (subsignal.ios[0].dir == "io" or dir == "-"):
                    raise ValueError("Direction of {!r} cannot be changed from \"{}\" to \"{}\"; "
                                     "direction can be changed from \"io\" to \"i\", \"o\", or "
                                     "\"oe\", or from anything to \"-\""
                                     .format(subsignal.ios[0], subsignal.ios[0].dir, dir))
                if not isinstance(xdr, int) or xdr < 0:
                    raise ValueError("Data rate of {!r} must be a non-negative integer, not {!r}"
                                     .format(subsignal.ios[0], xdr))
            return dir, xdr

        def resolve(resource, dir, xdr, name, attrs):
            for attr_key, attr_value in attrs.items():
                if hasattr(attr_value, "__call__"):
                    attr_value = attr_value(self)
                    assert attr_value is None or isinstance(attr_value, str)
                if attr_value is None:
                    del attrs[attr_key]
                else:
                    attrs[attr_key] = attr_value

            if isinstance(resource.ios[0], Subsignal):
                fields = OrderedDict()
                for sub in resource.ios:
                    fields[sub.name] = resolve(sub, dir[sub.name], xdr[sub.name],
                                               name="{}__{}".format(name, sub.name),
                                               attrs={**attrs, **sub.attrs})
                return Record([
                    (f_name, f.layout) for (f_name, f) in fields.items()
                ], fields=fields, name=name)

            elif isinstance(resource.ios[0], (Pins, DiffPairs)):
                phys = resource.ios[0]
                if isinstance(phys, Pins):
                    phys_names = phys.names
                    port = Record([("io", len(phys))], name=name)
                if isinstance(phys, DiffPairs):
                    phys_names = []
                    record_fields = []
                    if not self.should_skip_port_component(None, attrs, "p"):
                        phys_names += phys.p.names
                        record_fields.append(("p", len(phys)))
                    if not self.should_skip_port_component(None, attrs, "n"):
                        phys_names += phys.n.names
                        record_fields.append(("n", len(phys)))
                    port = Record(record_fields, name=name)
                if dir == "-":
                    pin = None
                else:
                    pin = Pin(len(phys), dir, xdr=xdr, name=name)

                for phys_name in phys_names:
                    if phys_name in self._phys_reqd:
                        raise ResourceError("Resource component {} uses physical pin {}, but it "
                                            "is already used by resource component {} that was "
                                            "requested earlier"
                                            .format(name, phys_name, self._phys_reqd[phys_name]))
                    self._phys_reqd[phys_name] = name

                self._ports.append((resource, pin, port, attrs))

                if pin is not None and resource.clock is not None:
                    self.add_clock_constraint(pin.i, resource.clock.frequency)

                return pin if pin is not None else port

            else:
                assert False # :nocov:

        value = resolve(resource,
            *merge_options(resource, dir, xdr),
            name="{}_{}".format(resource.name, resource.number),
            attrs=resource.attrs)
        self._requested[resource.name, resource.number] = value
        return value