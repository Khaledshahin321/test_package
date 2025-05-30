from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="automata-theory-tools",
    version="0.1.0",
    author="Your Name",
    author_email="naser.gahen71@yahoo.com",
    description="A package for automata theory tools like DFA minimization and CFG to CNF conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Khaledshahin321/test_package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
