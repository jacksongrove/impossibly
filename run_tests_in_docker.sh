#!/bin/bash
# run_tests_in_docker.sh
# Script to build and run Docker containers for testing the imagination-engine library.
# 
# This script runs the feature tests in the 'tests/' directory, which test:
# - Agent functionality and interaction (tests/features/test_agent_interaction.py)
# - Image handling capabilities (tests/features/test_image_capabilities.py)
# - Tool functionality and integration (tests/features/test_tools.py)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default values
TEST_PATH="tests/"
HELP=false
VERBOSE="-v"
FILTER=""
PARAMS=""
CLEAN=false
CLEAN_DOCKER=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      HELP=true
      shift
      ;;
    -k|--filter)
      FILTER="-k $2"
      shift
      shift
      ;;
    -p|--path)
      TEST_PATH="$2"
      shift
      shift
      ;;
    --no-verbose)
      VERBOSE=""
      shift
      ;;
    --clean)
      CLEAN=true
      shift
      ;;
    --clean-docker)
      CLEAN_DOCKER=true
      shift
      ;;
    *)
      # Additional parameters to pass to pytest
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

# Display help message
if [ "$HELP" = true ]; then
  echo -e "${BLUE}Usage:${NC} ./run_tests_in_docker.sh [options]"
  echo
  echo "Options:"
  echo "  -h, --help       Show this help message"
  echo "  -k, --filter     Filter tests by keyword expression"
  echo "  -p, --path       Specify test path (default: tests/)"
  echo "  --no-verbose     Run tests without verbose output"
  echo "  --clean          Clean up pytest cache and other temporary test files"
  echo "  --clean-docker   Clean up Docker test containers and images"
  echo
  echo "Examples:"
  echo "  ./run_tests_in_docker.sh                         # Run all tests"
  echo "  ./run_tests_in_docker.sh -k 'tools'              # Run tests containing 'tools'"
  echo "  ./run_tests_in_docker.sh -p tests/features/      # Run only feature tests"
  echo "  ./run_tests_in_docker.sh --clean                 # Clean up test cache files"
  echo "  ./run_tests_in_docker.sh --clean-docker          # Clean up Docker test resources"
  exit 0
fi

# Clean up Docker resources
if [ "$CLEAN_DOCKER" = true ]; then
  echo -e "${BLUE}Cleaning up Docker test resources...${NC}"
  
  # Stop and remove test containers
  docker compose -f compose.test.yml down 2>/dev/null || true
  
  # Remove test images
  docker rmi -f imagination-engine-v2-test 2>/dev/null || true
  
  echo -e "${GREEN}Docker cleanup complete!${NC}"
  
  # Exit if only Docker cleaning was requested
  if [ "$CLEAN" = false ] && [ "$TEST_PATH" == "tests/" ] && [ -z "$FILTER" ] && [ -z "$PARAMS" ]; then
    exit 0
  fi
fi

# Clean up operation
if [ "$CLEAN" = true ]; then
  echo -e "${BLUE}Cleaning up test directories...${NC}"
  
  # Remove pytest cache
  find . -type d -name "__pycache__" -exec rm -rf {} +  2>/dev/null || true
  find . -type d -name "*.egg-info" -exec rm -rf {} +  2>/dev/null || true
  find . -type d -name ".pytest_cache" -exec rm -rf {} +  2>/dev/null || true
  find . -type f -name "*.pyc" -delete
  
  # Remove coverage data
  rm -f .coverage
  rm -rf htmlcov/
  
  echo -e "${GREEN}Cleanup complete!${NC}"
  
  # Exit if only cleaning was requested
  if [ "$TEST_PATH" == "tests/" ] && [ -z "$FILTER" ] && [ -z "$PARAMS" ]; then
    exit 0
  fi
fi

# Build the Docker containers
echo -e "${BLUE}Building Docker containers for imagination-engine tests...${NC}"
docker compose -f compose.test.yml build

# Check if the build was successful
if [ $? -ne 0 ]; then
  echo -e "${RED}Error: Docker build failed.${NC}"
  exit 1
fi

echo -e "${GREEN}Build successful!${NC}"

# When using ENTRYPOINT in Dockerfile, 'docker run' arguments are passed to the ENTRYPOINT
# We need to pass our test path, filter and other parameters directly
TEST_CMD="docker compose -f compose.test.yml run --rm test $TEST_PATH $FILTER $PARAMS"

# Run the tests
echo -e "${BLUE}Running imagination-engine tests: ${TEST_CMD}${NC}"
$TEST_CMD

# Check if the tests were successful
if [ $? -ne 0 ]; then
  echo -e "${RED}Tests failed.${NC}"
  exit 1
else
  echo -e "${GREEN}All tests passed!${NC}"
fi 