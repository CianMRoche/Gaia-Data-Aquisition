#/usr/bin/env python
"""
Purpose of file: Download a subset (set by command line argument) of the rows of GAIA DR3, for the columns containing spectroscopic information 
suitable for parallelization via job submission system like slurm.

Command Line Inputs:
Starting row value in millions (5,10,... etc) corresponding to for example "start offset at 5 million". We use a row limit of 9 million

Outputs:
Writes the desired data for input patch to data_dir according to ADQL_base_script (both defined in script)

NOTES:
-   On inspecting outputs: Check the number of lines (objects) via "wc -l -c filename" where you
    replace filename, but only works as expected for csv files. In general to check file size in a human
    readable format, type "du -sh filename" and in the output "K" is kilobytes, "M" is megabytes and so on.
    For all files in folder do "du -ha"

-   On unzipping: to unzip a folder recursively and overwrite the originals, use "gunzip -r folder_name"
"""

from astroquery.gaia import Gaia
import sys
import glob
import sys

# For timing execution
import time
start_time = time.time()

# ----------------- Set job parameters ----------------------

# Define login details (necessary to avoid download limits)
username = '' # write your username
password = ''   # write your password
Gaia.login(user=username, password=password)

data_dir = "" # the folder with lots of storage where we'll save the files


# Add TOP x after "SELECT" below to only get these columns for the first x objects (x a natural number) eg "SELECT TOP 10 ..."
# The indentation isnt necessary in the ADQL script but it is good for readability

ADQL_base_script='''SELECT TOP %s spec.source_id, spec.teff_gspspec, spec.teff_gspspec_lower, spec.teff_gspspec_upper, 
                                spec.logg_gspspec, spec.logg_gspspec_lower, spec.logg_gspspec_upper, spec.mh_gspspec, 
                                spec.mh_gspspec_lower, spec.mh_gspspec_upper, g1.distance_gspphot, g1.distance_gspphot_lower, 
                                g1.distance_gspphot_upper, spec.alphafe_gspspec, spec.alphafe_gspspec_lower, spec.alphafe_gspspec_upper, 
                                spec.mgfe_gspspec, spec.mgfe_gspspec_lower, spec.mgfe_gspspec_upper
                    FROM gaiadr3.gaia_source AS g1 
                    JOIN gaiadr3.astrophysical_parameters as spec 
                    USING (source_id) 
                    WHERE g1.rv_nb_transits > 0
                    OFFSET %s
                '''


row_lim = 9000000
#row_lim = 10
offset = int(sys.argv[1]) * 1000000


# Print job info
print("\nStarting query for starting value {} and top {} rows".format(offset,row_lim))

# Define query and job name
query = ADQL_base_script % (row_lim,offset)

jobname = '{}_to_{}'.format(offset,offset+row_lim) # Sets the output file name too
output_filename = data_dir + jobname + '.fits.gz'

# Check if we already got this data
if len(glob.glob(output_filename))==1:
    print("Cancelling this job, " + output_filename + " already exists")
    print("\nExiting execution...")
    sys.exit()
    
# Run job
job=Gaia.launch_job_async(query, name=jobname, dump_to_file=True, output_format='fits',output_file = output_filename) # fits files are compressed
job.get_results() 

print("Job finished and result saved to " + output_filename + "\n")

# Delete the job from our cache (so we dont hit our quota)
print("Deleting job with id {}".format(job.jobid))
Gaia.remove_jobs([job.jobid])

# time execution
print("\nExecution took %s seconds\n" % (time.time() - start_time))