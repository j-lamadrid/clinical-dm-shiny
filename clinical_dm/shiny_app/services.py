from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from pathlib import Path
import os
import re
import shutil

from clinical_dm.processing.add_group import add_group
from clinical_dm.processing.flagger import id_date_sort
from clinical_dm.processing.group import group_late_talkers
from clinical_dm.processing.macarthur_percentiles import populate
from clinical_dm.processing.treatment_condensed import (
    calculate_treatment_units as calculate_treatment_units_condensed,
)
from clinical_dm.processing.treatment_condensed_wv import (
    calculate_treatment_units as calculate_treatment_units_condensed_wv,
)
from clinical_dm.processing.treatment_hours_full import calculate_treatment_hours
from clinical_dm.processing.modules.ets import EyeTrackingSheet

SCRIPT_OPTIONS = {
    "eye_tracking": "Eye Tracking Sheet Merger",
    "flagger": "Flagger",
    "group": "Group",
    "add_group": "AddGroup",
    "treatment_full": "Treatment Hours Full",
    "treatment_condensed": "Treatment Condensed",
    "treatment_condensed_wv": "Treatment Condensed WV",
    "macarthur": "MacArthur Percentiles",
}

SCRIPT_DETAILS = {
    "eye_tracking": {
        "script": "scripts/UpdateEyeTracking.py",
        "description": "Merges an exported eye-tracking sheet into the matching master sheet.",
    },
    "flagger": {
        "script": "scripts/Flagger.py",
        "description": "Sorts form output by subject and visit date, then assigns visit flags.",
    },
    "group": {
        "script": "scripts/Group.py",
        "description": "Groups late talker data into the existing diagnostic categories.",
    },
    "add_group": {
        "script": "scripts/AddGroup.py",
        "description": "Adds a new custom diagnostic grouping on top of grouped late talker data.",
    },
    "treatment_full": {
        "script": "scripts/TreatmentHoursFull.py",
        "description": "Calculates treatment hours and average hours per week on the full sheet.",
    },
    "treatment_condensed": {
        "script": "scripts/TreatmentCondensed.py",
        "description": "Calculates grouped treatment units on the condensed output.",
    },
    "treatment_condensed_wv": {
        "script": "scripts/TreatmentCondensedWV.py",
        "description": "Calculates grouped treatment units on the condensed WV output.",
    },
    "macarthur": {
        "script": "scripts/MacArthurPercentiles.py",
        "description": "Populates LWR records with MacArthur percentile columns.",
    },
}

TIMELINE_OPTIONS = {
    "Geo": "Original GeoPref",
    "Soc": "Complex Social GeoPref",
    "Play": "Peer Play GeoPref",
    "Traffic": "Motherese QL vs Traffic",
    "Techno": "Motherese LK vs Techno",
}

SOFTWARE_OPTIONS = {
    "Tobii ProLab": "Tobii ProLab",
    "Tobii Studio": "Tobii Studio",
    "Other": "Other",
}

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT_DIR / "outputs"


@dataclass
class ToolRunResult:
    output_path: Path
    log: str


@contextmanager
def working_directory(path: Path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def sanitize_output_stem(output_name: str | None, default_stem: str) -> str:
    raw_name = Path(output_name).stem if output_name else default_stem
    raw_name = raw_name.strip() or default_stem
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_name)
    return cleaned.strip("._") or default_stem


def create_run_dir(tool_key: str) -> Path:
    OUTPUT_ROOT.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / f"{timestamp}_{tool_key}"
    suffix = 1
    while run_dir.exists():
        suffix += 1
        run_dir = OUTPUT_ROOT / f"{timestamp}_{tool_key}_{suffix}"
    run_dir.mkdir(parents=True)
    return run_dir


def stage_file(source_path: str | Path, run_dir: Path, target_name: str | None = None) -> Path:
    source = Path(source_path)
    destination = run_dir / (target_name or source.name)
    shutil.copy2(source, destination)
    return destination


def finalize_log(buffer: StringIO, output_path: Path) -> str:
    message = buffer.getvalue().strip()
    if message:
        return f"{message}\n\nSaved to {output_path.resolve()}"
    return f"Completed without console output.\n\nSaved to {output_path.resolve()}"


