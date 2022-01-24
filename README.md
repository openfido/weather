OpenFIDO weather pipeline
=========================

The weather pipeline collates weather data for a location and set of years.

If only the *CSVFILE* is specified, then the CSV output includes a header row.
If the *GLMFILE* is also specified, then the CSV output does not include a
header row and the column names are identified in the GLM weather object.

PIPELINE
--------

Recommended pipeline settings:

| Setting                 | Recommended value                        |
| ----------------------- | ---------------------------------------- |
| Pipeline name           | Weather                                  |
| Description             | NSRDB historical weather data downloader |
| DockerHub Repository    | debian:11                                |
| Git Clone URL (https)   | https://github.com/openfido/weather.     |
| Repository Branch       | main                                     |
| Entrypoint Script (.sh) | openfido.sh                              |

INPUTS
------

`config.csv` - The run configuration file is required (see CONFIGURATION below).

OUTPUTS
-------

*CSVFILE* - Must be specified in `config.csv`. The following columns are
 provided:

| Column name             | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| datetime                | `YYYY-MM-DD HH:MM:SS` if CSV only, seconds in epoch w/GLM |
| solar_global[W/sf]      | Global solar irradiance                                   |
| solar_horizontal[W/sf]  | Horizontal surface solar irradiance                       |
| solar_direct[W/sf]      | Direct normal solar irradiance                            |
| clouds                  | Cloud type from NOAA PATMOS-X (see below)                 |
| dewpoint[degF]          | Wet bulb temperature                                      |
| temperature[degF]       | Dry bulb temperature                                      |
| ground_reflectivity[pu] | Ground albedo                                             |
| wind_speed[m/s]         | Wind speed                                                |
| wind_dir[rad]           | Wind direction (compass heading in radians                |
| solar_altitude[deg]     | Solar altitude.                                           |
| humidity[%]             | Relative humidity                                         |
| pressure[mbar]          | Air pressure                                              |
| heat_index[degF]        | Heat index temperature (NOAA method)                      |

| Cloud type | Definition.        |
| ---------- | ------------------ |
| 0          | Clear              |
| 1          | Probably clear     |
| 2          | Fog                |
| 3          | Water              |
| 4          | Super-cooled water |
| 5          | Mixed              |
| 6          | Opaque ice         |
| 7          | Cirrus             |
| 8          | Overlapping        |
| 9          | Overshooting       |
| 10         | Unknown            |
| 11         | Dust               |
| 12         | Smoke              |
| -15        | Not available      |

*GLMFILE* - Only if specified in `config.csv`. The model file includes the
 global "WEATHER", which enumerates the weather object name included. The
 model will always include the class definition for a weather object with
 the weather properties defined above.

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

You may use the http://openfido.gridlabd.us/weather.html to generate the configuration file.
