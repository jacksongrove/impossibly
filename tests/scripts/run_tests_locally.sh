#!/bin/bash
# run_tests_locally.sh
# Script to run tests locally in the Python environment

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default values
TEST_PATH="../"
HELP=false
VERBOSE="-v"
FILTER=""
COV_REPORT=""
COLLECT_ONLY=""

# Parse options
while (( "$#" )); do
  case "$1" in
    -h|--help)
      HELP=true
      shift
      ;;
    -k|--filter)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        FILTER="-k $2"
        shift 2
      else
        echo -e "${RED}Error: Argument for $1 is missing${NC}" >&2
        exit 1
      fi
      ;;
    --path)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        TEST_PATH="../$2"
        shift 2
      else
        echo -e "${RED}Error: Argument for $1 is missing${NC}" >&2
        exit 1
      fi
      ;;
    --no-verbose)
      VERBOSE=""
      shift
      ;;
    --cov)
      COV_REPORT="--cov=imagination-engine --cov-report=term"
      shift
      ;;
    --collect-only)
      COLLECT_ONLY="--collect-only"
      shift
      ;;
    -*) # unsupported flags
      echo -e "${RED}Error: Unsupported flag $1${NC}" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

# Show help message
if [ "$HELP" = true ]; then
  echo -e "${BLUE}Run tests locally in your Python environment${NC}"
  echo ""
  echo "Usage: $0 [options] [pytest_args]"
  echo ""
  echo "Options:"
  echo "  -h, --help                Show this help message"
  echo "  -k, --filter PATTERN      Only run tests matching the given pattern"
  echo "  --path PATH               Path to test directory or file (default: ../ which runs all tests)"
  echo "  --no-verbose              Run tests without verbose output"
  echo "  --cov                     Generate coverage report"
  echo "  --collect-only            Only collect tests, don't execute them"
  echo ""
  echo "Any additional arguments are passed directly to pytest"
  exit 0
fi

# Navigate to the project root directory
cd "$(dirname "$0")/../.." || exit 1
echo -e "${BLUE}Running tests from directory:${NC} $(pwd)"

# Check if virtual environment is active
if [[ -z "${VIRTUAL_ENV}" ]]; then
  echo -e "${YELLOW}Warning: Virtual environment not detected.${NC}"
  echo -e "${YELLOW}It's recommended to run tests within a virtual environment.${NC}"
  
  # Offer to activate the venv if it exists
  if [ -d ".venv" ]; then
    read -p "Activate .venv environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo -e "${BLUE}Activating virtual environment...${NC}"
      source .venv/bin/activate
    fi
  elif [ -d "venv" ]; then
    read -p "Activate venv environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo -e "${BLUE}Activating virtual environment...${NC}"
      source venv/bin/activate
    fi
  fi
fi

# Construct the test command
TEST_CMD="python -m pytest tests/$TEST_PATH $VERBOSE $FILTER $COV_REPORT $COLLECT_ONLY $PARAMS"

# Run the tests
echo -e "${BLUE}Running tests locally...${NC}"
echo -e "${YELLOW}Test command: $TEST_CMD${NC}"
eval $TEST_CMD
TEST_RESULT=$?

# Check if the tests were successful
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}Tests failed. Check the output above for details.${NC}"
    exit 1
fi 