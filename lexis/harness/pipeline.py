"""Lexis pipeline: run the 5-agent chain A→B→C→D→(E × arms) for one trial.

Each stage is a fresh `claude -p` subprocess (no shared context). Stage
transcripts (prompt sent + raw output) are written into the trial directory
for audit. Mirrors eval/harness/runner.py subprocess conventions.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from lexis.harness.spec import StageOutput, extract_answer, extract_json

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_DIR = REPO_ROOT / "lexis"  # v1 layout: prompts/ directly under it

# Sonnet for generation stages (A-D), opus for the measured respondent (E).
# GATE = drift-check judge (cheap).
DEFAULT_STAGE_MODELS = {"A": "sonnet", "B": "sonnet", "C": "sonnet", "D": "sonnet",
                        "E": "opus", "GATE": "haiku"}
STAGE_TIMEOUT_S = 300
DEFAULT_ARMS = ("lexis", "neutral_translation", "control")
DRIFT_MAX_RETRIES = 2  # D regenerations after a failed gate check


def _fill(template: str, **kwargs: str) -> str:
    """Placeholder substitution that tolerates literal braces in templates.

    str.format chokes on the JSON braces in our templates, so replace
    {key} tokens explicitly instead.
    """
    out = template
    for k, v in kwargs.items():
        out = out.replace("{" + k + "}", str(v))
    return out


def _load_template(name: str, config_dir: Path | None = None) -> str:
    return ((config_dir or DEFAULT_CONFIG_DIR) / "prompts" / name).read_text()


def run_stage(
    stage: str,
    prompt: str,
    model: str,
    claude_bin: str,
    trial_dir: Path,
    timeout_s: int = STAGE_TIMEOUT_S,
    parse_json: bool = True,
) -> StageOutput:
    """Invoke one agent; save transcript; parse output.

    Uses claude's --output-format json envelope so the EXACT model versions
    (envelope key `modelUsage`) and cost are recorded per call — the model
    audit trail. If stdout is not an envelope (fakes, older CLIs), it is
    treated as the raw response text.
    """
    t0 = time.monotonic()
    raw, exit_code, status = "", None, "completed"
    model_usage, cost_usd = None, None
    try:
        env = dict(os.environ, LEXIS_STAGE=stage)  # harmless for real claude; lets fakes key off stage
        proc = subprocess.run(
            [claude_bin, "-p", prompt, "--model", model,
             "--output-format", "json", "--dangerously-skip-permissions"],
            cwd=str(trial_dir),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
            env=env,
        )
        raw = proc.stdout
        exit_code = proc.returncode
        try:
            envelope = json.loads(raw)
            if isinstance(envelope, dict) and envelope.get("type") == "result":
                raw = envelope.get("result") or ""
                model_usage = envelope.get("modelUsage")
                cost_usd = envelope.get("total_cost_usd")
                if envelope.get("is_error"):
                    status = "crashed"
        except json.JSONDecodeError:
            pass  # not an envelope — raw stdout is the response text
    except subprocess.TimeoutExpired as e:
        status = "timeout"
        raw = e.stdout or ""
    except Exception as e:  # noqa: BLE001 — harness boundary; record and continue
        status = "crashed"
        raw = f"[{type(e).__name__}] {e}"

    wall = round(time.monotonic() - t0, 3)
    parsed = extract_json(raw) if (parse_json and status == "completed") else None

    (trial_dir / f"stage_{stage}.prompt.txt").write_text(prompt)
    (trial_dir / f"stage_{stage}.raw.txt").write_text(raw)

    return StageOutput(
        stage=stage, prompt=prompt, raw=raw, parsed=parsed,
        wall_s=wall, exit_code=exit_code, status=status,
        model_usage=model_usage, cost_usd=cost_usd,
    )


def run_trial(
    trial_n: int,
    run_id: str,
    seed_hint: str,
    role_hint: str = "any community with a rich register",
    arms: tuple[str, ...] = DEFAULT_ARMS,
    claude_bin: str = "claude",
    work_dir: Path | str = "/home/godli/eval-work",
    stage_models: dict[str, str] | None = None,
    git_sha: str = "unknown",
    preset_topic: dict[str, Any] | None = None,
    preset_role: dict[str, Any] | None = None,
    config_dir: Path | None = None,
    drift_gate: bool = False,
) -> list[dict[str, Any]]:
    """Run one full trial. Returns one result row per arm.

    preset_topic: a vetted stage-A output (topic/demand/answer_instruction/
    allowed_answers). When given, stage A is skipped and the preset is used —
    this is how the human-vetted topic bank feeds the pipeline.
    preset_role: a vetted stage-B output (role/register_notes). When given,
    stage B is skipped — the human-vetted role bank.

    A failed upstream stage aborts the trial: rows are emitted for each arm
    with status='pipeline_failed' and the failing stage recorded.
    """
    models = {**DEFAULT_STAGE_MODELS, **(stage_models or {})}
    trial_id = uuid.uuid4().hex[:12]
    trial_dir = Path(work_dir) / f"lexis-{run_id}" / f"trial-{trial_id}"
    trial_dir.mkdir(parents=True, exist_ok=False)

    stages: dict[str, StageOutput] = {}

    def fail_rows(failed_stage: str) -> list[dict[str, Any]]:
        return [
            _row(run_id, trial_id, trial_n, seed_hint, role_hint, git_sha, models, arm, stages,
                 status="pipeline_failed", failed_stage=failed_stage,
                 answer=None, e_output=None)
            for arm in arms
        ]

    # --- Stage A: topic + demand (skipped when a vetted preset is supplied) ---
    required_a = {"topic", "demand", "answer_instruction", "allowed_answers"}
    if preset_topic is not None:
        if not required_a <= set(preset_topic):
            raise ValueError(f"preset_topic missing keys: {required_a - set(preset_topic)}")
        a = StageOutput(stage="A", prompt="[preset topic — human-vetted bank]",
                        raw=json.dumps(preset_topic), parsed=dict(preset_topic),
                        wall_s=0.0, exit_code=0, status="completed")
        (trial_dir / "stage_A.prompt.txt").write_text(a.prompt)
        (trial_dir / "stage_A.raw.txt").write_text(a.raw)
    else:
        a = run_stage("A", _fill(_load_template("stage_a_topic.md", config_dir), seed_hint=seed_hint),
                      models["A"], claude_bin, trial_dir)
    stages["A"] = a
    if a.parsed is None or not required_a <= set(a.parsed):
        return fail_rows("A")

    # --- Stage B: role (independent — never sees the topic) ---
    required_b = {"role", "register_notes"}
    if preset_role is not None:
        if not required_b <= set(preset_role):
            raise ValueError(f"preset_role missing keys: {required_b - set(preset_role)}")
        b = StageOutput(stage="B", prompt="[preset role — human-vetted bank]",
                        raw=json.dumps(preset_role), parsed=dict(preset_role),
                        wall_s=0.0, exit_code=0, status="completed")
        (trial_dir / "stage_B.prompt.txt").write_text(b.prompt)
        (trial_dir / "stage_B.raw.txt").write_text(b.raw)
    else:
        b = run_stage("B", _fill(_load_template("stage_b_role.md", config_dir), role_hint=role_hint),
                      models["B"], claude_bin, trial_dir)
    stages["B"] = b
    if b.parsed is None or not required_b <= set(b.parsed):
        return fail_rows("B")

    # --- Stage C: lexis (role only; never the topic) ---
    c = run_stage("C", _fill(_load_template("stage_c_lexis.md", config_dir),
                             role=b.parsed["role"],
                             register_notes=b.parsed["register_notes"]),
                  models["C"], claude_bin, trial_dir)
    stages["C"] = c
    if c.parsed is None or "examples" not in c.parsed:
        return fail_rows("C")

    # --- Stage D: translate demand into the lexis (drift-gated when enabled) ---
    d_prompt = _fill(_load_template("stage_d_translate.md", config_dir),
                     demand=a.parsed["demand"],
                     truth_conditions=a.parsed.get("truth_conditions", "(not specified)"),
                     lexis_json=json.dumps(c.parsed, indent=2),
                     answer_instruction=a.parsed["answer_instruction"])
    d = _gated_translation("D", d_prompt, a.parsed, models, claude_bin, trial_dir,
                           stages, config_dir, drift_gate)
    if d is None or d.parsed is None or "translated_prompt" not in d.parsed:
        gate_failed = d is not None and d.status == "drift_gate_failed"
        return fail_rows("D_gate" if gate_failed else "D")

    # --- Stage D_neutral: same lossy translation process, bland register ---
    # (Control for "any thorough rewording shifts answers" vs "the lexis does.")
    d_neutral = None
    if "neutral_translation" in arms:
        dn_prompt = _fill(_load_template("stage_d_neutral.md", config_dir),
                          demand=a.parsed["demand"],
                          truth_conditions=a.parsed.get("truth_conditions", "(not specified)"),
                          answer_instruction=a.parsed["answer_instruction"])
        d_neutral = _gated_translation("D_neutral", dn_prompt, a.parsed, models, claude_bin,
                                       trial_dir, stages, config_dir, drift_gate)
        if d_neutral is None or d_neutral.parsed is None or "translated_prompt" not in d_neutral.parsed:
            gate_failed = d_neutral is not None and d_neutral.status == "drift_gate_failed"
            return fail_rows("D_neutral_gate" if gate_failed else "D_neutral")

    # --- Stage E: one invocation per arm ---
    allowed = [str(x) for x in a.parsed["allowed_answers"]]
    e_prompts = {
        "lexis": d.parsed["translated_prompt"],
        "control": _fill(_load_template("stage_e_control.md", config_dir),
                         demand=a.parsed["demand"],
                         answer_instruction=a.parsed["answer_instruction"]),
    }
    if d_neutral is not None:
        e_prompts["neutral_translation"] = d_neutral.parsed["translated_prompt"]

    # Replay bundle: everything needed to re-run E on identical prompts later
    # (exact replication / added replicates without regenerating A-D).
    bundle = {
        "trial_id": trial_id,
        "trial_n": trial_n,
        "run_id": run_id,
        "git_sha": git_sha,
        "topic": a.parsed.get("topic"),
        "role": b.parsed.get("role"),
        "allowed_answers": allowed,
        "e_prompts": e_prompts,
        "stage_models": models,
    }
    (trial_dir / "bundle.json").write_text(json.dumps(bundle, indent=2))

    rows = []
    for arm in arms:
        e = run_stage(f"E_{arm}", e_prompts[arm], models["E"], claude_bin, trial_dir,
                      parse_json=False)
        if e.status == "crashed":  # infra failure — one retry; unparseable answers are data
            e = run_stage(f"E_{arm}_retry", e_prompts[arm], models["E"], claude_bin, trial_dir,
                          parse_json=False)
        answer = extract_answer(e.raw, allowed) if e.status == "completed" else None
        rows.append(_row(run_id, trial_id, trial_n, seed_hint, role_hint, git_sha, models, arm,
                         stages, status=e.status, failed_stage=None,
                         answer=answer, e_output=e))
    return rows


def _gated_translation(
    stage_name: str,
    prompt: str,
    a_parsed: dict[str, Any],
    models: dict[str, str],
    claude_bin: str,
    trial_dir: Path,
    stages: dict[str, StageOutput],
    config_dir: Path | None,
    drift_gate: bool,
) -> StageOutput | None:
    """Run a translation stage, optionally drift-gated with retries.

    Gate flow: translate -> judge checks semantic equivalence against the
    demand's truth conditions -> on failure, retry the translation with the
    judge's violations appended (up to DRIFT_MAX_RETRIES). Returns the last
    translation StageOutput; returns it even if the final gate failed (caller
    marks the trial drift-failed via the recorded gate stage), or None if the
    translation itself never parsed.
    """
    attempt_prompt = prompt
    out: StageOutput | None = None
    for attempt in range(1 + (DRIFT_MAX_RETRIES if drift_gate else 0)):
        label = stage_name if attempt == 0 else f"{stage_name}_retry{attempt}"
        out = run_stage(label, attempt_prompt, models["D"], claude_bin, trial_dir)
        stages[label] = out
        if out.parsed is None or "translated_prompt" not in out.parsed:
            return out  # unparseable translation — caller fails the trial on the stage

        if not drift_gate:
            return out

        gate_prompt = _fill(_load_template("gate_drift.md", config_dir),
                            demand=a_parsed["demand"],
                            truth_conditions=a_parsed.get("truth_conditions", "(not specified)"),
                            rendering=out.parsed["translated_prompt"])
        gate = run_stage(f"GATE_{label}", gate_prompt, models["GATE"], claude_bin, trial_dir)
        stages[f"GATE_{label}"] = gate
        verdict = gate.parsed or {}
        if verdict.get("equivalent") is True:
            return out
        # Retry with objections appended
        violations = json.dumps(verdict.get("violations", ["gate unparseable"]))
        attempt_prompt = (prompt +
                          "\n\nA semantic checker rejected your previous rendering for these "
                          "violations — fix them while keeping everything else:\n" + violations)

    # Retries exhausted with gate still failing: signal via parsed=None sentinel
    # while keeping the transcript. Caller marks the trial as gate-failed.
    return StageOutput(stage=f"{stage_name}_gate_failed", prompt=out.prompt, raw=out.raw,
                       parsed=None, wall_s=out.wall_s, exit_code=out.exit_code,
                       status="drift_gate_failed", model_usage=out.model_usage,
                       cost_usd=out.cost_usd)


def _row(
    run_id: str, trial_id: str, trial_n: int, seed_hint: str, role_hint: str, git_sha: str,
    models: dict[str, str], arm: str, stages: dict[str, StageOutput],
    status: str, failed_stage: str | None,
    answer: str | None, e_output: StageOutput | None,
) -> dict[str, Any]:
    from datetime import datetime

    a = stages.get("A")
    b = stages.get("B")
    return {
        "run_id": run_id,
        "trial_id": trial_id,
        "trial_n": trial_n,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "git_sha": git_sha,
        "seed_hint": seed_hint,
        "role_hint": role_hint,
        "arm": arm,
        "status": status,
        "failed_stage": failed_stage,
        "topic": (a.parsed or {}).get("topic") if a else None,
        "demand": (a.parsed or {}).get("demand") if a else None,
        "allowed_answers": (a.parsed or {}).get("allowed_answers") if a else None,
        "role": (b.parsed or {}).get("role") if b else None,
        "answer": answer,
        "e_wall_s": e_output.wall_s if e_output else None,
        "e_brief": e_output.brief() if e_output else None,
        "stage_briefs": [s.brief() for s in stages.values()],
        "stage_models": models,
    }
