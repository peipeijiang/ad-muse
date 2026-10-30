#!/usr/bin/env python3
"""Check and install AdMuse companion skills.

Existing skills are never overwritten. Missing skills are fetched from the
GitHub source listed in dependencies.json. Local tools and Whisper weights are
only checked; nothing is downloaded for ASR.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
MANIFEST = SKILL_DIR / "dependencies.json"
DEFAULT_ROOTS = [Path.home() / ".agents" / "skills", Path.home() / ".codex" / "skills"]
PYTHON_CANDIDATES = [sys.executable, "python3", "python", "/opt/anaconda3/bin/python",
                     "/opt/homebrew/bin/python3", "/usr/local/bin/python3"]


def find_installed(name, roots):
    for root in roots:
        if (root / name / "SKILL.md").is_file():
            return root / name
    return None


def local_bundle(path):
    """Return a bundled skill directory when running from a repository checkout."""
    repo_root = SKILL_DIR.parent.parent
    if not path or not (repo_root / "install.py").is_file():
        return None
    candidate = repo_root / path
    return candidate if (candidate / "SKILL.md").is_file() else None


def fetch_github(repo, ref, path, workdir):
    """Shallow, sparse clone; returns the directory that contains SKILL.md."""
    dest = workdir / "src"
    url = f"https://github.com/{repo}.git"
    clone = ["git", "clone", "--depth", "1", "--branch", ref, "--filter=blob:none"]
    if path:
        clone += ["--sparse"]
    subprocess.run(clone + [url, str(dest)], check=True, capture_output=True, text=True)
    if path:
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", path],
                       check=True, capture_output=True, text=True)
    src = dest / path if path else dest
    if not (src / "SKILL.md").is_file():
        raise RuntimeError(f"SKILL.md not found at {repo}/{path or '.'}")
    return src


def install_skill(dep, target):
    final = target / dep["name"]
    if final.exists():
        raise RuntimeError(f"{final} already exists; not overwriting")
    source = dep["source"]
    target.mkdir(parents=True, exist_ok=True)
    part = target / f".{dep['name']}.part"
    if part.exists():
        raise RuntimeError(f"Leftover {part}; inspect and move it away first")
    with tempfile.TemporaryDirectory(prefix="ad-muse-") as tmp:
        src = local_bundle(source.get("path")) if source["type"] == "bundled" else None
        origin = "local bundle" if src else f"github:{source['github']}/{source.get('path') or '.'}@{source['ref']}"
        if src is None:
            src = fetch_github(source["github"], source["ref"], source.get("path", ""), Path(tmp))
        shutil.copytree(src, part, ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"))
    os.replace(part, final)
    return origin


def whisper_python():
    seen = set()
    for cand in PYTHON_CANDIDATES:
        exe = shutil.which(cand) or (cand if Path(cand).is_file() else None)
        if not exe or exe in seen:
            continue
        seen.add(exe)
        probe = subprocess.run([exe, "-c", "import whisper,json;print(json.dumps({'v':whisper.__version__,"
                                "'u':whisper._MODELS.get('large-v3-turbo','')}))"],
                               capture_output=True, text=True)
        if probe.returncode == 0:
            info = json.loads(probe.stdout.strip().splitlines()[-1])
            return exe, info
    return None, None


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_asr(cfg, verify_hash):
    exe, info = whisper_python()
    rows = []
    if not exe:
        return [{"item": "openai-whisper", "status": "missing", "detail": "No Python imports whisper; reference ASR unavailable"}]
    rows.append({"item": "openai-whisper", "status": "ok", "detail": f"{exe} (whisper {info['v']})"})
    cache = Path.home() / ".cache" / "whisper"
    for model in [cfg["default_model"], *cfg.get("alternatives", [])]:
        weights = cache / f"{model}.pt"
        if not weights.is_file():
            rows.append({"item": f"whisper:{model}", "status": "missing", "detail": "not downloaded (installer never downloads)"})
            continue
        status, detail = "present", f"{weights.stat().st_size:,} bytes"
        if verify_hash and model == cfg["default_model"] and info.get("u"):
            ok = sha256(weights) == info["u"].split("/")[-2]
            status, detail = ("ok" if ok else "invalid"), detail + (", official SHA-256 verified" if ok else ", SHA-256 mismatch")
        rows.append({"item": f"whisper:{model}", "status": status, "detail": detail})
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true", help="Only report; install nothing")
    p.add_argument("--target", type=Path, default=DEFAULT_ROOTS[0], help="Install directory for missing skills (default: ~/.agents/skills)")
    p.add_argument("--roots", type=Path, nargs="+", help="Skill roots to search (default: ~/.agents/skills ~/.codex/skills)")
    p.add_argument("--verify-asr-hash", action="store_true", help="Hash large-v3-turbo weights (about 1.6 GB read)")
    p.add_argument("--json", action="store_true", help="Print machine-readable results")
    args = p.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    roots = [r.expanduser() for r in (args.roots or DEFAULT_ROOTS)]
    if args.target.expanduser() not in roots:
        roots.insert(0, args.target.expanduser())
    results, failed_required = [], False

    if not args.check and shutil.which("git") is None:
        print("git is required to install missing skills", file=sys.stderr)
        return 2

    for dep in manifest["skills"]:
        found = find_installed(dep["name"], roots)
        row = {"kind": "skill", "item": dep["name"], "role": dep["role"]}
        if found:
            row.update(status="installed", detail=str(found))
        elif args.check:
            row.update(status="missing", detail="run without --check to install")
            failed_required = True
        else:
            try:
                origin = install_skill(dep, args.target.expanduser())
                row.update(status="added", detail=f"{args.target.expanduser() / dep['name']} <- {origin}")
            except (subprocess.CalledProcessError, RuntimeError, OSError) as exc:
                msg = exc.stderr.strip().splitlines()[-1] if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
                row.update(status="error", detail=msg)
                failed_required = True
        results.append(row)

    for tool in manifest["tools"]:
        path = shutil.which(tool["name"])
        status = "ok" if path else ("missing" if tool["required"] else "optional-missing")
        detail = path or tool.get("install_hint", tool["purpose"])
        failed_required |= bool(tool["required"] and not path)
        results.append({"kind": "tool", "item": tool["name"], "status": status, "detail": detail})

    for row in check_asr(manifest["asr"], args.verify_asr_hash):
        results.append({"kind": "asr", **row})

    if args.json:
        print(json.dumps({"ok": not failed_required, "results": results}, ensure_ascii=False, indent=2))
    else:
        width = max(len(r["item"]) for r in results)
        for r in results:
            print(f"{r['kind']:<5}  {r['item']:<{width}}  {r['status']:<16}  {r['detail']}")
        print("\nAll required dependencies are available." if not failed_required
              else "\nSome required dependencies are missing or failed; see the rows above.")
    return 1 if failed_required else 0


if __name__ == "__main__":
    sys.exit(main())
