import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MTCFeatures",
    version="0.1",
    author="Peter van Kranenburg",
    author_email="peter.van.kranenburg@meertens.knaw.nl",
    description="Melodies from Meertens Tune Collections as sequences of features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pvankranenburg/MTCFeatures",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={
        'MTCFeatures' : ['data/*.jsonl.gz']
    }
)