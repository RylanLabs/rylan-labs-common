#!/usr/bin/env python3
import yaml
import sys
import os

def get_report(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Scorecard not found at {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    
    criteria = data.get('criteria', {})
    statuses = []
    for key, value in sorted(criteria.items()):
        status = value.get('status', 'PENDING')
        statuses.append(status)
        # print(f"{status}: {key}") # Optional detailed view

    from collections import Counter
    counts = Counter(statuses)
    for status, count in sorted(counts.items()):
        print(f"{count:7} {status}")
    
    print(f"\nOverall Score: {data.get('overall_score', '0.0/10')}")
    print(f"Status: {data.get('status', 'PENDING')}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ".audit/maturity-level-5-scorecard.yml"
    get_report(path)
