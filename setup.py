from setuptools import setup, find_packages

setup(
    name="imagination-engine",  # Your package name. Note: distribution names can include hyphens.
    version="0.1.0",
    packages=find_packages(),  # Automatically finds all packages in your project
    install_requires=[
        "openai",
        "anthropic",
        "python-dotenv",
        # add other dependencies as needed
    ],
    description="An agentic architecture for idea generation & critical thinking",
    author="Jackson Grove",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
) 