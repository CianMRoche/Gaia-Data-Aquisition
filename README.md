# Gaia-Data-Aquisition
Jupyter notebook tutorials on how to download Gaia data (DR2 and eDR3 as examples, where "DR" = "Data Release") for the purpose of the MIT Gaia DR3 hackathon

# The Basics
GAIA and other space missions produce huge amounts of data, and it is impractical to download it all onto some local file system (or even cluster file system) for use. As a result, we must submit _queries_ to an archive which contains all the data, where our query contains all the information about:
- What data we want
- From which data release(s) we want it (for example DR2)
- Conditions on the returned data (for example "Only show me objects in a certain patch of the sky, which also have low measurement error on their velocities")
- What format we want the data in

# SQL
Typically, one submits queries like this using Structured Query Language (SQL) which is designed to be a very readable programmatic representation of the above points[^1]. For example, if you have a **table** called "Nurses" (think of it like a spreadsheet with columns of data) whose columns are  as follows:

| First_name        | Surname           | Age  | Height |
| :------------- |:-------------| -----:| -----:|
| Asma     | Vlatko | 26 |  1.72 |
| Spiros | Arslan      |    31 | 1.66 |
| Isabel      | Antigone      |   42 | 1.58 | 
| Kevin    | Ma         |  52 | 1.48  |


using SQL one could ask for a list of all the first names of nurses older than 30, shorter than 1.6 m and ordered by descending age:
```
SELECT First_name
FROM Nurses
WHERE Age > 30
    AND Height < 1.6
ORDER BY Age DESC
```
We could have asked for all the information about nurses fitting these criteria rather than just the first names by using `SELECT *` instead of `SELECT First_name`. Note that all the SQL keywords are in capital letters, which is not necessary but is standard in order to make clear which statements are SQL and which relate to your data. The result would be
| First_name        | Surname           | Age  | Height |
| :------------- |:-------------| -----:| -----:|
| Isabel      | Antigone      |   42 | 1.58 | 
| Kevin    | Ma         |  52 | 1.48  |

To become more familiar with basic SQL, it may be useful to do the first 12 lessons from this interactive tutorial: https://sqlbolt.com/lesson/introduction.
Though the remaining tutorials would be nice to do, the structure of a request is covered in these 12, and the remaining lessons deal with altering tables (which we cannot do with Gaia data, as they are read-only).

[^1]: One usually submits SQL queries through some SQL client they install on their system. Since we will use Python as our interface with the database, we need no additional installation past the relevant python package.

# ADQL and the Gaia Archive
We wont be using SQL itself, but rather a specialization called "Astronomical Data Query Language" (ADQL). ADQL has essentially the same structure as SQL, but with additional functionality which makes querying astronomical data simpler. Before getting into the details, lets have a look at where our data will come from: the "search" tab of the Gaia data archive https://gea.esac.esa.int/archive/

![Image of Gaia data archive menu](https://github.com/CianMRoche/Gaia-Data-Aquisition/blob/4077223bcaf3048034557c70486296fe728dcc66/tutorial_images/archive_menu.png "Archive Menu")

As you can see, we can choose from a "basic search", which provides a nice interface for relatively simple searches, or submit an "advanced (ADQL)" query. To begin, do a basic search for "T Tau" by name, and get all the sources within a circle of radius 3 arc min. You can search in "gaiaedr3.gaia_source" which is the main source for eDR3 (=early DR3). After clicking submit query, you should be presented with a table of results (total number of resulting objects on bottom left). 

You can go back to the basic search and add "extra conditions" which will restrict the objects returned, or you can change which columns (properties of the objects) will be returned. You can see how your basic search would be written in ADQL by clicking "show query". An example of a constrained search is shown below, where we want to make sure the returned objects have low parallax error.

![Image of a constrained gaia data archive search](https://github.com/CianMRoche/Gaia-Data-Aquisition/blob/4077223bcaf3048034557c70486296fe728dcc66/tutorial_images/search_with_condition.png "Constrained Search")

One can find a collection of more complex ADQL queries here: https://www.cosmos.esa.int/web/gaia-users/archive/writing-queries which can be used for designing your own queries later. After completing a request, one could in principle download the resulting data, but this would be to your own laptop (or whatever device your browser is running on). To get the data on the computing cluster that we'll work on, you'll need to submit ADQL requests programatically.

### Optional
You can click on the "visualisation" tab at the top, and by clicking on the plot types on the top left you can create different visualisations of the eDR3 Gaia data. When you click on a plot type, you choose the data source and a plot size (not really important). This can be fun to mess around with! It opens with some default plots, but I recommend closing them and opening your own to understand what you're looking at better.

# Submitting ADQL queries programatically
We will use python for our submission and analysis, through the ADQL query submission package "astroquery". If youd really like to use another language we wont be able to help as much, but there are ways to get the data without using the python module we'll use.

In this github repository youll find a Jupyter notebook called "python_ADQL_tutorial.ipynb" which provides examples of how to submit ADQL requests in python, and download the kinds of data you may want to use. At a basic level, a request can look like this:
```
from astroquery.gaia import Gaia

job = Gaia.launch_job_async("""SELECT TOP 100 ra, dec
                                FROM gaiadr2.gaia_source 
                                ORDER BY source_id""",
                            dump_to_file=True, output_format='csv')
```

As you can see, the ADQL script can be entered as a multiline string, and we have chosen to output the RA and DEC (right-ascension and declination) for sources in the Gaia DR2 catalogue, ordered by source id, and we only keep the top 100 results (that is, we get the lowest 100 source ID objects from this query). The results will be saved as a .csv in the directory we ran the code, with a name corresponding to an ID for the job so we dont accidentally overwrite previous queries.
