"""
SEAA - Self-Evolving Autonomous Agent

Setup configuration for pip installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Core dependencies (always required)
install_requires = [
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "watchdog>=3.0",
]

# Optional CLI dependencies
extras_require = {
    "cli": [
        "rich>=13.0",
        "prompt-toolkit>=3.0",
    ],
    "dev": [
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "black>=23.0",
        "flake8>=6.0",
        "mypy>=1.0",
    ],
    "all": [
        "rich>=13.0",
        "prompt-toolkit>=3.0",
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "black>=23.0",
        "flake8>=6.0",
        "mypy>=1.0",
    ],
}

setup(
    name="seaa",
    version="1.0.0",
    description="Self-Evolving Autonomous Agent - Code that writes itself",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sutraworks Labs",
    author_email="info@sutraworks.ai",
    url="https://github.com/sutraworks/seaa",
    license="MIT",
    packages=find_packages(exclude=["tests", "docs", "soma"]),
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agent autonomous self-evolving llm code-generation",
    entry_points={
        "console_scripts": [
            "seaa=seaa.cli:run_interactive",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
