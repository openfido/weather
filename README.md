OpenFIDO weather pipeline
=========================

The weather pipeline collates weather data for a location and set of years.

If only the *CSVFILE* is specified, then the CSV output includes a header row.
If the *GLMFILE* is also specified, then the CSV output does not include a
header row and the column names are identified in the GLM weather object.

INPUTS
------

`config.csv` - The run configuration file is required (see CONFIGURATION below).

OUTPUTS
-------

*CSVFILE* - Must be specified in `config.csv`. The following columns are
 provided:

    datetime
    solar_global[W/sf]
    solar_horizontal[W/sf]
    solar_direct[W/sf]
    clouds
    dewpoint[degF]
    temperature[degF]
    ground_reflectivity[pu]
    wind_speed[m/s]
    wind_dir[rad]
    solar_altitude[deg]
    humidity[%]
    pressure[mbar]
    heat_index[degF]

*GLMFILE* - Only if specified in `config.csv`. The model file includes the
 global "WEATHER", which enumerates the weather object name included.

CONFIGURATION
-------------

The following is a summary of parameters that are supported by the config.csv
file.

Template for `config.csv`:

    CSVFILE,filename.csv
    GLMFILE,filename.glm
    NAME,objectname
    EMAIL,your.email@your.org
    APIKEY,your-api-key
    YEARS,year1,year2,...
    LATLON,latitude,longitude

*CSVFILE* - Specifies the weather CSV output file name. Required.

*GLMFILE* - Specifies the gridlabd GLM output model file. Optional. If omitted,
the CSV file is formatted for standalone use (with a header row). If
included, the CSV file is formatted for GridLAB-D player input (without a
header row).

*NAME* - Specifies the GLM weather object name to use. Optional. If omitted, the
object will be given a geocoded name based on the latitude and longitude of
the weather location.

*EMAIL* - Specifies the email address used to register with the NREL NSRDB API.
See https://nsrdb.nrel.gov/data-sets/api-instructions.html for details.

*APIKEY* - Provides the API key provided by NREL when the EMAIL was registered.
See EMAIL for details.

*YEARS* - Specifies the years for which weather data is downloaded.  Multiple years
are permitted by adding additional columns

*LATLON* - Specifies the latitude and longitude for the weather data.
