"""
Command-line interface for running tests for Impossibly.
"""
import os
import subprocess
import sys
from pathlib import Path

import click


@click.group()
def tests():
    """Run tests for Impossibly."""
    pass


@tests.command()
@click.option(
    "--path",
    default=None,
    help="Path to test directory or file (relative to tests directory)",
)
@click.option("-k", "--filter", default=None, help="Only run tests matching the given pattern")
@click.option("--no-verbose", is_flag=True, help="Run tests without verbose output")
@click.option("--cov", is_flag=True, help="Generate coverage report")
@click.option("--collect-only", is_flag=True, help="Only collect tests, don't execute them")
@click.option("--docker", is_flag=True, help="Run tests in Docker")
@click.option("--clean", is_flag=True, help="Clean up pytest cache and other temporary test files")
@click.option("--clean-docker", is_flag=True, help="Clean up Docker test containers and images")
@click.pass_context
def run(
    ctx, path, filter, no_verbose, cov, collect_only, docker, clean, clean_docker
):
    """Run tests for Impossibly."""
    # Find the project root
    project_root = find_project_root()
    
    # Construct the command
    if docker:
        run_tests_in_docker(project_root, path, filter, no_verbose, clean, clean_docker)
    else:
        run_tests_locally(
            project_root, path, filter, no_verbose, cov, collect_only, clean
        )


def find_project_root():
    """Find the root directory of the project."""
    # Start at the current directory
    current_dir = Path.cwd()
    
    # Go up until we find setup.py or reach the root
    while current_dir != current_dir.parent:
        if (current_dir / "setup.py").exists():
            return current_dir
        current_dir = current_dir.parent
    
    # If we reach here, we couldn't find the project root
    click.echo("Error: Could not find project root (directory with setup.py)", err=True)
    sys.exit(1)


def run_tests_locally(
    project_root, path, filter, no_verbose, cov, collect_only, clean
):
    """Run tests locally."""
    # Change to the project root
    os.chdir(project_root)
    
    # Try to find pytest directly rather than relying on python -m
    try:
        # Try running pytest directly
        subprocess.run(["pytest", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        cmd = ["pytest"]
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fall back to python -m pytest
        cmd = [sys.executable, "-m", "pytest"]
    
    # Add path
    if path:
        cmd.append(f"tests/{path}")
    else:
        cmd.append("tests/")
    
    # Add options
    if not no_verbose:
        cmd.append("-v")
    
    if filter:
        cmd.append(f"-k {filter}")
    
    if cov:
        cmd.append("--cov=impossibly")
        cmd.append("--cov-report=term")
    
    if collect_only:
        cmd.append("--collect-only")
    
    # If clean, remove pycache first
    if clean:
        click.echo("Cleaning up test directories...")
        clean_command = f"find {project_root} -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type d -name '*.egg-info' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type d -name '.pytest_cache' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type f -name '*.pyc' -delete"
        subprocess.run(clean_command, shell=True)
        click.echo("Cleanup complete!")
    
    # Run the command
    click.echo(f"Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # Check the result
    if result.returncode == 0:
        click.echo(click.style("All tests passed successfully!", fg="green"))
    else:
        click.echo(click.style(f"Tests failed with exit code: {result.returncode}", fg="red"))
        sys.exit(result.returncode)


def run_tests_in_docker(project_root, path, filter, no_verbose, clean, clean_docker):
    """Run tests in Docker."""
    # Change to the project root
    os.chdir(project_root)
    
    # Build the Docker command
    cmd = ["docker", "compose", "-f", "tests/scripts/compose.test.yml"]
    
    # Clean Docker if requested
    if clean_docker:
        click.echo("Cleaning up Docker test resources...")
        subprocess.run([*cmd, "down"], check=False)
        subprocess.run(["docker", "rmi", "-f", "impossibly-v2-test"], check=False, stderr=subprocess.PIPE)
        click.echo("Docker cleanup complete!")
    
    # Clean files if requested
    if clean:
        click.echo("Cleaning up test directories...")
        clean_command = f"find {project_root} -type d -name '__pycache__' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type d -name '*.egg-info' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type d -name '.pytest_cache' -exec rm -rf {{}} + 2>/dev/null || true"
        subprocess.run(clean_command, shell=True)
        clean_command = f"find {project_root} -type f -name '*.pyc' -delete"
        subprocess.run(clean_command, shell=True)
        click.echo("Cleanup complete!")
    
    # Build the container
    click.echo("Building Docker test container...")
    build_cmd = [*cmd, "build"]
    build_result = subprocess.run(build_cmd)
    if build_result.returncode != 0:
        click.echo(click.style("Docker build failed!", fg="red"))
        sys.exit(build_result.returncode)
    
    # Run tests in Docker
    run_cmd = [*cmd, "run", "--rm", "test"]
    
    # Add options
    if path:
        run_cmd.append(path)
    
    if filter:
        run_cmd.append(f"-k {filter}")
    
    if no_verbose:
        run_cmd.append("--no-verbose")
    
    # Run the command
    click.echo(f"Running tests in Docker: {' '.join(run_cmd)}")
    result = subprocess.run(run_cmd)
    
    # Check the result
    if result.returncode == 0:
        click.echo(click.style("All tests passed successfully!", fg="green"))
    else:
        click.echo(click.style(f"Tests failed with exit code: {result.returncode}", fg="red"))
        sys.exit(result.returncode)


if __name__ == "__main__":
    tests()

# Explicitly export the 'tests' function for entry points
__all__ = ['tests'] 