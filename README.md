# Simple Video Frame Extractor

This Python tool extracts frames from a video file with options to:
- Resize frames using a scaling factor.
- Select a specific time range within the video.
- Skip frames using a specified time step.
- Utilize multithreading for faster processing.

## Setup

### 1. Clone the Repository
Clone the repository and change into the project directory:

```bash
git clone https://github.com/Maxiviper117/simple-video-frame-extractor.git
cd simple-video-frame-extractor
```

### 2. Create and Activate a Virtual Environment

#### On Unix/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
Ensure you have a `requirements.txt` file in the root of your project. Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

The main script is located at `app/main.py`. You can run the script from the command line using:

```bash
python app/main.py <video_path> [--output_folder OUTPUT_FOLDER] [--scale SCALE] [--start START] [--end END] [--frame_step FRAME_STEP]
```

### Command-Line Arguments

- **video_path** (required): Path to the input video file.
- **--output_folder**: Folder to save the extracted frames (default: `frames`).
- **--scale**: Scaling factor for the frames (default: `0.9`).
- **--start**: Start time in seconds (default: `0.0`).
- **--end**: End time in seconds (default: video duration if not provided).
- **--frame_step**: Time step between frames in seconds (default: `1.0`).

### Example

To extract frames from `input_video.mp4` starting at 0 seconds until 30 seconds, resizing frames to 90% of their original size, and extracting one frame every 1 second, run:

```bash
python app/main.py ./input_video.mp4 --output_folder ./frames --scale 0.9 --start 0 --end 30 --frame_step 1
```

