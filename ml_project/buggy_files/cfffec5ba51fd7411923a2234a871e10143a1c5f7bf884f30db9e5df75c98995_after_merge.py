def get_sliders(update):
    # Start_box value indicates the desired start point of queried window.
    start_box = widgets.FloatText(
        description="Start Time:",
        disabled=True,
    )

    # End_box value indicates the desired end point of queried window.
    end_box = widgets.FloatText(
        description="End Time:",
        disabled=True,
    )

    # Percentage slider. Indicates either % of total time or total tasks
    # depending on what breakdown_opt is set to.
    range_slider = widgets.IntRangeSlider(
        value=[0, 100],
        min=0,
        max=100,
        step=1,
        description="%:",
        continuous_update=False,
        orientation="horizontal",
        readout=True,
    )

    # Indicates the number of tasks that the user wants to be returned. Is
    # disabled when the breakdown_opt value is set to total_time_value.
    num_tasks_box = widgets.IntText(
        description="Num Tasks:",
        disabled=False
    )

    # Dropdown bar that lets the user choose between modifying % of total
    # time or total number of tasks.
    breakdown_opt = widgets.Dropdown(
        options=[total_time_value, total_tasks_value],
        value=total_tasks_value,
        description="Selection Options:"
    )

    # Display box for layout.
    total_time_box = widgets.VBox([start_box, end_box])

    # This sets the CSS style display to hide the box.
    total_time_box.layout.display = 'none'

    # Initially passed in to the update_wrapper function.
    INIT_EVENT = "INIT"

    # Create instance of context manager to determine whether callback is
    # currently executing
    out_recursion = _EventRecursionContextManager()

    def update_wrapper(event):
        # Feature received a callback, but it shouldn't be executed
        # because the callback was the result of a different feature
        # executing its callback based on user input.
        if not out_recursion.should_recurse:
            return

        # Feature received a callback and it should be executed because
        # the callback was the result of user input.
        with out_recursion:
            smallest, largest, num_tasks = ray.global_state._job_length()
            diff = largest - smallest
            if num_tasks is not 0:

                # Describes the initial values that the slider/text box
                # values should be set to.
                if event == INIT_EVENT:
                    if breakdown_opt.value == total_tasks_value:
                        num_tasks_box.value = -min(10000, num_tasks)
                        range_slider.value = (int(100 -
                                              (100. * -num_tasks_box.value) /
                                              num_tasks), 100)
                    else:
                        low, high = map(lambda x: x / 100., range_slider.value)
                        start_box.value = round(diff * low, 2)
                        end_box.value = round(diff * high, 2)

                # Event was triggered by a change in the start_box value.
                elif event["owner"] == start_box:
                    if start_box.value > end_box.value:
                        start_box.value = end_box.value
                    elif start_box.value < 0:
                        start_box.value = 0
                    low, high = range_slider.value
                    range_slider.value = (int((start_box.value * 100.) /
                                          diff), high)

                # Event was triggered by a change in the end_box value.
                elif event["owner"] == end_box:
                    if start_box.value > end_box.value:
                        end_box.value = start_box.value
                    elif end_box.value > diff:
                        end_box.value = diff
                    low, high = range_slider.value
                    range_slider.value = (low, int((end_box.value * 100.) /
                                          diff))

                # Event was triggered by a change in the breakdown options
                # toggle.
                elif event["owner"] == breakdown_opt:
                    if breakdown_opt.value == total_tasks_value:
                        start_box.disabled = True
                        end_box.disabled = True
                        num_tasks_box.disabled = False
                        total_time_box.layout.display = 'none'

                        # Make CSS display go back to the default settings.
                        num_tasks_box.layout.display = None
                        num_tasks_box.value = min(10000, num_tasks)
                        range_slider.value = (int(100 -
                                              (100. * num_tasks_box.value) /
                                              num_tasks), 100)
                    else:
                        start_box.disabled = False
                        end_box.disabled = False
                        num_tasks_box.disabled = True

                        # Make CSS display go back to the default settings.
                        total_time_box.layout.display = None
                        num_tasks_box.layout.display = 'none'
                        range_slider.value = (int((start_box.value * 100.) /
                                              diff),
                                              int((end_box.value * 100.) /
                                              diff))

                # Event was triggered by a change in the range_slider
                # value.
                elif event["owner"] == range_slider:
                    low, high = map(lambda x: x / 100., range_slider.value)
                    if breakdown_opt.value == total_tasks_value:
                        old_low, old_high = event["old"]
                        new_low, new_high = event["new"]
                        if old_low != new_low:
                            range_slider.value = (new_low, 100)
                            num_tasks_box.value = (-(100. - new_low) /
                                                   100. * num_tasks)
                        else:
                            range_slider.value = (0, new_high)
                            num_tasks_box.value = new_high / 100. * num_tasks
                    else:
                        start_box.value = round(diff * low, 2)
                        end_box.value = round(diff * high, 2)

                # Event was triggered by a change in the num_tasks_box
                # value.
                elif event["owner"] == num_tasks_box:
                    if num_tasks_box.value > 0:
                        range_slider.value = (0, int(100 *
                                              float(num_tasks_box.value) /
                                              num_tasks))
                    elif num_tasks_box.value < 0:
                        range_slider.value = (100 +
                                              int(100 *
                                                  float(num_tasks_box.value) /
                                                  num_tasks), 100)

                if not update:
                    return

                diff = largest - smallest

                # Low and high are used to scale the times that are
                # queried to be relative to the absolute time.
                low, high = map(lambda x: x / 100., range_slider.value)

                # Queries to task_profiles based on the slider and text
                # box values.
                # (Querying based on the % total amount of time.)
                if breakdown_opt.value == total_time_value:
                    tasks = ray.global_state.task_profiles(start=(smallest +
                                                           diff * low),
                                                           end=(smallest +
                                                           diff * high))

                # (Querying based on % of total number of tasks that were
                # run.)
                elif breakdown_opt.value == total_tasks_value:
                    if range_slider.value[0] == 0:
                        tasks = ray.global_state.task_profiles(num_tasks=(int(
                                                               num_tasks *
                                                               high)),
                                                               fwd=True)
                    else:
                        tasks = ray.global_state.task_profiles(num_tasks=(int(
                                                               num_tasks *
                                                               (high - low))),
                                                               fwd=False)

                update(smallest, largest, num_tasks, tasks)

    # Get updated values from a slider or text box, and update the rest of
    # them accordingly.
    range_slider.observe(update_wrapper, names="value")
    breakdown_opt.observe(update_wrapper, names="value")
    start_box.observe(update_wrapper, names="value")
    end_box.observe(update_wrapper, names="value")
    num_tasks_box.observe(update_wrapper, names="value")

    # Initializes the sliders
    update_wrapper(INIT_EVENT)

    # Display sliders and search boxes
    display(breakdown_opt, widgets.HBox([range_slider, total_time_box,
                                         num_tasks_box]))

    # Return the sliders and text boxes
    return start_box, end_box, range_slider, breakdown_opt