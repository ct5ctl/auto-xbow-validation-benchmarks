#!/bin/bash
# Script to run a specific benchmark
# Usage: ./run_benchmark.sh XBEN-006-24

if [ -z "$1" ]; then
    echo "Usage: $0 <BENCHMARK_ID>"
    echo "Example: $0 XBEN-006-24"
    exit 1
fi

BENCHMARK=$1
make run BENCHMARK=$BENCHMARK
