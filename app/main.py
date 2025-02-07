import cv2
import os
import concurrent.futures
import argparse
import sys


def process_and_save(frame, frame_id, scale_factor, output_folder):
    """
    Resize the frame using the given scale factor and save it as an image.
    """
    # Get original dimensions and compute new dimensions
    height, width = frame.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    resized_frame = cv2.resize(
        frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR
    )

    # Build output file name and save the image
    filename = os.path.join(output_folder, f"frame_{frame_id:06d}.jpg")
    cv2.imwrite(filename, resized_frame)
    print(f"Saved {filename}")


def extract_frames(
    video_path, output_folder="frames", scale_factor=0.9, start_time=0.0, end_time=None, frame_step=1.0
):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        sys.exit(1)

    # Retrieve FPS and total frames to calculate video duration
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print("Error retrieving FPS from video.")
        sys.exit(1)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps

    # Validate start and end times
    if start_time < 0:
        print("Error: Start time cannot be negative.")
        sys.exit(1)
    if end_time is None:
        end_time = duration  # If not specified, set end time to video duration
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

    # Set the video position to the start time (in milliseconds)
    cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)

    # Determine the number of CPU cores for multithreading
    num_cores = os.cpu_count() or 1
    print(f"Using {num_cores} threads for processing.")

    futures = []
    saved_frame_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        while True:
            ret, frame = cap.read()
            if not ret:
                break  # No more frames to read

            # Get current time in the video (in seconds)
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            current_time = current_frame / fps

            # Stop if we've passed the end time
            if current_time > end_time:
                break

            # Submit frame processing to the thread pool
            futures.append(
                executor.submit(
                    process_and_save,
                    frame,
                    saved_frame_count,
                    scale_factor,
                    output_folder,
                )
            )
            saved_frame_count += 1

            # Skip to the next frame based on frame_step
            cap.set(cv2.CAP_PROP_POS_MSEC, (current_time + frame_step) * 1000)

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)
    cap.release()
    print("Finished extracting frames.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract frames from a video with scaling, multithreading, and time range selection."
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
    )
