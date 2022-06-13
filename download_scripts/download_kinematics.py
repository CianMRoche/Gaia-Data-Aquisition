#/usr/bin/env python
"""
Purpose of file: Download a subset (set by command line argument) of the rows of GAIA DR3, for the columns containing kinematic information 
suitable for parallelization via job submission system like slurm.

Command Line Inputs:
Starting row value in millions (5,10,... etc) corresponding to for example "start offset at 5 million". We use a row limit of 5 million

Outputs:
Writes the desired data for input patch to data_dir according to ADQL_base_script (both defined in script)

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

data_dir = "/data/submit/gaia/dr3/kinematics/" # the folder with lots of storage where we'll save the files
#data_dir = "test_data_dir/"

# Add TOP x after "SELECT" below to only get these columns for the first x objects (x a natural number) eg "SELECT TOP 10 ..."
# The indentation isnt necessary in the ADQL script but it is good for readability

ADQL_base_script='''SELECT TOP %s g1.source_id, g1.ra, g1.dec, g1.l, g1.b, g1.parallax, g1.parallax_error, g1.pmra, g1.pmra_error, 
                        g1.pmdec, g1.pmdec_error, g1.parallax_pmra_corr, g1.parallax_pmdec_corr, g1.pmra_pmdec_corr, g1.ruwe, g1.phot_g_mean_mag, 
                        g1.phot_bp_mean_mag, g1.phot_rp_mean_mag, g1.radial_velocity, g1.radial_velocity_error, spec.alphafe_gspspec, 
                        spec.alphafe_gspspec_lower, spec.alphafe_gspspec_upper, 
                        spec.mh_gspspec + spec.fem_gspspec AS feh, 
                        spec.mh_gspspec_lower + spec.fem_gspspec_lower AS feh_lower, 
                        spec.mh_gspspec_upper + spec.fem_gspspec_upper AS feh_upper 
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