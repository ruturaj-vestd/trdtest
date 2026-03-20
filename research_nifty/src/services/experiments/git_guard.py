from __future__ import annotations

import subprocess


def create_experiment_branch(name: str) -> None:
    subprocess.run(["git", "checkout", "-b", name], check=False)


def generate_patch(diff_path: str = "experiments/candidate.patch") -> None:
    subprocess.run(["git", "diff", "--", "."], check=False, capture_output=False)
