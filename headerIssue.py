
#Read two nifti files one for header, one for data

import nibabel as nib
import numpy as np
from pathlib import Path

dataPath = Path("data\\")
inputFolder = "predictions"
fileName = "BraTS-GLI-00007-000.nii.gz"
year = "2023"
challenge = "BraTS-GLI"
winners = ["Faking_it"]

file1Path = dataPath.joinpath(inputFolder, year, challenge, winners[0], "._"+fileName)
file2Path = dataPath.joinpath(inputFolder, year, challenge, winners[0], "PaxHeader", fileName)


