#/usr/bin/env python
"""
Purpose of file: Download patch data for a variety of patch centers, *NOT PARALLELIZED*
For a parallel version see download_patch.py and associated slurm batch job script

Inputs: 
None, all changes made by editing script

Outputs:
Writes the desired data to data_dir according to ADQL_base_script (both defined in script) for each patch

NOTES:
-   Centers loaded in from centers.csv, available at https://github.com/CianMRoche/Gaia-Data-Aquisition
    Lots of storage available at "/scratch/submit/gaia/roche" on subMIT

-   On precision: the string versions of the sky patch coordinate centers have a precision 10 
    decimal places as is. If this is changed, the file handling will need to be adjusted.
    (though download_patch.py will not need to be changed)

-   On inspecting outputs: Check the number of lines (objects) via "wc -l -c filename" where you
    replace filename, but only works as expected for csv files. In general to check file size in a human
    readable format, type "du -sh filename" and in the output "K" is kilobytes, "M" is megabytes and so on.

-   On unzipping: to unzip a folder recursively and overwrite the originals, use "gunzip -r folder_name"
"""

import numpy as np
import glob
import os
from astropy import units as u
from astropy.coordinates import SkyCoord
from tqdm import tqdm
from astroquery.gaia import Gaia


#----------------- Job Parameters ----------------------

# Define the folder where we'll store the files
data_dir = "./test_data/"
#data_dir = "/scratch/submit/gaia/roche/"  # Has to also be changed in download_patch.py 

print("\nData checks are happening in " + data_dir + "\n")

# Define login details (necessary to avoid download limits)
username = 'croche'
password = ''
Gaia.login(user=username, password=password)

# Cut the data to only download some of the centers
cut_start = 0
cut_end = 5  # set to -1 for "all"

# Define the patch-finding ADQL script
ADQL_base_script='''SELECT TOP 10 source_id,ra,ra_error,dec,dec_error, parallax,parallax_error,parallax_over_error,pmra,pmra_error,
                    pmdec,pmdec_error, phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag,bp_rp,radial_velocity,radial_velocity_error,teff_val 
                FROM gaiadr2.gaia_source  
                WHERE (pmra>=-100 AND pmra<=75 AND pmdec>=-150 AND pmdec<=100 AND parallax<=1.0) 
                    AND CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec), CIRCLE('ICRS',%s,%s,15))=1;
            '''

            # In the above, we look in a circle of radius 15 degrees cenetered on about our input point on the sky in RA and DEC in 
            # the International Celestial Reference System (ICRS) 


# ----------------- Load in desired patch centers ----------------------

#Load in all the patch centers, in galactic coordinates (phi,theta) also called (l,b)
philist, thetalist = np.loadtxt('centers.csv', delimiter=',', unpack=True, skiprows=1)

# Cut to the centers we want
philist = philist[cut_start:cut_end]
thetalist = thetalist[cut_start:cut_end]

num_centers = len(philist)


# ----------------- Submit jobs and get results ----------------------

for idx, (phi,theta) in enumerate(zip(philist,thetalist)): 
    print("Checking patch {} of {}".format(idx+1,num_centers))

    # Check if we did this job already
    output_filename = f"{phi:.10f}" + '_' + f"{theta:.10f}" + '.fits.gz'

    if len(glob.glob(data_dir + output_filename))==1:
        print("\n ---- Result for phi = {:.10f}, theta = {:.10f} was already present ---- \n".format(phi,theta))
        continue

    # Establish coordinate center for this patch in RA and DEC 
    c_gal = SkyCoord(l=phi*u.degree, b=theta*u.degree, frame='galactic')

    RA_center = c_gal.icrs.ra.degree
    DEC_center = c_gal.icrs.dec.degree

    # Print job info
    print("Starting query...")
    print("phi = {:.10f}, theta = {:.10f}".format(phi,theta))
    print('RA = {:.10f}, DEC = {:.10f}'.format(RA_center,DEC_center))

    # Define query and job name
    query = ADQL_base_script % (RA_center,DEC_center)

    jobname = '{:.10f}_{:.10f}'.format(phi,theta) # Sets the output file name too

    # Run job
    job=Gaia.launch_job_async(query, name=jobname, dump_to_file=True, output_format='fits', output_file = data_dir + jobname + '.fits.gz') # fits files are compressed
    job.get_results() 

    print("Job finished and result saved to " + data_dir + "\n")