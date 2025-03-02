


from pathlib import Path
import datetime
from brats_toolkit.fusionator import Fusionator
from multiprocessing import Pool
import nibabel as nib
import numpy as np

def process_file(args):
    i, filePath, N, challengePath, winners, outputPath, method, threadID = args
    name = filePath.name
    outputFilePath = outputPath.joinpath(name)
    if outputFilePath.exists():

        #read nii.gz file file to check if its broken
        printPrefix = f"[{threadID}, {'/'.join(challengePath.parts[-2:])}/{name}]: " 
       
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
    for winner in winners:
        filePath = challengePath.joinpath(winner, name)
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
        dataPath: Path,
        inputFolder: str,
        year: str,
        challenge: str,
        winners: list,
        method: str,
        outputFolder: str,
        threads = 8, #threads
        verbose = False
):
    # print parameters
    if(verbose):
        print(f"Applying fusionator to")
        print(f"\tdataPath: {dataPath}")
        print(f"\tinputFolder: {inputFolder}")
        print(f"\tyear: {year}")
        print(f"\tchallenge: {challenge}")
        print(f"\twinners: {winners}")
        print(f"\tmethod: {method}")
        print(f"\toutputFolder: {outputFolder}")

    challengePath = dataPath.joinpath(inputFolder, year, challenge) #path to the challenge folder where the winner folders are in
    
    outputPath = dataPath.joinpath(outputFolder, year, challenge, method, "+".join(winners))
    outputPath.mkdir(parents=True, exist_ok=True)

    #Check if "PaxHeader" folder exists and use it instead of the main folder
    if challengePath.joinpath(winners[0], "PaxHeader").exists():
        imagesFolder = challengePath.joinpath(winners[0], "PaxHeader") #path to the folder where the images are in
    else:
        imagesFolder = challengePath.joinpath(winners[0])
    
    # For every file, fuse the winners segmentations

    filePaths = list(imagesFolder.iterdir())
    N = len(filePaths)
    args = [(i, filePath, N, challengePath, winners, outputPath, method, threadID) for threadID, (i, filePath) in enumerate(enumerate(filePaths))]

    with Pool(processes=threads) as pool:
        for i, _ in enumerate(pool.imap_unordered(process_file, args), 1):
            print(f"\t{100*(i/N):.4f} %\t{i}/{N}", end='\r')

winnerMapping = {
    "2023": {
        "BraTS-GLI": ["Faking_it", "NVAUTO", "BiomedMBZ"],        # TODO: ERROR: Unable to determine ImageIO reader
        "BraTS-MEN": ["NVAUTO", "blackbean", "CNMC_PMI2023"],      # TODO: ERROR: Unable to determine ImageIO reader
        "BraTS-MET": ["NVAUTO", "S_Y", "blackbean"],               # TODO: ERROR: Unable to determine ImageIO reader
        "BraTS-PED": ["CNMC_PMI2023", "NVAUTO", "Sherlock_Zyb"],   # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
        "BraTS-SSA": ["NVAUTO", "BraTS2023_SPARK_UNN", "blackbean"],# TODO: ERROR: Unable to determine ImageIO reader
    },
    "2024": {
        #"BraTS-GEN": ["PolyU-AMA-Brain"],                              #TODO: what file is the correct one to unpack!?
        "BraTS-GLI": ["Faking_it", "kimbab", "MIST"],                  # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
        "BraTS-MEN-RT": ["nic-vicorob", "astraraki", "Faking_it"],     # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
        #"BraTS-MET": [],
        "BraTS-PED": ["astaraki", "AIPNI", "Biomedia-MBZU"],            # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
        "BraTS-SSA": ["CNMC_PMI", "CUHK_RPAI", "Biomedia-MBZU"],        # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
    }

    #"aggregate": { 
    #    "BraTS-GLI": ["2023\\Faking_it", "2023\\NVAUTO", "2023\\BiomedMBZ",
    #                  "2024\\Faking_it", "2024\\kimbab", "2024\\MIST"],
}

#file main function
if __name__ == "__main__":

    # log
    starttime = str(datetime.datetime.now().time())
    print("*** starting at", starttime, "***")

    # apply fusionator (DEBUGGING)
    if False:
        year, challenge = "2024", "BraTS-GLI"
        apply_fusionator(
            dataPath = Path("C:\\Users\\eva\\Desktop\\Helmholz_AI\\BraTS_Fusion\\data"),
            inputFolder = "predictions",
            year = year,
            challenge = challenge,
            winners = winnerMapping[year][challenge],
            #method = "mav",
            method = "simple",
            outputFolder = "fused",
        )

    #Apply on all challenges and years using both methods
    for method in ["simple", "mav"]:
        for year, challenges in winnerMapping.items():
            for challenge, winners in challenges.items():
                apply_fusionator(
                    dataPath = Path("data\\"),
                    #dataPath = Path("C:\\Users\\eva\\Desktop\\Helmholz_AI\\BraTS_Fusion\\data"),
                    inputFolder = "predictions",
                    year = year,
                    challenge = challenge,
                    winners = winners,
                    method = method,
                    outputFolder = "fused",
                    threads = 12, #threads
                    verbose = True
                )
                print("\n\n")

    # log
    endtime = str(datetime.datetime.now().time())
    print("*** finished at:", endtime, "***")