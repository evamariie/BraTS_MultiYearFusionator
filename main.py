


from pathlib import Path
import datetime
from brats_toolkit.fusionator import Fusionator

def apply_fusionator(
        dataPath: Path,
        inputFolder: str,
        year: str,
        challenge: str,
        winners: list,
        method: str,
        outputFolder: str,
):
    # print parameters
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
    
    fus = Fusionator(verbose=True) # instantiate

    #For every file, fuse the winners segmentations
    filePaths = list(challengePath.joinpath(winners[0]).iterdir()) # all winners should have all files
    N = len(filePaths)
    for i,filePath in enumerate(filePaths):
        name = filePath.name # Example: ._BraTS-GLI-00038-001.nii.gz
        #print(f"\t{100*((i+1)/N):.4f} %)\t{i+1}/{N}\t{name}") #print progress
        #print(filePath)

        #Get segementation files winner options
        segs = [] # list of winner segementation files for the given name
        for winner in winners:
            filePath = challengePath.joinpath(winner, name)
            assert filePath.exists(), f"File does not exist: {filePath}"
            segs.append(str(filePath))

        # Fuse winner options
        outputFilePath = outputPath.joinpath(name)
        fus.fuse(
            segmentations=segs,
            outputPath=outputFilePath,
            method=method,
            weights=None,
        )
        break # DEBUGGING: just do one file

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
        "BraTS-MET": [],
        "BraTS-PED": ["astaraki", "AIPNI", "Biomedia-MBZU"],            # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
        "BraTS-SSA": ["CNMC_PMI", "CUHK_RPAI", "Biomedia-MBZU"],        # TODO: TypeError: in method 'ImageFileWriter_SetFileName', argument 2 of type 'std::string const &'
    },
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
                    dataPath = Path("C:\\Users\\eva\\Desktop\\Helmholz_AI\\BraTS_Fusion\\data"),
                    inputFolder = "predictions",
                    year = year,
                    challenge = challenge,
                    winners = winners,
                    method = method,
                    outputFolder = "fused",
                )
                print("\n\n")

    # log
    endtime = str(datetime.datetime.now().time())
    print("*** finished at:", endtime, "***")