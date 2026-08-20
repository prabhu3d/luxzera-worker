# handler.py
"""
LUXZERA RunPod Serverless worker.

Job input (sent by the app):
  {
    "input": {
      "job_id": "...",
      "photo_url": "https://...",      # signed url, first photo
      "photo_urls": ["https://...", ...],
      "video_url": "https://... | null",  # reference dance video
      "ref_song": "... | null",
      "dance_style": "... | null",
      "duration_seconds": 30,
      "settings": { ... },
      "callback_url": "... | null"
    }
  }

Return value MUST contain a public video url so the app can show it:
  {"output_url": "https://..."}
"""

import os
import traceback

import runpod


def _generate(job_input: dict) -> dict:
    """Replace the body of this function with your real model pipeline."""
    photo_url = job_input.get("photo_url") or (job_input.get("photo_urls") or [None])[0]
    video_url = job_input.get("video_url")

    if not photo_url:
        return {"error": "photo_url is required"}

    # ------------------------------------------------------------------
    # TODO: run your model here (e.g. InstantID + Wan 2.1 / CogVideoX),
    # upload the mp4 somewhere public (S3 / R2 / Supabase storage) and
    # return that url below.
    # ------------------------------------------------------------------
    result_url = os.environ.get("DEMO_OUTPUT_URL")
    if not result_url:
        return {
            "error": "Pipeline not implemented yet. Fill in _generate() and return {'output_url': ...}",
            "received": {"photo_url": photo_url, "video_url": video_url},
        }

    return {"output_url": result_url}


def handler(event):
    """RunPod entry point. Must be sync or async and return JSON-serialisable data."""
    try:
        job_input = (event or {}).get("input") or {}
        print(f"[luxzera] received job: {job_input.get('job_id')}", flush=True)
        result = _generate(job_input)
        print(f"[luxzera] finished job: {result}", flush=True)
        return result
    except Exception as exc:  # noqa: BLE001 - report every failure back to RunPod
        traceback.print_exc()
        return {"error": f"{type(exc).__name__}: {exc}"}


# This MUST be the last line of the file — without it the worker starts,
# never picks up jobs, and every job stays IN_QUEUE forever.
runpod.serverless.start({"handler": handler})
