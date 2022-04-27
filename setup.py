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
    entry_points={"console_scripts": ["mailbagit=mailbag:cli", "mailbagit-gui=mailbag:gui"]},
    install_requires=[
        "bagit>=1.8.1,<2",
        "beautifulsoup4>=4.11.1,<5" "black>=22.1.0,<23",
        "gooey>=1.0.8.1,<2",
        "jsonmodels>=2.2,<=2.5.0",
        "extract_msg>=0.30.10,<1",
        "structlog>=21.1.0,<22",
        "pytest>=7.0.1,<8",
        "python-dotenv>0.19.0,<=0.19.1",
        "RTFDE>=0.0.2",
        "chardet>=4.0.0,<5",
        "warcio>=1.7.4,<2",
        "requests >=2.27.1,<3",
        # for black
        "typed-ast>=1.5.3,<2",
    ],
    python_requires=">=3.7",
)
