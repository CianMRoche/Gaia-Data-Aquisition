import pandas as pd

dataframes_dir = "/data/submit/gaia/dr3/kinematics/velocity_info/"

filename_base = "gaia_dr3_velocities_%s.pkl"

df = pd.read_pickle(dataframes_dir + (filename_base % 0))

for i in range(1,30):
    df_read = pd.read_pickle(dataframes_dir + (filename_base % i))
    print(dataframes_dir + (filename_base % i))

    df_bigger = pd.concat([df, df_read], verify_integrity=True, ignore_index=True)

    del(df_read)
    del(df)

    df = df_bigger
    del(df_bigger)

df.to_pickle(dataframes_dir + "gaia_dr3_velocities_combined.pkl")