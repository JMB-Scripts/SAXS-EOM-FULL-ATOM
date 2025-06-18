## SAXS-EOM-FULL-ATOM

Convert EOM output to a full atom PDB files 

## Features
EOMv3.0 genrates cif that you can convert to full atom pdb files :

1 - Converts CIF files to PDB format using Open Babel.
2 - Creates peptide bonds and links C-alpha dummy atoms using PD2.
3 - Optimises side-chain conformations using Scwrl4.

## Requirements
- Python 3.x
  
Python packages:
   1- Open Babel

conda install openbabel

   2- tqdm

conda install tqdm

External programs:  
    1- PD2

https://github.com/jmacdona/pd2_public

To install PD2 you need:
   
   For LINUX and MAC:
   
       1- You need to update the SConstruct file and change all the print fonction
       
       example print("INFO: compiling with gprof flags")
  
       2- you need to change the name of the liboost by removing the "-mt", because liboost change its name
       
  For Mac M1,M2 ...:
  
      1- In src/external/include/eigen replace the file by the last version on GitHub

           https://github.com/libigl/eigen
           
      2- add on SConstruct
      
      import platform
      is_arm = platform.machine() == "arm64"

      and change the line 'gcc_cppflags='
      for 
      
      '''
      
      gcc_cppflags = ['-ffast-math', '-funroll-loops', '-pipe','-g', '-Wall', '-fmessage-length=0', '-std=c++17' ]
      if not is_arm:
      cxxflags.insert(0, '-msse3')  # On ajoute -msse3 uniquement sur x86_64
      
      '''
      
   For LINUX and MAC:
   
       In your .bashrc add something like
           export PATH=$PATH:/location/of/PD2/bin
           export PD2_DB=/location/of/PD2/database
           
 2- Scwrl4

 http://dunbrack.fccc.edu/lab/scwrl

 In your .bashrc add something like 
 
 export PATH=$PATH://location/of/Scwrl4
 export SCWRL_DB=/location/of/Scwrl4.ini

## USAGE 
 Ensure you set up properly the environment variables PD2_DB and SCWRL_DB to point to the respective database directories.
 Run the script by providing the path of the folder where the CiFS are and the sequence in fasta format as a command-line argument:

 python script_name.py path_to_sequence.fasta path_to_CIFS_FOLDER

 In the sequence file if the aa are in lower case they will be untouched by SCWRL4.

 The script will convert CIF files to PDB format, perform protein structure refinement, optimize side-chain conformations, and generate output PDB files 
 in the final_pdb/ directory.

2023 JMB

