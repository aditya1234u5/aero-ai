import json
import os
import pytest
from aero_ai.schemas import Requirements
from aero_ai.pipeline import run_pipeline


@pytest.fixture(scope="module")
def pipeline_run(tmp_path_factory):
    out_dir = str(tmp_path_factory.mktemp("pipeline"))
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=45, cruise_speed_ms=15)
    return run_pipeline(req, out_dir=out_dir), out_dir


def test_pipeline_succeeds_and_writes_files(pipeline_run):
    result, _ = pipeline_run
    assert result.ok
    assert result.results is not None
    assert all(os.path.getsize(p) > 0 for p in result.files)


def test_pipeline_saves_valid_json(pipeline_run):
    result, out_dir = pipeline_run
    with open(os.path.join(out_dir, "result.json")) as f:
        data = json.load(f)
    assert data["ok"] is True
    assert abs(data["design"]["total_mass_kg"] - result.design.total_mass_kg) < 1e-9
    assert data["requirements"]["aircraft_type"] == "fixed_wing"


def test_pipeline_result_meets_the_requirements(pipeline_run):
    result, _ = pipeline_run
    assert result.results.endurance_min >= 0.9 * 45
    assert abs(result.results.cruise_cm) < 0.01


def test_unsupported_aircraft_type_names_the_supported_ones(tmp_path):
    req = Requirements("blimp", payload_kg=1.0, endurance_min=30, cruise_speed_ms=10)
    with pytest.raises(ValueError, match="fixed_wing"):
        run_pipeline(req, out_dir=str(tmp_path))


def test_unrealistic_request_fails_cleanly_without_crashing(tmp_path):
    req = Requirements("fixed_wing", payload_kg=1.0, endurance_min=1000, cruise_speed_ms=15)
    result = run_pipeline(req, out_dir=str(tmp_path))
    assert not result.ok
    assert result.files == []
    assert any(i.severity == "error" for i in result.issues)
