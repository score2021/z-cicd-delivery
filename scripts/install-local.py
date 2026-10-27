#!/usr/bin/env python3
"""Install only this skill's runtime resources; no network, overwrite or shell execution."""
import argparse
import os
from pathlib import Path
import shutil
import sys

NAME = 'z-cicd-delivery'
RUNTIME = (
    'SKILL.md', 'LICENSE', 'agents/openai.yaml',
    'references/delivery-workflow.md', 'references/failure-patterns.md',
    'references/acceptance-recovery.md', 'references/operations-postmortem.md',
)


def install(source, target):
    source, target = Path(source), Path(target)
    if target.name != NAME:
        raise ValueError('destination_must_end_with_skill_name')
    if os.path.lexists(target):
        raise FileExistsError('destination_exists_not_overwritten')
    payload = {}
    for name in RUNTIME:
        p = source / name
        relative = Path(name)
        if any((source / Path(*relative.parts[:i])).is_symlink()
               for i in range(1, len(relative.parts) + 1)):
            raise ValueError('runtime_symlink_refused')
        if not p.is_file():
            raise ValueError('runtime_file_missing:' + name)
        payload[name] = p.read_bytes()
    if b'name: z-cicd-delivery' not in payload['SKILL.md']:
        raise ValueError('unexpected_skill_identity')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()  # exclusive: protects existing targets, including a concurrent installation
    try:
        for name, data in payload.items():
            p = target / name
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as f:
                f.write(data)
    except BaseException:
        shutil.rmtree(target)  # only this call's newly created destination
        raise
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dest', type=Path,
                    help='full new skill directory; default: ~/.agents/skills/z-cicd-delivery')
    args = ap.parse_args()
    if args.dest is None:
        legacy = Path.home() / '.codex' / 'skills' / NAME
        if os.path.lexists(legacy):
            raise FileExistsError('legacy_install_exists_resolve_duplicate_first')
    target = args.dest if args.dest is not None else Path.home() / '.agents' / 'skills' / NAME
    result = install(Path(__file__).resolve().parent.parent, target)
    print('Installed: ' + str(result))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print('Install refused: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
