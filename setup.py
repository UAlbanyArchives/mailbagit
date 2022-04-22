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
        "console_scripts": ["mailbagit=mailbag:cli", "mailbagit-gui=mailbag:gui"]
    },
    install_requires=[
        "bagit>=1.8.1,<2",
        "beautifulsoup4>=4.11.1,<5",
        "gooey>=1.0.8.1,<2",
        "jsonmodels>=2.2,<=2.5.0",
        "extract_msg>=0.30.10",
        "structlog>=18.1.0,<=21.1.0",
        "python-dotenv>0.19.0,<=0.19.1",
        "RTFDE>=0.0.2",
        "chardet>=4.0.0",
        "warcio>=1.7.4,<2",
        "requests >=2.27.1,<3",
    ],
    python_requires=">=3.6",
)
