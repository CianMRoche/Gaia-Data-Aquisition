#/usr/bin/env python
"""
Purpose of file: Download a subset (set by command line argument) of the rows of GAIA DR3, for the columns containing spectroscopic information 
suitable for parallelization via job submission system like slurm.

Outputs:
Writes the velocity data according to ADQL_base_script (both defined in script)

NOTES:
-   On precision: the string versions of the sky patch coordinate centers have a precision 10 
    decimal places as is. If this is changed, the file handling will need to be adjusted.
    (though download_patch.py will not need to be changed)

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
username = 'croche' # write your username
password = ''   # write your password
Gaia.login(user=username, password=password)

data_dir = "/data/submit/gaia/dr3/kinematics/velocity_info/" # the folder with lots of storage where we'll save the files

# Add TOP x after "SELECT" below to only get these columns for the first x objects (x a natural number) eg "SELECT TOP 10 ..."
# The indentation isnt necessary in the ADQL script but it is good for readability

query = '''SELECT 
                source_id, ra, dec, l,b, parallax, parallax_error, pmra, pmra_error, pmdec, pmdec_error, 
                parallax_pmra_corr, parallax_pmdec_corr, pmra_pmdec_corr, ruwe, radial_velocity, radial_velocity_error,
                rv_template_fe_h, parallax_over_error
            FROM gaiadr3.gaia_source
            WHERE rv_nb_transits > 0 AND parallax/parallax_error > 5.0
        '''

jobname = "small_velocity_info" # Sets the output file name too
output_filename = data_dir + jobname + '.csv'

# Check if we already got this data
if len(glob.glob(output_filename))==1:
    print("Cancelling this job, " + output_filename + " already exists")
    print("\nExiting execution...")
    sys.exit()
    
# Run job
job=Gaia.launch_job_async(query, name=jobname, dump_to_file=True, output_format='csv',output_file = output_filename) # fits files are compressed
job.get_results() 

print("Job finished and result saved to " + output_filename + "\n")

# Delete the job from our cache (so we dont hit our quota)
print("Deleting job with id {}".format(job.jobid))
Gaia.remove_jobs([job.jobid])

# time execution
print("\nExecution took %s seconds\n" % (time.time() - start_time))