def run_eye_tracking(
    export_path: str | Path,
    master_path: str | Path,
    summary_path: str | Path,
    lwr_path: str | Path,
    timeline: str,
    software: str,
    project_hint: str | None = None,
    output_name: str | None = None,
) -> ToolRunResult:
    run_dir = create_run_dir("eye_tracking")
    normalized_project_hint = (project_hint or "").strip()
    if normalized_project_hint.isdigit():
        normalized_project_hint = f"Project {normalized_project_hint}"
    normalized_project_hint = re.sub(r"[^A-Za-z0-9 _-]+", "", normalized_project_hint).strip()

    export_name_prefix = normalized_project_hint if normalized_project_hint else "export"
    export_local = stage_file(export_path, run_dir, target_name=f"{export_name_prefix}__{Path(export_path).name}")
    master_local = stage_file(master_path, run_dir, target_name=f"master__{Path(master_path).name}")
    summary_local = stage_file(summary_path, run_dir, target_name=f"summary__{Path(summary_path).name}")
    lwr_local = stage_file(lwr_path, run_dir, target_name=f"lwr__{Path(lwr_path).name}")
    output_stem = sanitize_output_stem(output_name, f"{Path(master_path).stem}_updated")
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        eye_tracking = EyeTrackingSheet(
            str(export_local),
            str(master_local),
            str(summary_local),
            str(lwr_local),
            timeline,
            software,
        )
        eye_tracking.generate()
        eye_tracking.fill()
        eye_tracking.push()
        eye_tracking.master_df.to_excel(output_path, index=False)
        print(f"File exported as {output_path.name}")

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_flagger(file_path: str | Path, output_name: str | None = None) -> ToolRunResult:
    run_dir = create_run_dir("flagger")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, f"{input_local.stem}_flagged")
    output_path = run_dir / f"{output_stem}.csv"
    buffer = StringIO()

    with redirect_stdout(buffer):
        id_date_sort(str(input_local), output_stem)
        print(f"File exported as {output_path.name}")

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_group(file_path: str | Path, output_name: str | None = None) -> ToolRunResult:
    run_dir = create_run_dir("group")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, "grouped_late_talkers")
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        with working_directory(run_dir):
            group_late_talkers(str(input_local), output_stem)

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_add_group(
    file_path: str | Path,
    new_group: str,
    begins_with: list[str],
    ends_with: list[str],
    possibilities: list[str],
    min_dxj: int,
    output_name: str | None = None,
) -> ToolRunResult:
    run_dir = create_run_dir("add_group")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, new_group or "custom_group")
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        with working_directory(run_dir):
            add_group(
                str(input_local),
                output_stem,
                new_group=new_group,
                begins_with=begins_with,
                ends_with=ends_with,
                possibilities=possibilities,
                min_dxj=min_dxj,
            )

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_treatment_full(file_path: str | Path, output_name: str | None = None) -> ToolRunResult:
    run_dir = create_run_dir("treatment_full")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, f"{input_local.stem}_hours")
    output_base = run_dir / output_stem
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        calculate_treatment_hours(str(input_local), str(output_base))

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_treatment_condensed(file_path: str | Path, output_name: str | None = None) -> ToolRunResult:
    run_dir = create_run_dir("treatment_condensed")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, f"{input_local.stem}_condensed")
    output_base = run_dir / output_stem
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        calculate_treatment_units_condensed(str(input_local), str(output_base))

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_treatment_condensed_wv(file_path: str | Path, output_name: str | None = None) -> ToolRunResult:
    run_dir = create_run_dir("treatment_condensed_wv")
    input_local = stage_file(file_path, run_dir)
    output_stem = sanitize_output_stem(output_name, f"{input_local.stem}_condensed_wv")
    output_base = run_dir / output_stem
    output_path = run_dir / f"{output_stem}.xlsx"
    buffer = StringIO()

    with redirect_stdout(buffer):
        calculate_treatment_units_condensed_wv(str(input_local), str(output_base))

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))


def run_macarthur(
    lwr_path: str | Path,
    appendix_path: str | Path,
    output_name: str | None = None,
) -> ToolRunResult:
    run_dir = create_run_dir("macarthur")
    lwr_local = stage_file(lwr_path, run_dir, target_name=f"lwr__{Path(lwr_path).name}")
    appendix_local = stage_file(
        appendix_path,
        run_dir,
        target_name=f"scoring_appendix__{Path(appendix_path).name}",
    )
    buffer = StringIO()

    with redirect_stdout(buffer):
        populate(str(lwr_local), str(appendix_local), str(run_dir))

    generated_path = run_dir / "macarthur_percentiles.xlsx"
    output_stem = sanitize_output_stem(output_name, generated_path.stem)
    output_path = run_dir / f"{output_stem}.xlsx"

    if output_path != generated_path:
        shutil.move(generated_path, output_path)
    else:
        output_path = generated_path

    return ToolRunResult(output_path=output_path, log=finalize_log(buffer, output_path))
