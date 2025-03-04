


from pathlib import Path
import datetime
from brats_toolkit.fusionator import Fusionator
from multiprocessing import Pool
import nibabel as nib
import numpy as np

def process_file(args):
    i, inputFolders, filePath, N, outputPath, method, threadID = args
    name = filePath.name
    outputFilePath = outputPath.joinpath(name)
    printPrefix = f"[{threadID}, {'/'.join(outputFilePath.parts[-2:])}/{name}]: " 
       
    #check if file already exists and if so do some sanity checks
    if outputFilePath.exists():
        #Check validaity of data
        try:
            img = nib.load(str(outputFilePath))
            data = img.get_fdata()
        except Exception as e:
            print(f"{printPrefix}ERROR: broken (could not be loaded via nibabel)!")
            print(f"{printPrefix}\t{e}")
            return
        
        shape = data.shape
        if data.shape != (240, 240, 155) and data.shape != (182, 218, 182):
            print(f"{printPrefix}ERROR: shape {shape} instead of (240, 240, 155) or (182, 218, 182)!")
            return
        # NOTE: some chellanges have no shape constraints! e.g. 2024/BraTS-MEN-RT
        
        if np.count_nonzero(data) == 0:
            #print(f"{printPrefix}ERROR: only zeros!")
            return
        
        return
    
    print(f"{printPrefix} Processing...")

    segs = []
    for inputFolder in inputFolders:
        filePath = inputFolder.joinpath(name)
        assert filePath.exists(), f"File does not exist: {filePath}"
        segs.append(str(filePath))

    fus = Fusionator(verbose=False)
    try:
        fus.fuse(
            segmentations=segs,
            outputPath=outputFilePath,
            method=method,
            weights=None,
        )
    except UnboundLocalError as e:
        if "cannot access local variable 'bin_candidates' where it is not associated with a value" in str(e):
            print(f"[{threadID}] \t{e}")
            print(f"[{threadID}] \tSKIPPING {name}")

def apply_fusionator(
        inputFolders: list,
        folderName: str,
        method: str,
        outputFolder: str,
        threads = 8, #threads
        verbose = False
):
    # print parameters
    if(verbose):
        print(f"Applying fusionator to")
        print(f"\tfolderName: {folderName}")
        print(f"\tfolders: {inputFolders}")
        print(f"\tmethod: {method}")
        print(f"\toutputFolder: {outputFolder}")

    outputPath = dataPath.joinpath(outputFolder, folderName)
    outputPath.mkdir(parents=True, exist_ok=True)

    #get interseaction of all files from the input Folders
    print("Multi-year file availability:")
    folderNames = []
    
    for inputFolder in inputFolders:
        folderNames.append( {str(f.name) for f in inputFolder.iterdir()} )

    #get intersection of all file names
    intersectionNames = folderNames[0]
    for folderName in folderNames[1:]:
        intersectionNames = intersectionNames.intersection(folderName)
    print(f"\tIntersect:\t{len(intersectionNames)} files")

    # get file Paths for union file Names
    filePaths = [filePath for filePath in inputFolders[0].iterdir() if filePath.name in intersectionNames]
    N = len(filePaths)
    args = [(i, inputFolders, filePath, N, outputPath, method, threadID) for threadID, (i, filePath) in enumerate(enumerate(filePaths))]

    with Pool(processes=threads) as pool:
        for i, _ in enumerate(pool.imap_unordered(process_file, args), 1):
            print(f"\t{100*(i/N):.4f} %\t{i}/{N}", end='\r')

winnerMapping = {
    "BraTS-GLI": {
        "2023": ["Faking_it", "NVAUTO", "BiomedMBZ"],       
        "2024": ["Faking_it", "kimbab", "MIST"],            
    },
    "BraTS-PED": {
        "2023": ["CNMC_PMI2023", "NVAUTO", "Sherlock_Zyb"],  
        "2024": ["astaraki", "AIPNI", "Biomedia-MBZU"],     
    },
    "BraTS-SSA": {
        "2023": ["NVAUTO", "BraTS2023_SPARK_UNN", "blackbean"], 
        "2024": ["CNMC_PMI", "CUHK_RPAI", "Biomedia-MBZU"],     
    }
}

#file main function
if __name__ == "__main__":

    # log
    starttime = str(datetime.datetime.now().time())
    print("*** starting at", starttime, "***")

    dataPath = Path("data\\")
    inputFolder = "predictions"

    #Apply on all challenges and years using both methods
    for method in ["simple", "mav"]:
        for challenge, years in winnerMapping.items():
            folderPaths = []
            folderName = ""
            for year, winners in years.items():
                if folderName != "":
                    folderName += "__" # add separator between years
                folderName = year
                for winner in winners:
                    folderName += "_"+winner

                    challengePath = dataPath.joinpath(inputFolder, year, challenge)
                    #Check if "PaxHeader" folder exists and use it instead of the main folder
                    if challengePath.joinpath(winner, "PaxHeader").exists():
                        folderPaths.append(challengePath.joinpath(winner, "PaxHeader"))  #path to the folder where the images are in
                    else:
                        folderPaths.append(challengePath.joinpath(winner))

            apply_fusionator(
                inputFolders = folderPaths,
                folderName = folderName,
                method = method,
                outputFolder = "fused",
                threads = 12, #threads
                verbose = True
            )
            print("\n\n")

    # log
    endtime = str(datetime.datetime.now().time())
    print("*** finished at:", endtime, "***")