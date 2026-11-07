"""The full flow: requirements -> design -> 3D model -> analysis, with JSON output."""
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from aero_ai.schemas import Requirements, Design, Issue, Results
from aero_ai.templates.fixed_wing.template import FixedWingTemplate

TEMPLATES = {t.name: t for t in (FixedWingTemplate(),)}


@dataclass
class PipelineResult:
    requirements: Requirements
    design: Optional[Design] = None
    results: Optional[Results] = None
    files: list = field(default_factory=list)
    issues: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.design is not None and not any(i.severity == "error" for i in self.issues)


def run_pipeline(req: Requirements, out_dir: str = "outputs") -> PipelineResult:
    template = TEMPLATES.get(req.aircraft_type)
    if template is None:
        supported = ", ".join(sorted(TEMPLATES))
        raise ValueError(f"Unsupported aircraft type '{req.aircraft_type}'. Supported: {supported}")

    out = PipelineResult(requirements=req)

    # Step 1: size the aircraft (can fail if the requirements are unrealistic)
    try:
        design = template.size(req)
    except RuntimeError as err:
        out.issues.append(Issue("error", f"Sizing failed: {err}"))
        _save(out, out_dir)
        return out

    # Step 2: reality check before spending time on CAD and simulation
    out.design = design
    out.issues.extend(template.validate(design))
    if any(i.severity == "error" for i in out.issues):
        _save(out, out_dir)
        return out

    # Step 3: tune the layout, build the 3D model, analyze the final design
    try:
        out.design = template.refine(design, req)
    except RuntimeError as err:
        out.issues.append(Issue("error", f"Layout tuning failed: {err}"))
        _save(out, out_dir)
        return out
    out.files = template.build_geometry(out.design, out_dir)
    out.results = template.analyze(out.design, req)
    out.issues.extend(out.results.issues)
    _save(out, out_dir)
    return out


def _save(result: PipelineResult, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    data = asdict(result)
    data["ok"] = result.ok
    with open(os.path.join(out_dir, "result.json"), "w") as f:
        json.dump(data, f, indent=2)
