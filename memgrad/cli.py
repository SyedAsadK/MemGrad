from __future__ import annotations

import argparse
import os

from .memory import MemoryStore
from .optimizer import MemGradOptimizer


def _build_optimizer():
    return MemGradOptimizer(memory_store=MemoryStore())


def cmd_record(args):
    optimizer = _build_optimizer()
    optimizer.record_failure(
        role=args.role,
        task=args.task,
        failure=args.failure,
        resolution=args.resolution,
        trace=args.trace,
    )
    print(f"Recorded memory for role: {args.role}")


def cmd_optimize(args):
    optimizer = _build_optimizer()
    improved = optimizer.build_role_prompt(
        role=args.role,
        base_prompt=args.prompt,
        task=args.task,
        failure=args.failure,
    )
    print(improved)


def cmd_summary(args):
    optimizer = _build_optimizer()
    print(optimizer.retrospective_summary(args.role))


def main():
    parser = argparse.ArgumentParser(description="MemGrad command-line interface")
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="Store a retrospective failure/resolution pair")
    rec.add_argument("--role", required=True)
    rec.add_argument("--task", required=True)
    rec.add_argument("--failure", required=True)
    rec.add_argument("--resolution", required=True)
    rec.add_argument("--trace", default=None)
    rec.set_defaults(func=cmd_record)

    opt = sub.add_parser("optimize", help="Improve a prompt using stored memory")
    opt.add_argument("--role", required=True)
    opt.add_argument("--task", required=True)
    opt.add_argument("--failure", required=True)
    opt.add_argument("--prompt", required=True)
    opt.set_defaults(func=cmd_optimize)

    sump = sub.add_parser("summary", help="Print historical memory for a role")
    sump.add_argument("--role", required=True)
    sump.set_defaults(func=cmd_summary)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
