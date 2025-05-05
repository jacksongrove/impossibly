from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Base dependencies that are always required
core_requires = [
    "python-dotenv>=1.0.0",
    "click>=8.0.0",  # For CLI commands
    "openai>=1.0.0",  # OpenAI API client
    "anthropic>=0.4.0",  # Anthropic API client
]

# LLM provider dependencies
openai_requires = ["openai>=1.0.0"]
anthropic_requires = ["anthropic>=0.4.0"]
all_llm_requires = openai_requires + anthropic_requires

# Testing dependencies (without LLM clients)
testing_core = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0", 
    "mock>=5.0.0",
]

# Testing with all LLM clients included
test_requires = testing_core + all_llm_requires

# Dev dependencies include testing plus linting/formatting tools
dev_requires = test_requires + [
    "black>=23.0.0",
    "flake8>=6.0.0", 
    "isort>=5.0.0",
    "mypy>=1.0.0",
    "build>=1.0.0",
    "wheel>=0.40.0",
    "twine>=4.0.0",
    "setuptools>=61.0.0",
]

setup(
    name="imagination-engine",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=core_requires,
    extras_require={
        # Individual LLM integrations
        "openai": openai_requires,
        "anthropic": anthropic_requires,
        
        # All LLM integrations
        "all": all_llm_requires,
        
        # Testing (includes all LLM clients)
        "test": test_requires,
        
        # For development (includes testing + dev tools)
        "dev": dev_requires,
    },
    entry_points={
        "console_scripts": [
            "imagination-engine=imagination_engine.cli.test_commands:tests",
        ],
    },
    description="An agentic architecture for idea generation & critical thinking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Jackson Grove",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai, agents, llm, orchestration, tools, agentic, architecture",
    python_requires=">=3.9",
    project_urls={
        "Homepage": "https://github.com/jacksongrove/imagination-engine",
        "Bug Reports": "https://github.com/jacksongrove/imagination-engine/issues",
        "Documentation": "https://github.com/jacksongrove/imagination-engine/blob/main/README.md",
    },
) 