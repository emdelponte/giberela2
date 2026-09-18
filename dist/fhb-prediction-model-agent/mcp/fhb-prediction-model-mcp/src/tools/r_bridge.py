"""Subprocess bridge to R dispatcher for scientific computation."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


def run_r_dispatcher(command: str, payload: dict) -> dict:
    """Execute an operation using the R dispatcher script.

    Parameters
    ----------
    command : str
        Dispatcher command ('predict_logistic', 'predict_ensemble', 'economic_benefit').
    payload : dict
        Arguments serialized as JSON and passed to the R process.

    Returns
    -------
    dict
        Parsed JSON output from the R dispatcher.
    """
    # Allow environment override
    rscript_bin = os.environ.get("P2A_RSCRIPT", "Rscript")

    # Locate dispatcher script
    script_path = Path(__file__).resolve().parent.parent / "r_scripts" / "fhb_dispatcher.R"
    if not script_path.exists():
        raise FileNotFoundError(f"R dispatcher script not found at {script_path}")

    input_json = json.dumps(payload)

    env = os.environ.copy()
    # Support custom R library/project if set
    if "P2A_R_PROJECT" in env:
        env["R_PROFILE_USER"] = str(Path(env["P2A_R_PROJECT"]) / ".Rprofile")

    cmd = [rscript_bin, str(script_path), command]

    try:
        proc = subprocess.run(
            cmd,
            input=input_json,
            text=True,
            capture_output=True,
            check=False,
            cwd=str(script_path.parent),
            env=env,
            timeout=45,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Could not find Rscript binary '{rscript_bin}'. "
            "Please ensure R is installed and accessible in PATH, or set P2A_RSCRIPT."
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"R computation timed out after 45 seconds: {e}") from e

    if proc.returncode != 0:
        err_msg = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"R dispatcher failed with exit code {proc.returncode}: {err_msg}")

    # Parse stdout JSON
    stdout_clean = proc.stdout.strip()
    if not stdout_clean:
        raise RuntimeError(f"R dispatcher produced no output. Stderr: {proc.stderr.strip()}")

    # In case any warning leaked into stdout, extract the JSON object
    first_brace = stdout_clean.find("{")
    last_brace = stdout_clean.rfind("}")
    if first_brace != -1 and last_brace != -1:
        json_str = stdout_clean[first_brace : last_brace + 1]
    else:
        json_str = stdout_clean

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse R JSON output: {e}. Raw stdout: {stdout_clean}") from e
