import cv2
import os
import concurrent.futures
import argparse
import sys
import numpy as np  # Added for frame comparison
from tqdm import tqdm  # added for progress bar

# New mapping for interpolation methods
INTERPOLATION_MAP = {
    "linear": cv2.INTER_LINEAR,
    "nearest": cv2.INTER_NEAREST,
    "cubic": cv2.INTER_CUBIC,
    "area": cv2.INTER_AREA,
}

def process_and_save(frame, frame_id, scale_factor, output_folder, img_format, overlay_timestamp, current_time, interpolation):
    """
    Resize the frame using the given scale factor and save it as an image.
    """
    # Optionally overlay the timestamp
    if overlay_timestamp:
        text = f"{current_time:.2f}s"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    height, width = frame.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=interpolation)
    filename = os.path.join(output_folder, f"frame_{frame_id:06d}.{img_format}")
    cv2.imwrite(filename, resized_frame)
    print(f"Saved {filename}")


def extract_frames(
    video_path,
    output_folder="frames",
    scale_factor=0.9,
    start_time=0.0,
    end_time=None,
    frame_step=1.0,
    similarity_threshold=0.0,
    ignore_similarity=False,  # New parameter to toggle similarity check
    img_format="jpg",
    overlay_timestamp=False,
    interpolation_method="linear"
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Error retrieving FPS from video.")
        sys.exit(1)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps

    if start_time < 0:
        print("Error: Start time cannot be negative.")
        sys.exit(1)
    if end_time is None:
        end_time = duration
    if start_time > duration:
        print(
            f"Error: Start time ({start_time} s) is greater than video duration ({duration:.2f} s)."
        )
        sys.exit(1)
    if end_time > duration:
        print(
            f"Error: End time ({end_time} s) is greater than video duration ({duration:.2f} s)."
        )
        sys.exit(1)
    if end_time <= start_time:
        print("Error: End time must be greater than start time.")
        sys.exit(1)

    print(f"Video duration: {duration:.2f} seconds, FPS: {fps:.2f}")
    print(f"Extracting frames from {start_time} s to {end_time} s with a step of {frame_step} s")
    num_cores = os.cpu_count() or 1
    print(f"Using {num_cores} threads for processing.")

    # Calculate frame indices and skip count
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    skip_frames = max(1, int(frame_step * fps))
    total_steps = (end_frame - start_frame) // skip_frames

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame_index = start_frame
    processed_count = 0
    skipped_count = 0
    saved_frame_count = 0
    previous_frame = None  # For similarity comparison
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor, tqdm(total=total_steps, desc="Extracting frames") as pbar:
        while current_frame_index < end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            current_time = current_frame_index / fps

            if not ignore_similarity and previous_frame is not None:
                # Optimized similarity check via cv2.absdiff
                diff = cv2.absdiff(frame, previous_frame)
                mse = np.mean(diff.astype(np.float32) ** 2)
                if mse < similarity_threshold:
                    skipped_count += 1
                    # Skip remaining frames for this interval using grab()
                    for _ in range(skip_frames - 1):
                        if cap.grab():
                            current_frame_index += 1
                        else:
                            break
                    current_frame_index += 1
                    pbar.update(1)
                    continue

            previous_frame = frame.copy()
            processed_count += 1

            futures.append(
                executor.submit(
                    process_and_save,
                    frame,
                    saved_frame_count,
                    scale_factor,
                    output_folder,
                    img_format,
                    overlay_timestamp,
                    current_time,
                    INTERPOLATION_MAP.get(interpolation_method, cv2.INTER_LINEAR)
                )
            )
            saved_frame_count += 1

            # Skip frames using grab() for efficiency
            for _ in range(skip_frames - 1):
                if cap.grab():
                    current_frame_index += 1
                else:
                    break
            current_frame_index += 1
            pbar.update(1)

    concurrent.futures.wait(futures)
    cap.release()
    print("Finished extracting frames.")
    print(f"Summary: Processed frames: {processed_count}, Saved frames: {saved_frame_count}, Skipped frames: {skipped_count}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract frames from a video with scaling, multithreading, time range selection, duplicate frame skipping, timestamp overlay, interpolation options, and error tolerance."
    )
    parser.add_argument("video_path", help="Path to the input video file.")
    parser.add_argument(
        "--output_folder", default="frames", help="Folder to save extracted frames."
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1,
        help="Scaling factor for frames (default 0.9).",
    )
    parser.add_argument(
        "--start", type=float, default=0.0, help="Start time in seconds (default 0.0)."
    )
    parser.add_argument(
        "--end",
        type=float,
        default=None,
        help="End time in seconds (default is video duration).",
    )
    parser.add_argument(
        "--frame_step",
        type=float,
        default=1.0,
        help="Time step between frames in seconds (default 1.0).",
    )
    parser.add_argument(
        "--similarity_threshold",
        type=float,
        default=0.0,
        help="If the mean squared error (MSE) between consecutive frames is less than this value, the frame is skipped. Use 0.0 to only skip completely identical frames; a reasonable value (e.g., 100.0) will skip frames with minor differences. Values significantly higher than 100.0 may skip even moderately different frames.",
    )
    parser.add_argument(
        "--ignore_similarity",
        action="store_true",
        help="If set, ignore the similarity check and extract all frames.",
    )
    # New arguments
    parser.add_argument("--format", choices=["jpg", "png"], default="jpg", help="Image format for saved frames.")
    parser.add_argument("--timestamp", action="store_true", help="Overlay frame timestamp on extracted images.")
    parser.add_argument("--interpolation", choices=["linear", "nearest", "cubic", "area"], default="linear", help="Interpolation method to resize frames.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    extract_frames(
        video_path=args.video_path,
        output_folder=args.output_folder,
        scale_factor=args.scale,
        start_time=args.start,
        end_time=args.end,
        frame_step=args.frame_step,
        similarity_threshold=args.similarity_threshold,
        ignore_similarity=args.ignore_similarity,  # Passing the new flag
        img_format=args.format,
        overlay_timestamp=args.timestamp,
        interpolation_method=args.interpolation
    )
