OpenFIDO weather pipeline
=========================

The weather pipeline collates weather data for a location and set of years.

If only the CSVFILE is specified, then the output includes a header row.  If
the GLMFILE is also specified, then the output does not include a header row
and the column names are identified in the GLM weather object.

INPUTS
------

    config.csv (required)

OUTPUTS
-------

    CSVFILE (if specified in config.csv)

    GLMFILE (if specified in config.csv)

CONFIGURATION
-------------

The following is a summary of parameters that are supported by the config.csv
file.

    CSVFILE,filename.csv
    GLMFILE,filename.glm
    NAME,objectname
    EMAIL,your.email@your.org
    APIKEY,your-api-key
    YEARS,year1,year2,...
    LATLON,latitude,longitude
