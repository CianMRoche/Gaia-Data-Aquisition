#/usr/bin/env python

# This script is an example of downloading a large number of properties for all the objects
# in a circle centered at a particular RA and DEC on the sky, subject to some cuts.
# Run from a terminal with an anaconda environment activated as `python3 download_patch.py`

from astroquery.gaia import Gaia


# We'll only get these columns for the top 100 objects to save time during this demonstration
# The indentation isnt necessary in the ADQL script but it is good for readability

ADQL_script='''SELECT TOP 100 source_id,ra,ra_error,dec,dec_error, parallax,parallax_error,parallax_over_error,pmra,pmra_error,
                pmdec,pmdec_error, phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag,bp_rp,radial_velocity,radial_velocity_error,teff_val 
                FROM gaiadr2.gaia_source  
                WHERE (pmra>=-100 AND pmra<=75 AND pmdec>=-150 AND pmdec<=100 AND parallax<=1.0) 
                    AND CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec), CIRCLE('ICRS',305.3070014170295,-40.966924750203106,15))=1;
            '''

            # In the above, we look in a circle of radius 15 degrees cenetered on about (305 , -40) in RA and DEC in 
            # the International Celestial Reference System (ICRS) 
    
jobname='simple_job' # Sets the output file name too
job=Gaia.launch_job_async(ADQL_script, name=jobname, dump_to_file=True, output_format='csv')
job.get_results() 