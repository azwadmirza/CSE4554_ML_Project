    def print_results(results):
        """
        Method to print the aggregated results from the profiler

        .. code-block:: python

            profiler.print_results(results)

        Example output:

        .. code-block:: text

            --------------------------------------------
            - Time profiling results:
            --------------------------------------------
            Processing function time stats (in seconds):
                min/index: (2.9754010029137135e-05, 0)
                max/index: (2.9754010029137135e-05, 0)
                mean: 2.9754010029137135e-05
                std: nan
                total: 2.9754010029137135e-05

            Dataflow time stats (in seconds):
                min/index: (0.2523871660232544, 0)
                max/index: (0.2523871660232544, 0)
                mean: 0.2523871660232544
                std: nan
                total: 0.2523871660232544

            Time stats of event handlers (in seconds):
            - Total time spent:
                1.0080009698867798

            - Events.STARTED:
                min/index: (0.1256754994392395, 0)
                max/index: (0.1256754994392395, 0)
                mean: 0.1256754994392395
                std: nan
                total: 0.1256754994392395

            Handlers names:
            ['BasicTimeProfiler._as_first_started', 'delay_start']
            --------------------------------------------
        """

        def odict_to_str(d):
            out = ""
            for k, v in d.items():
                out += "\t{}: {}\n".format(k, v)
            return out

        others = {
            k: odict_to_str(v) if isinstance(v, OrderedDict) else v for k, v in results["event_handlers_stats"].items()
        }

        others.update(results["event_handlers_names"])

        output_message = """
--------------------------------------------
- Time profiling results:
--------------------------------------------

Processing function time stats (in seconds):
{processing_stats}

Dataflow time stats (in seconds):
{dataflow_stats}

Time stats of event handlers (in seconds):
- Total time spent:
\t{total_time}

- Events.STARTED:
{STARTED}
Handlers names:
{STARTED_names}

- Events.EPOCH_STARTED:
{EPOCH_STARTED}
Handlers names:
{EPOCH_STARTED_names}

- Events.ITERATION_STARTED:
{ITERATION_STARTED}
Handlers names:
{ITERATION_STARTED_names}

- Events.ITERATION_COMPLETED:
{ITERATION_COMPLETED}
Handlers names:
{ITERATION_COMPLETED_names}

- Events.EPOCH_COMPLETED:
{EPOCH_COMPLETED}
Handlers names:
{EPOCH_COMPLETED_names}

- Events.COMPLETED:
{COMPLETED}
Handlers names:
{COMPLETED_names}

""".format(
            processing_stats=odict_to_str(results["processing_stats"]),
            dataflow_stats=odict_to_str(results["dataflow_stats"]),
            **others,
        )
        print(output_message)
        return output_message