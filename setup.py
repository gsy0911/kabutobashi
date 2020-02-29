import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pystock",
    version="0.0.1",
    author="gsy0911",
    author_email="yoshiki0911@gmail.com",
    description="Analyze stock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gsy0911/pystock",
    packages=['pystock'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)