"""
Build a range of XBOW benchmarks by number.

Usage:
    python build_range.py 1 10 --flag MYFLAG
    python build_range.py 5 12 --continue-on-error
"""

import argparse
import os
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build benchmarks from index A through index B (inclusive)."
    )
    parser.add_argument("start", type=int, help="Starting benchmark index (e.g., 1)")
    parser.add_argument("end", type=int, help="Ending benchmark index (e.g., 10)")
    parser.add_argument(
        "--flag",
        help="Flag value passed to the benchmark build (optional).",
    )
    parser.add_argument(
        "--suffix",
        default="24",
        help='Suffix used in benchmark folder names, default: "24".',
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue building remaining benchmarks when one fails.",
    )
    return parser.parse_args()


def generate_ids(start, end, suffix):
    if start > end:
        raise ValueError("start must be <= end")
    return [f"XBEN-{i:03d}-{suffix}" for i in range(start, end + 1)]


def build_benchmark(bench_id, flag, continue_on_error):
    env = os.environ.copy()
    env["BENCHMARK"] = bench_id
    if flag:
        env["FLAG"] = flag

    print(f"\n=== Building {bench_id} ===")
    try:
        subprocess.run(["make", "build"], env=env, check=True)
        print(f"=== Success: {bench_id} ===")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"*** Failed: {bench_id} (exit {exc.returncode})")
        if not continue_on_error:
            raise
        return False


def main():
    args = parse_args()
    try:
        bench_ids = generate_ids(args.start, args.end, args.suffix)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "benchmarks"))
    results = []

    for bench_id in bench_ids:
        bench_path = os.path.join(base_dir, bench_id)
        if not os.path.isdir(bench_path):
            print(f"Skipping {bench_id}: folder not found at {bench_path}")
            results.append(f"{bench_id}: skipped (missing)")
            continue
        try:
            success = build_benchmark(bench_id, args.flag, args.continue_on_error)
            status = "ok" if success else "failed"
        except subprocess.CalledProcessError:
            status = "failed"
        results.append(f"{bench_id}: {status}")
        if status == "failed" and not args.continue_on_error:
            break

    print("\nSummary:")
    for line in results:
        print(f"- {line}")


if __name__ == "__main__":
    main()
