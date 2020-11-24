import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="walksignal-threexc"
    version="0.0.1",
    author="Trevor Gamblin",
    author_email="tvgamblin@gmail.com",
    description="A library for parsing and plotting OpenCellID data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/threexc/walksignal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
