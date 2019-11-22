import setuptools
import requests
import sys
from pathlib import Path
from setuptools.command.install import install

def download(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                sys.stdout.flush()
    sys.stdout.write('\n')
        

class MTCFeaturesInstall(install):
    def run(self):
        self.download_datafiles()
        install.run(self)

    def download_datafiles(self):
        mtcfsinstdatafile = 'MTC-FS-INST-2.0_sequences-1.1.jsonl.gz'
        mtcanndatafile = 'MTC-ANN-2.0.1_sequences-1.1.jsonl.gz'
        essendatafile = 'essen_sequences-1.1.jsonl.gz'
        
        fsinstpath = Path('MTCFeatures','data', mtcfsinstdatafile)
        annpath = Path('MTCFeatures','data', mtcanndatafile)
        essenpath = Path('MTCFeatures','data', essendatafile)
        
        if not fsinstpath.is_file():
            print(f"Downloading {mtcfsinstdatafile}")
            download(f"https://zenodo.org/record/3551003/files/{mtcfsinstdatafile}?download=1", fsinstpath)
        
        if not annpath.is_file():
            print(f"Downloading {mtcanndatafile}")
            download(f"https://zenodo.org/record/3551003/files/{mtcanndatafile}?download=1", annpath)
        
        if not essenpath.is_file():
            print(f"Downloading {essendatafile}")
            download(f"https://zenodo.org/record/3551003/files/{essendatafile}?download=1", essenpath)
        

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MTCFeatures",
    version="1.1a",
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
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
    package_data={
        'MTCFeatures' : ['data/*.jsonl.gz']
    },
    cmdclass={'install': MTCFeaturesInstall},
)

