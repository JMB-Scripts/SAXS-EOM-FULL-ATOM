### Features
# Create from EOM 3.0 cif files a full atom pdb files :
# 1 - Converts CIF files to PDB format using Open Babel.
# 2 - Creates peptide bonds and linking C-alpha dummy atoms using PD2.
# 3 - Optimises side-chain conformations using Scwrl4.
# 
#
### Requirements
# - Python 3.x
## Python packages:
# 1- Open Babel
# conda install openbabel
#
# 2- tqdm
# conda install tqdm
## External progams 
# 1- PD2
# https://github.com/jmacdona/pd2_public
#
# To install PD2 you need:
#   For LINUX and MAC:
#       1- You need to update the SConstruct file and change all the print fonction
#       example print("INFO: compiling with gprof flags")
##  For linux only :
#       2- you need to change the name of the liboost by removing the "-mt", because liboost change its name
##  For Mac only   
#       2 -In src/external/include/eigen replace the file by the last version on GitHub
#
#           https://github.com/libigl/eigen
#
#       3- Add -mt for boost_thread
#
#   For LINUX and MAC:
#       In your .bashrc add something like
#           export PATH=$PATH:/location/of/PD2/bin
#           export PD2_DB=/location/of/PD2/database
# 2- Scwrl4
#
# http://dunbrack.fccc.edu/lab/scwrl
#
# In your .bashrc add something like 
# export PATH=$PATH://location/of/Scwrl4
# export SCWRL_DB=/location/of/Scwrl4.ini
#
### USAGE 
# Ensure that you set up properly the environment variables PD2_DB and SCWRL_DB to point to the respective database directories.
# Run the script by providing the path of the folder where the CiFS are, and the sequence as a command-line argument:
#
# python script_name.py path_to_sequence.fasta path_to_CIFS_FOLDER
#
# In the sequence file if the aa are in lower case they will be untouched by SCWRL4.
#
# The script will convert CIF files to PDB format, perform protein structure refinement, optimize side-chain conformations, and generate output PDB files 
# in the final_pdb/ directory.
#
# 2023 Bourhis Jean-Marie (with a bit chat gpt, I'm still a "tanche" in python but getting there)
#
import os
import subprocess
import sys
from tqdm import tqdm

# Define the input and output directories
output_pdb_directory = "output_pdbs/"
tmp_directory = "tmp/"
final_pdb = "final_pdb/"
pd2_db = os.environ.get("PD2_DB")
SCWRL_DB = os.environ.get("SCWRL_DB")

# Check if the command line arguments are provided correctly
if len(sys.argv) < 3:
    print("Please provide the necessary arguments: script_name.py Sequence.fasta data_folder_path")
    sys.exit(1)
# Path to the sequence 
SEQ = str(sys.argv[1])
input_cif_directory = str(sys.argv[2])

# Create output and temporary directories if they don't exist
os.makedirs(output_pdb_directory, exist_ok=True)
os.makedirs(tmp_directory, exist_ok=True)
os.makedirs(final_pdb, exist_ok=True)

# Get a list of CIF files in the input directory and sort them
cif_files = [f for f in os.listdir(input_cif_directory) if f.endswith(".cif")]
cif_files.sort()  # Sort alphabetically

# Wrap the loop with tqdm to add a progress bar
for cif_file in tqdm(cif_files, desc="Converting files"):
    cif_path = os.path.join(input_cif_directory, cif_file)
    pdb_file = cif_file.replace(".cif", ".pdb")
    pdb_path = os.path.join(output_pdb_directory, pdb_file)

    # Convert CIF to PDB using Open Babel
    obabel_command = ["obabel", cif_path, "-O", pdb_path]
    with open(os.devnull, 'w') as devnull:
        subprocess.run(obabel_command, stdout=devnull, stderr=devnull)
    
    # Run pd2_ca2main using subprocess and redirect output to a black hole
    pd2_command = [
        "pd2_ca2main",
        "--database", pd2_db,
        "--ca2main:new_fixed_ca",
        "--ca2main:bb_min_steps", "500",
        "-i", pdb_path,
        "-o", os.path.join(tmp_directory, "tmp1")
    ]
    with open(os.devnull, 'w') as devnull:
        pd2_process = subprocess.Popen(pd2_command, stdout=devnull, stderr=devnull)
        pd2_process.wait()

    # Remove headers using awk
    awk_command = ["awk", '/^ATOM |^TER/']
    with open(os.path.join(tmp_directory, "tmp1"), "rb") as input_file:
        awk_process = subprocess.run(awk_command, stdin=input_file, stdout=subprocess.PIPE, text=True)
        tmp2_content = awk_process.stdout

    with open(os.path.join(tmp_directory, "tmp2"), "w") as tmp2_file:
        tmp2_file.write(tmp2_content)

    # Run Scwrl4 using subprocess and redirect output to a black hole
    scwrl_command = [
        "Scwrl4",
        "-i", os.path.join(tmp_directory, "tmp2"),
        "-s", SEQ,
        "-p", SCWRL_DB,
        "-h",
        "-o", os.path.join(tmp_directory, "tmp3")
    ]
    with open(os.devnull, 'w') as devnull:
        scwrl_process = subprocess.Popen(scwrl_command, stdout=devnull, stderr=devnull)
        scwrl_process.wait()

    # Remove headers using awk
    with open(os.path.join(tmp_directory, "tmp3"), "rb") as input_file:
        awk_process = subprocess.run(awk_command, stdin=input_file, stdout=subprocess.PIPE, text=True)
        tmp4_content = awk_process.stdout

    with open(os.path.join(final_pdb, pdb_file), "w") as tmp4_file:
        tmp4_file.write(tmp4_content)
    # Delete temporary files created during the processing
    os.remove(os.path.join(tmp_directory, "tmp1"))
    os.remove(os.path.join(tmp_directory, "tmp2"))
    os.remove(os.path.join(tmp_directory, "tmp3"))


print("Conversion complete.")
