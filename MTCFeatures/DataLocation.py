import os, sys
import requests
import hashlib

from .appdirs import user_data_dir, site_data_dir

#data file missing
class DataFileMissingError(Exception):
    def __init__(self, arg):
        self.name = arg
    def __str__(self):
        return f"""Datafile for {self.name} missing.
    To download run MTCFeatures.downloadData(dest='user'). This will store three
    data files in either a platform specific user data directory or the system wide
    data directory (if dest='system'). The files will be downloaded from Zenodo:
    https://zenodo.org/record/3551003. 
    """

class DataDirCreateError(Exception):
    def __init__(self, arg):
        self.name = arg
    def __str__(self):
        return f"Failed to create or write in the directory for data.: {self.name}."

class MD5Error(Exception):
    def __init__(self, arg):
        self.name = arg
    def __str__(self):
        return f"MD5 hash value for downloaded file is not correct: {self.name}."

def downloadData(dest='user'):
    """Downloads data files into either a user data folder or a system wide data folder.
    
    The data files will be downloaded from Zenodo: https://zenodo.org/record/3551003 and
    the MD5 hash will be checked. To find out the directories:
    
    .. code-block:: python

            from MTCFeatures import DataLocation
            print(DataLocation().user_data_dir)
            print(DataLocation().site_data_dir)
    
    Parameters
    ----------
    dest : string, default='user'
        If dest='user', install the datafiles into a platform specific user data file.
        If dest='system', install the datafiles into a platform specific user data file.
    """
    
    DataLocation().downloadData(dest)

class DataLocation:

    def __init__(self, jsonpath=None):
        self.jsonpath = jsonpath
        self.resolvedPath = None
        self.filenames = {
            'MTC-ANN-2.0.1'    : 'MTC-ANN-2.0.1_sequences-1.1.jsonl.gz',
            'MTC-FS-INST-2.0'  : 'MTC-FS-INST-2.0_sequences-1.1.jsonl.gz',
            'ESSEN'            : 'essen_sequences-1.1.jsonl.gz'
        }
        
        self.downloadlinks = {
            'MTC-ANN-2.0.1'    : f"https://zenodo.org/record/3551003/files/{self.filenames['MTC-ANN-2.0.1']}?download=1",
            'MTC-FS-INST-2.0'  : f"https://zenodo.org/record/3551003/files/{self.filenames['MTC-FS-INST-2.0']}?download=1",
            'ESSEN'            : f"https://zenodo.org/record/3551003/files/{self.filenames['ESSEN']}?download=1"
        }
        
        self.md5hashes = {
            'MTC-ANN-2.0.1'    : "1a15615a4f7222702276565a0253e329",
            'MTC-FS-INST-2.0'  : "2c5ef01870e9e202df392fed5b34b061",
            'ESSEN'            : "c9290572aefb97af60b206775d050876"
        }
        
        self.user_data_dir = user_data_dir('MTCFeatures', "PvK")
        self.site_data_dir = site_data_dir('MTCFeatures', "PvK")

        self.resolvePath()

    def resolvePath(self):
        if self.jsonpath is not None:
            if os.path.isfile(self.jsonpath):
                #if it is a valid file path. Done.
                self.resolvedPath = self.jsonpath
            else:
                #try combinations
                if os.path.isfile(os.path.join(self.user_data_dir, self.filenames[self.jsonpath])):
                    self.resolvedPath = os.path.join(self.user_data_dir, self.filenames[self.jsonpath])
                if os.path.isfile(os.path.join(self.site_data_dir, self.filenames[self.jsonpath])):
                    self.resolvedPath = os.path.join(self.site_data_dir, self.filenames[self.jsonpath])
            if self.resolvedPath is None and self.jsonpath in self.filenames.keys():
                #Data file is missing: raise error
                raise DataFileMissingError(self.jsonpath)

    def getFilePath(self):
        return self.resolvedPath
 
    def download(self, url, filename, verbose=False):
        if verbose:
            sys.stdout.write(f"Downloading {url} -> {filename}")
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
                    if verbose:
                        sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                        sys.stdout.flush()
        if verbose:
            sys.stdout.write('\n')
    
    def createDataDir(self, destdir):
        if os.path.isdir(destdir):
            #Exists. writable?
            if not os.access(destdir, os.W_OK):
                #not writable
                raise DataDirCreateError(destdir)        
        else:
            #Doesn't exists. Crate
            try:
                os.makedirs(destdir)
            except OSError as e:
                print(e)
                raise DataDirCreateError(destdir)        

    def downloadData(self, dest='user'):
        destdir = self.user_data_dir
        if dest == 'system':
            destdir = self.site_data_dir
        try:
            self.createDataDir(destdir)
        except DataDirCreateError as e:
            print(e)
            raise
        for name in self.downloadlinks.keys():
            destfilename = os.path.join(destdir, self.filenames[name])
            self.download(self.downloadlinks[name], destfilename, verbose=True)
            md5_hash = self.computeMD5(destfilename)
            if md5_hash != self.md5hashes[name]:
                raise MD5Error(self.filenames[name])

    def computeMD5(self, filename):
        md5_hash = hashlib.md5()
        with open(filename,"rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                md5_hash.update(byte_block)
        return md5_hash.hexdigest()
