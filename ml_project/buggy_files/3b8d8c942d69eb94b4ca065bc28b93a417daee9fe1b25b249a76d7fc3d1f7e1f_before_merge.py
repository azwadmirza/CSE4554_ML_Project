def render_unrendered_timelapse(name, gcode=None, postfix=None, fps=25):
	capture_dir = settings().getBaseFolder("timelapse_tmp")
	output_dir = settings().getBaseFolder("timelapse")
	threads = settings().get(["webcam", "ffmpegThreads"])

	job = TimelapseRenderJob(capture_dir, output_dir, name,
	                         postfix=postfix,
	                         capture_format=_capture_format,
	                         output_format=_output_format,
	                         fps=fps,
	                         threads=threads,
	                         on_start=_create_render_start_handler(name, gcode=gcode),
	                         on_success=_create_render_success_handler(name, gcode=gcode),
	                         on_fail=_create_render_fail_handler(name, gcode=gcode),
	                         on_always=_create_render_always_handler(name, gcode=gcode))
	job.process()