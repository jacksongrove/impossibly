from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Base dependencies that are always required
core_requires = [
    "python-dotenv>=1.0.0",
]

setup(
    name="imengine",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=core_requires,
    extras_require={
        # OpenAI integration
        "openai": ["openai>=1.0.0"],
        # Anthropic integration
        "anthropic": ["anthropic>=0.4.0"],
        # Install all integrations
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.4.0",
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