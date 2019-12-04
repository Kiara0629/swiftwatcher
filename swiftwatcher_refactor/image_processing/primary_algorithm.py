import swiftwatcher_refactor.image_processing.data_structures as ds
import swiftwatcher_refactor.io.video_io as vio
import swiftwatcher_refactor.data_analysis.segment_tracking as st
import swiftwatcher_refactor.io.ui as ui


def swift_counting_algorithm(filepath, crop_region, resize_dim, roi_mask):
    """"""

    print("[*] Now processing {}.".format(filepath.name))

    # TODO: Replace FrameReader with VideoCapture object (possibly subclass?)

    ui.start_status(filepath.name)

    # reader = vio.FrameReader(frame_path, start, end)
    queue = ds.FrameQueue()
    tracker = st.SegmentTracker(roi_mask)

    while queue.frames_processed:  # < reader.total_frames:
        # frames, frame_numbers = reader.get_n_frames(n=queue.maxlen)
        queue.fill_queue()  # (frames, frame_numbers)
        queue.preprocess_queue(crop_region, resize_dim)
        queue.segment_queue()

        while not queue.is_empty():
            tracker.set_current_frame(queue.pop_frame())
            cost_matrix = tracker.formulate_cost_matrix()
            assignments = tracker.apply_hungarian_algorithm(cost_matrix)
            tracker.interpret_assignments(assignments)
            tracker.link_matching_segments()
            tracker.check_for_events()
            tracker.cache_current_frame()

        ui.frames_processed_status(queue.frames_processed)  # reader.total_frames)

    return tracker.detected_events