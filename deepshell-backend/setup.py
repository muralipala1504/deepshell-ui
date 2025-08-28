from setuptools import setup, find_packages

setup(
    name="deepshell",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "litellm==1.74.9.post1",
        "python-dotenv>=0.19.0",
        "prompt-toolkit>=3.0.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "deepshell=deepshell.cli:main",  # Adjust if your CLI entry point differs
        ],
    },
)
