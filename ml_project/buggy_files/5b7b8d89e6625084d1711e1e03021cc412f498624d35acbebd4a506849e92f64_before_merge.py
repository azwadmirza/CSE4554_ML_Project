def make_nditer_cls(nditerty):
    """
    Return the Structure representation of the given *nditerty* (an
    instance of types.NumpyNdIterType).
    """
    ndim = nditerty.ndim
    layout = nditerty.layout
    narrays = len(nditerty.arrays)
    nshapes = ndim if nditerty.need_shaped_indexing else 1

    class BaseSubIter(object):
        """
        Base class for sub-iterators of a nditer() instance.
        """

        def __init__(self, nditer, member_name, start_dim, end_dim):
            self.nditer = nditer
            self.member_name = member_name
            self.start_dim = start_dim
            self.end_dim = end_dim
            self.ndim = end_dim - start_dim

        def set_member_ptr(self, ptr):
            setattr(self.nditer, self.member_name, ptr)

        @utils.cached_property
        def member_ptr(self):
            return getattr(self.nditer, self.member_name)

        def init_specific(self, context, builder):
            pass

        def loop_continue(self, context, builder, logical_dim):
            pass

        def loop_break(self, context, builder, logical_dim):
            pass

    class FlatSubIter(BaseSubIter):
        """
        Sub-iterator walking a contiguous array in physical order, with
        support for broadcasting (the index is reset on the outer dimension).
        """

        def init_specific(self, context, builder):
            zero = context.get_constant(types.intp, 0)
            self.set_member_ptr(cgutils.alloca_once_value(builder, zero))

        def compute_pointer(self, context, builder, indices, arrty, arr):
            index = builder.load(self.member_ptr)
            return builder.gep(arr.data, [index])

        def loop_continue(self, context, builder, logical_dim):
            if logical_dim == self.ndim - 1:
                # Only increment index inside innermost logical dimension
                index = builder.load(self.member_ptr)
                index = cgutils.increment_index(builder, index)
                builder.store(index, self.member_ptr)

        def loop_break(self, context, builder, logical_dim):
            if logical_dim == 0:
                # At the exit of outermost logical dimension, reset index
                zero = context.get_constant(types.intp, 0)
                builder.store(zero, self.member_ptr)
            elif logical_dim == self.ndim - 1:
                # Inside innermost logical dimension, increment index
                index = builder.load(self.member_ptr)
                index = cgutils.increment_index(builder, index)
                builder.store(index, self.member_ptr)

    class TrivialFlatSubIter(BaseSubIter):
        """
        Sub-iterator walking a contiguous array in physical order,
        *without* support for broadcasting.
        """

        def init_specific(self, context, builder):
            assert not nditerty.need_shaped_indexing

        def compute_pointer(self, context, builder, indices, arrty, arr):
            assert len(indices) <= 1, len(indices)
            return builder.gep(arr.data, indices)

    class IndexedSubIter(BaseSubIter):
        """
        Sub-iterator walking an array in logical order.
        """

        def compute_pointer(self, context, builder, indices, arrty, arr):
            assert len(indices) == self.ndim
            return cgutils.get_item_pointer(builder, arrty, arr,
                                            indices, wraparound=False)

    class ZeroDimSubIter(BaseSubIter):
        """
        Sub-iterator "walking" a 0-d array.
        """

        def compute_pointer(self, context, builder, indices, arrty, arr):
            return arr.data

    class ScalarSubIter(BaseSubIter):
        """
        Sub-iterator "walking" a scalar value.
        """

        def compute_pointer(self, context, builder, indices, arrty, arr):
            return arr

    class NdIter(cgutils.create_struct_proxy(nditerty)):
        """
        .nditer() implementation.

        Note: 'F' layout means the shape is iterated in reverse logical order,
        so indices and shapes arrays have to be reversed as well.
        """

        @utils.cached_property
        def subiters(self):
            l = []
            factories = {'flat': FlatSubIter if nditerty.need_shaped_indexing
                         else TrivialFlatSubIter,
                         'indexed': IndexedSubIter,
                         '0d': ZeroDimSubIter,
                         'scalar': ScalarSubIter,
                         }
            for i, sub in enumerate(nditerty.indexers):
                kind, start_dim, end_dim, _ = sub
                member_name = 'index%d' % i
                factory = factories[kind]
                l.append(factory(self, member_name, start_dim, end_dim))
            return l

        def init_specific(self, context, builder, arrtys, arrays):
            """
            Initialize the nditer() instance for the specific array inputs.
            """
            zero = context.get_constant(types.intp, 0)

            # Store inputs
            self.arrays = context.make_tuple(builder, types.Tuple(arrtys),
                                             arrays)
            # Create slots for scalars
            for i, ty in enumerate(arrtys):
                if not isinstance(ty, types.Array):
                    member_name = 'scalar%d' % i
                    # XXX as_data()?
                    slot = cgutils.alloca_once_value(builder, arrays[i])
                    setattr(self, member_name, slot)

            arrays = self._arrays_or_scalars(context, builder, arrtys, arrays)

            # Extract iterator shape (the shape of the most-dimensional input)
            main_shape_ty = types.UniTuple(types.intp, ndim)
            main_shape = None
            main_nitems = None
            for i, arrty in enumerate(arrtys):
                if isinstance(arrty, types.Array) and arrty.ndim == ndim:
                    main_shape = arrays[i].shape
                    main_nitems = arrays[i].nitems
                    break
            else:
                # Only scalar inputs => synthesize a dummy shape
                assert ndim == 0
                main_shape = context.make_tuple(builder, main_shape_ty, ())
                main_nitems = context.get_constant(types.intp, 1)

            # Validate shapes of array inputs
            def check_shape(shape, main_shape):
                n = len(shape)
                for i in range(n):
                    if shape[i] != main_shape[len(main_shape) - n + i]:
                        raise ValueError("nditer(): operands could not be "
                                         "broadcast together")

            for arrty, arr in zip(arrtys, arrays):
                if isinstance(arrty, types.Array) and arrty.ndim > 0:
                    sig = signature(types.none,
                                    types.UniTuple(types.intp, arrty.ndim),
                                    main_shape_ty)
                    context.compile_internal(builder, check_shape,
                                             sig, (arr.shape, main_shape))

            # Compute shape and size
            shapes = cgutils.unpack_tuple(builder, main_shape)
            if layout == 'F':
                shapes = shapes[::-1]

            # If shape is empty, mark iterator exhausted
            shape_is_empty = builder.icmp_signed('==', main_nitems, zero)
            exhausted = builder.select(shape_is_empty, cgutils.true_byte,
                                       cgutils.false_byte)

            if not nditerty.need_shaped_indexing:
                # Flatten shape to make iteration faster on small innermost
                # dimensions (e.g. a (100000, 3) shape)
                shapes = (main_nitems,)
            assert len(shapes) == nshapes

            indices = cgutils.alloca_once(builder, zero.type, size=nshapes)
            for dim in range(nshapes):
                idxptr = cgutils.gep_inbounds(builder, indices, dim)
                builder.store(zero, idxptr)

            self.indices = indices
            self.shape = cgutils.pack_array(builder, shapes, zero.type)
            self.exhausted = cgutils.alloca_once_value(builder, exhausted)

            # Initialize subiterators
            for subiter in self.subiters:
                subiter.init_specific(context, builder)

        def iternext_specific(self, context, builder, result):
            """
            Compute next iteration of the nditer() instance.
            """
            bbend = builder.append_basic_block('end')

            # Branch early if exhausted
            exhausted = cgutils.as_bool_bit(builder,
                                            builder.load(self.exhausted))
            with cgutils.if_unlikely(builder, exhausted):
                result.set_valid(False)
                builder.branch(bbend)

            arrtys = nditerty.arrays
            arrays = cgutils.unpack_tuple(builder, self.arrays)
            arrays = self._arrays_or_scalars(context, builder, arrtys, arrays)
            indices = self.indices

            # Compute iterated results
            result.set_valid(True)
            views = self._make_views(context, builder, indices, arrtys, arrays)
            views = [v._getvalue() for v in views]
            if len(views) == 1:
                result.yield_(views[0])
            else:
                result.yield_(context.make_tuple(builder, nditerty.yield_type,
                                                 views))

            shape = cgutils.unpack_tuple(builder, self.shape)
            _increment_indices(context, builder, len(shape), shape,
                               indices, self.exhausted,
                               functools.partial(self._loop_continue,
                                                 context,
                                                 builder),
                               functools.partial(self._loop_break,
                                                 context,
                                                 builder),
                               )

            builder.branch(bbend)
            builder.position_at_end(bbend)

        def _loop_continue(self, context, builder, dim):
            for sub in self.subiters:
                if sub.start_dim <= dim < sub.end_dim:
                    sub.loop_continue(context, builder, dim - sub.start_dim)

        def _loop_break(self, context, builder, dim):
            for sub in self.subiters:
                if sub.start_dim <= dim < sub.end_dim:
                    sub.loop_break(context, builder, dim - sub.start_dim)

        def _make_views(self, context, builder, indices, arrtys, arrays):
            """
            Compute the views to be yielded.
            """
            views = [None] * narrays
            indexers = nditerty.indexers
            subiters = self.subiters
            rettys = nditerty.yield_type
            if isinstance(rettys, types.BaseTuple):
                rettys = list(rettys)
            else:
                rettys = [rettys]
            indices = [builder.load(cgutils.gep_inbounds(builder, indices, i))
                       for i in range(nshapes)]

            for sub, subiter in zip(indexers, subiters):
                _, _, _, array_indices = sub
                sub_indices = indices[subiter.start_dim:subiter.end_dim]
                if layout == 'F':
                    sub_indices = sub_indices[::-1]
                for i in array_indices:
                    assert views[i] is None
                    views[i] = self._make_view(context, builder, sub_indices,
                                               rettys[i],
                                               arrtys[i], arrays[i], subiter)
            assert all(v for v in views)
            return views

        def _make_view(self, context, builder, indices, retty, arrty, arr,
                       subiter):
            """
            Compute a 0d view for a given input array.
            """
            assert isinstance(retty, types.Array) and retty.ndim == 0

            ptr = subiter.compute_pointer(context, builder, indices, arrty, arr)
            view = context.make_array(retty)(context, builder)

            itemsize = get_itemsize(context, retty)
            shape = context.make_tuple(builder, types.UniTuple(types.intp, 0),
                                       ())
            strides = context.make_tuple(builder, types.UniTuple(types.intp, 0),
                                         ())
            # HACK: meminfo=None avoids expensive refcounting operations
            # on ephemeral views
            populate_array(view, ptr, shape, strides, itemsize, meminfo=None)
            return view

        def _arrays_or_scalars(self, context, builder, arrtys, arrays):
            # Return a list of either array structures or pointers to
            # scalar slots
            l = []
            for i, (arrty, arr) in enumerate(zip(arrtys, arrays)):
                if isinstance(arrty, types.Array):
                    l.append(context.make_array(arrty)(context,
                                                       builder,
                                                       value=arr))
                else:
                    l.append(getattr(self, "scalar%d" % i))
            return l

    return NdIter