"""OpenFIDO weather pipeline

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

EXAMPLE
-------

    shell$ openfido install weather
    shell$ openfido run weather year=2020 position=37.4,-122.3 /dev/null /tmp/weather.csv,/dev/null

"""

try:

    import os, sys, shutil, json, csv

    OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")
    OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

    GLMFILE = "/dev/null"
    NAME = None

    with open(f"{OPENFIDO_INPUT}/config.csv","r") as f:
        reader = csv.reader(f)
        for line in reader:
            if len(line) == 1:
                globals()[line[0]] = True
            elif len(line) == 2:
                globals()[line[0]] = line[1]
            elif len(line) > 2:
                globals()[line[0]] = line[1:]

    os.chdir("/tmp")

    sys.path.append(".")
    import __init__ as weather

    weather.email = EMAIL
    weather.addkey(APIKEY)
    outputs = [CSVFILE,GLMFILE]

    weather.main([],outputs,{"year":year,"position":position,"name":name})

    for file in outputs:
        if file and file != "/dev/null":
            shutil.copyfile(file,f"{OPENFIDO_OUTPUT}/{file}")

except Exception as err:

    print(f"\n*** ERROR ***\n{err}\n\nHelp on {__doc__}")
    raise

