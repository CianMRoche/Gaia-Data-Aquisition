#/usr/bin/env python
"""
Purpose of file: Download patch data for a single patch center, more suitable for parallelization
via job submission system like slurm

Command Line Inputs:
Index of the desired patch center (0,1,2,... etc) in the file "centers.csv"

Outputs:
Writes the desired data for input patch to data_dir according to ADQL_base_script (both defined in script)

NOTES:
-   Centers loaded in from centers.csv, available at https://github.com/CianMRoche/Gaia-Data-Aquisition
    Lots of storage available at "/scratch/submit/gaia/roche" on subMIT and folders within, but also at 
    "/data/submit/gaia"

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
from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
import glob
import sys

# For timing execution
import time
start_time = time.time()

# ----------------- Set job parameters ----------------------

# Define login details (necessary to avoid download limits)
username = 'croche'
password = ''
Gaia.login(user=username, password=password)

data_dir = "/data/submit/gaia/dr3" # the folder with lots of storage where we'll save the files


# Add TOP x after "SELECT" below to only get these columns for the first x objects (x a natural number) eg "SELECT TOP 10 ..."
# The indentation isnt necessary in the ADQL script but it is good for readability

ADQL_base_script='''SELECT source_id,ra,ra_error,dec,dec_error,parallax,parallax_error,pmra,pmra_error,pmdec,pmdec_error,ruwe,
                        phot_g_mean_flux,phot_g_mean_flux_error,phot_g_mean_mag,phot_bp_mean_flux,phot_bp_mean_flux_error,
                        phot_bp_mean_mag,phot_rp_mean_flux,phot_rp_mean_flux_error,phot_rp_mean_mag,bp_rp,dr2_radial_velocity,
                        dr2_radial_velocity_error,dr2_rv_template_teff
                FROM gaiaedr3.gaia_source  
                WHERE (pmra>=-100 AND pmra<=75 AND pmdec>=-150 AND pmdec<=100 AND parallax<=1.0) 
                    AND CONTAINS(POINT('ICRS',gaiaedr3.gaia_source.ra,gaiaedr3.gaia_source.dec), CIRCLE('ICRS',%s,%s,15))=1;
                '''

            # In the above, we look in a circle of radius 15 degrees cenetered on about our input point on the sky in RA and DEC in 
            # the International Celestial Reference System (ICRS) 

# Establish desired coordinate center for this patch
center_index = int(sys.argv[1])


# ----------------- Load in desired patch center ----------------------

#Load in all the patch centers, in galactic coordinates (phi,theta) also called (l,b)
philist, thetalist = np.loadtxt('centers.csv', delimiter=',', unpack=True, skiprows=1)

phi_center = philist[center_index]
theta_center = thetalist[center_index]

# Define a coordinate object for this center
c_gal = SkyCoord(l=phi_center*u.degree, b=theta_center*u.degree, frame='galactic')

# Get RA and DEC for this center
RA_center = c_gal.icrs.ra.degree
DEC_center = c_gal.icrs.dec.degree


# ----------------- Running the job ----------------------

# Print job info
print("\nStarting query for center index {}".format(center_index))
print("phi = {:.10f}, theta = {:.10f}".format(phi_center,theta_center))
print('RA = {:.10f}, DEC = {:.10f}'.format(RA_center,DEC_center))

# Define query and job name
query = ADQL_base_script % (RA_center,DEC_center)

jobname = '{:.10f}_{:.10f}'.format(phi_center,theta_center) # Sets the output file name too
output_filename = data_dir + jobname + '.fits.gz'

# Check if we already got this data
if len(glob.glob(output_filename))==1:
    print("\n ---- Result for phi = {:.10f}, theta = {:.10f}, center index {} was already present ---- \n".format(phi_center,theta_center,center_index))
    print("Found in " + output_filename)
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