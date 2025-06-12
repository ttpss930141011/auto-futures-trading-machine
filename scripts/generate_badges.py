#!/usr/bin/env python3
"""
Script to generate badges locally for testing.
This script simulates what GitHub Actions does to generate badges.
"""

import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def run_command(command):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return "", str(e), 1


def get_pylint_score():
    """Get pylint score."""
    print("Running pylint...")
    stdout, stderr, returncode = run_command("poetry run pylint src/ --disable=all --enable=E,W --output-format=text --reports=yes")
    
    # Extract score from output
    for line in stdout.split('\n'):
        if "Your code has been rated at" in line:
            try:
                score = line.split("Your code has been rated at")[1].split("/10")[0].strip()
                return float(score)
            except (IndexError, ValueError):
                pass
    
    print("Could not extract pylint score from output")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
    return 0.0


def get_coverage_percentage():
    """Get test coverage percentage."""
    print("Running tests with coverage...")
    stdout, stderr, returncode = run_command("poetry run pytest --cov=src --cov-report=xml --cov-report=term-missing")
    
    # Parse coverage.xml
    try:
        tree = ET.parse('coverage.xml')
        root = tree.getroot()
        coverage = float(root.attrib['line-rate']) * 100
        return coverage
    except Exception as e:
        print(f"Error parsing coverage.xml: {e}")
        return 0.0


def get_color(value, thresholds):
    """Get color based on value and thresholds."""
    if value >= thresholds[0]:
        return "brightgreen"
    elif value >= thresholds[1]:
        return "green"
    elif value >= thresholds[2]:
        return "yellowgreen"
    elif value >= thresholds[3]:
        return "yellow"
    elif value >= thresholds[4]:
        return "orange"
    else:
        return "red"


def create_badge_json(label, message, color):
    """Create badge JSON."""
    return {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color
    }


def main():
    """Main function."""
    # Create badges directory
    badges_dir = Path(".github/badges")
    badges_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate pylint badge
    pylint_score = get_pylint_score()
    pylint_color = get_color(pylint_score, [9.0, 8.0, 7.0, 6.0, 5.0])
    pylint_badge = create_badge_json("pylint", f"{pylint_score:.1f}/10", pylint_color)
    
    with open(badges_dir / "pylint.json", "w") as f:
        json.dump(pylint_badge, f, indent=2)
    
    print(f"✅ Pylint badge generated: {pylint_score:.1f}/10 ({pylint_color})")
    
    # Generate coverage badge
    coverage = get_coverage_percentage()
    coverage_color = get_color(coverage, [90, 80, 70, 60, 50])
    coverage_badge = create_badge_json("coverage", f"{coverage:.1f}%", coverage_color)
    
    with open(badges_dir / "coverage.json", "w") as f:
        json.dump(coverage_badge, f, indent=2)
    
    print(f"✅ Coverage badge generated: {coverage:.1f}% ({coverage_color})")
    
    print("\n📍 Badge files created:")
    print(f"  - {badges_dir / 'pylint.json'}")
    print(f"  - {badges_dir / 'coverage.json'}")
    
    print("\n🔗 To use in README.md:")
    print(f"  Pylint: ![Pylint](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/YOUR_BRANCH/.github/badges/pylint.json)")
    print(f"  Coverage: ![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/YOUR_BRANCH/.github/badges/coverage.json)")


if __name__ == "__main__":
    main()