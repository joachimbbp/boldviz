# USAGE: python download_test_data.py
from urllib.request import urlretrieve

url = "https://s3.amazonaws.com/openneuro.org/ds003548/sub-01/anat/sub-01_T1w.nii.gz?versionId=5ZTXVLawdWoVNWe5XVuV6DfF2BnmxzQz"
file = "./data/test_data/sub-01_T1w.nii.gz"
print("Downloading test data...")
f_res = urlretrieve(url, file)
print("Test data downloaded")