import setuptools
import MTCFeatures

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MTCFeatures",
    version=MTCFeatures.__version__,
    license='MIT',
    author="Peter van Kranenburg",
    author_email="peter.van.kranenburg@meertens.knaw.nl",
    description="Melodies from Meertens Tune Collections and Essen Folksong Collection as sequences of features.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pvankranenburg/MTCFeatures",
    keywords = ['Melody','Music','Features'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

