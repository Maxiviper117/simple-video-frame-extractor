# Simple Video Frame Extractor

This Python tool extracts frames from a video file with options to:
- Resize frames using a scaling factor.
- Select a specific time range within the video.
- Skip frames using a specified time step.
- Utilize multithreading for faster processing.
- Skip similar frames using a similarity threshold.

## Setup

### 1. Clone the Repository
Clone the repository and change into the project directory:

```bash
git clone <repository-url>
cd <repository-directory>
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
python app/main.py <video_path> [--output_folder OUTPUT_FOLDER] [--scale SCALE] [--start START] [--end END] [--frame_step FRAME_STEP] [--similarity_threshold SIMILARITY_THRESHOLD] [--ignore_similarity]
```

### Command-Line Arguments

- **video_path** (required): Path to the input video file.
- **--output_folder**: Folder to save the extracted frames (default: `frames`).
- **--scale**: Scaling factor for the frames (default: `0.9`).
- **--start**: Start time in seconds (default: `0.0`).
- **--end**: End time in seconds (default: video duration if not provided).
- **--frame_step**: Time step between frames in seconds (default: `1.0`).
- **--similarity_threshold**: Threshold for Mean Squared Error (MSE) between consecutive frames. Higher values skip more similar frames (default: `0.0`). 
  - Values below `10.0` are not recommended as they may be too sensitive
  - `50.0`: Good starting point for most videos
  - `100.0`: Skips frames with minor differences
  - `1000.0`: Skips frames with moderate differences
  - Use higher values for more aggressive frame skipping but too high may be excessive!
- **--ignore_similarity**: Flag to disable similarity checking and extract all frames.

### Example

To extract frames from `input_video.mp4` starting at 0 seconds until 30 seconds, resizing frames to 90% of their original size, extracting one frame every 1 second, and skipping similar frames with a threshold of 100:

```bash
python app/main.py ./input_video.mp4 --output_folder frames --scale 0.9 --start 0 --end 30 --frame_step 1 --similarity_threshold 100
```

To extract all frames without similarity checking:

```bash
python app/main.py ./input_video.mp4 --output_folder frames --ignore_similarity
```

