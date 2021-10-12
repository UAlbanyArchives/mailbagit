# /usr/bin/env python3
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mailbag",  # Replace with your own username
    version="0.0.1",
    author="Gregory Wiedeman",
    author_email="gwiedeman@albany.edu",
    description="A tool for preserving email with multiple masters.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UAlbanyArchives/mailbag",
    packages=setuptools.find_namespace_packages(exclude=("tests")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mailbagit=mailbag:cli",
            "mailbagit-gui=mailbag:gui"
        ]
    },
    install_requires=["bagit>=1.8.1,<2", "gooey>=1.0.8.1,<2", "jsonmodels>=2.2,<=2.5.0", "extract_msg>=0.23.4,<=0.28.6", "structlog>=18.1.0,<=21.1.0"],
    python_requires=">=3.6",
)
