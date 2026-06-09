import os, subprocess, tempfile, math, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.tools import tool
from groq import Groq
from backend.config import PROJECT_ROOT, MAX_CHUNK_MB, MAX_WORKERS, AUDIO_MODEL

client = Groq()


def split_audio_ffmpeg(
    audio_path: str,
    target_chunk_mb: int = MAX_CHUNK_MB
):
    """
    Split large audio files into chunks using ffmpeg.
    """

    path = Path(audio_path)

    size_mb = path.stat().st_size / (1024 * 1024)

    if size_mb <= target_chunk_mb:
        return [str(path)]

    duration_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]

    duration = float(
        subprocess.check_output(duration_cmd)
        .decode()
        .strip()
    )

    num_chunks = math.ceil(
        size_mb / target_chunk_mb
    )

    chunk_duration = duration / num_chunks

    temp_dir = tempfile.mkdtemp()

    chunk_paths = []

    for i in range(num_chunks):

        start_time = i * chunk_duration

        output_file = os.path.join(
            temp_dir,
            f"chunk_{i}.mp3"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(path),
            "-ss", str(start_time),
            "-t", str(chunk_duration),
            output_file
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

        chunk_paths.append(output_file)

    return chunk_paths, temp_dir



def transcribe_chunk(chunk_path: str):

    with open(chunk_path, "rb") as f:

        result = client.audio.transcriptions.create(
            file=f,
            model=AUDIO_MODEL
        )

    chunk_num = int(
        Path(chunk_path)
        .stem
        .split("_")[-1]
    )

    return chunk_num, result.text





@tool
def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribe audio using Groq Whisper.
    Automatically chunks large audio files and
    transcribes chunks in parallel.
    """

    temp_dir = None

    try:

        path = Path(audio_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        path = path.resolve()

        if not path.exists():

            return {
                "success": False,
                "error": f"Audio file not found: {path}"
            }

        size_mb = path.stat().st_size / (
            1024 * 1024
        )

        # ----------------------------
        # Small File
        # ----------------------------

        if size_mb <= MAX_CHUNK_MB:

            with open(path, "rb") as f:

                result = (
                    client.audio.transcriptions.create(
                        file=f,
                        model="whisper-large-v3-turbo"
                    )
                )

            return {
                "success": True,
                "file_path": str(path),
                "num_chunks": 1,
                "transcript": result.text
            }

        # ----------------------------
        # Large File
        # ----------------------------

        chunk_paths, temp_dir = split_audio_ffmpeg(
            str(path)
        )

        transcripts = {}

        with ThreadPoolExecutor(
            max_workers=min(
                MAX_WORKERS,
                len(chunk_paths)
            )
        ) as executor:

            futures = [
                executor.submit(
                    transcribe_chunk,
                    chunk
                )
                for chunk in chunk_paths
            ]

            for future in as_completed(futures):

                chunk_id, text = future.result()

                transcripts[chunk_id] = text

        merged_transcript = "\n".join(
            transcripts[i]
            for i in sorted(
                transcripts.keys()
            )
        )

        return {
            "success": True,
            "file_path": str(path),
            "num_chunks": len(chunk_paths),
            "transcript": merged_transcript
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:

        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(
                temp_dir,
                ignore_errors=True
            )