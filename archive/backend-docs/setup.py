from setuptools import setup, find_packages

setup(
    name="deepshell",
    version="1.0.0",
    description="A command-line productivity tool powered by OpenAI LLM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="DeepShell Team",
    author_email="muralipala1504@gmail.com",
    url="https://github.com/muralipala1504/deepshell",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "litellm>=1.0.0",
        "python-dotenv>=0.19.0",
        "prompt-toolkit>=3.0.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deepshell=deepshell.cli:app",
            "ds=deepshell.cli:app",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
)
