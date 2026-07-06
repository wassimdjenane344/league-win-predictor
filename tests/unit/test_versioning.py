"""Tests for DVC data-version resolution (ml/src/versioning.py)."""

from pathlib import Path

from versioning import get_dvc_data_version


def test_get_dvc_data_version_reads_md5_from_dvc_file(tmp_path: Path):
    dvc_file = tmp_path / "dataset.csv.dvc"
    dvc_file.write_text(
        "outs:\n- md5: abc123def456\n  size: 42\n  hash: md5\n  path: dataset.csv\n"
    )

    assert get_dvc_data_version(dvc_file) == "abc123def456"


def test_get_dvc_data_version_falls_back_when_file_missing(tmp_path: Path):
    missing_file = tmp_path / "does_not_exist.csv.dvc"

    assert get_dvc_data_version(missing_file) == "no-dvc-file-yet"
