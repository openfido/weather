"""Weather pipeline

SYNOPSIS

Pipeline:

    Setting                   Recommended value                        
    -----------------------   ---------------------------------------- 
    Pipeline name             Weather                                  
    Description               NSRDB historical weather data downloader 
    DockerHub Repository      debian:11                                
    Git Clone URL (https)     https://github.com/openfido/weather.     
    Repository Branch         main                                     
    Entrypoint Script (.sh)   openfido.sh                              

CLI:

    sh$ openfido install weather
    sh$ openfido run year=YEAR1,YEAR2,... position=LATITUDE,LONGITUDE /dev/null CSVNAME,{/dev/null,GLMNAME}

DESCRIPTION

The weather pipeline collates weather data for a location and set of years.

If only the *CSVFILE* is specified, then the CSV output includes a header row.
If the *GLMFILE* is also specified, then the CSV output does not include a
header row and the column names are identified in the GLM weather object.

SEE ALSO:

* https://github.com/openfido/weather/README.md
"""

import sys, os, json, requests, pandas, numpy, datetime

leap = True
interval = 60
utc = False
email = None # by default this will be the first key in the credentials file
interpolate_time = None
interpolate_method = 'linear'
server = "https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv"
cachedir = "/usr/local/share/gridlabd/weather"
attributes = 'ghi,dhi,dni,cloud_type,dew_point,air_temperature,surface_albedo,wind_speed,wind_direction,solar_zenith_angle,relative_humidity,surface_pressure'
credential_file = f"{os.getenv('HOME')}/.nsrdb/credentials.json"
geocode_precision = 5 
float_format="%.1f"
date_format="%Y-%m-%d %H:%M:%S"
verbose_enable = False

try:
    from nsrdb_weather_config import *
except:
    pass

def error(msg,code=None):
    """Display an error message and exit if code is a number"""
    if code != None:
        print(f"ERROR [nsrdb_weather]: {msg}",file=sys.stderr)
        exit(code)
    else:
        raise Exception(msg)

def warning(msg):
    print(f"WARNING [nsrdb_weather]: {msg}")

def syntax(code=0):
    """Display docs (code=0) or syntax help and exit (code!=0)"""
    if code == 0:
        print(__doc__)
    else:
        print(f"Syntax: {os.path.basename(sys.argv[0])} -y|--year=YEARS -p -position=LAT,LON")
        print("\t[-i|--interpolate=MINUTES|METHOD]\n\t[-g|--glm[=GLMNAME]] [-n|--name=OBJECTNAME] [-c|--csv=CSVNAME]\n\t[--whoami] [--signup=EMAIL] [--apikey[=APIKEY]]\n\t[--test] [-v|--verbose] [-h|--help|help]")
    exit(code)

def verbose(msg):
    """Display a verbose message (verbose_enable must be True"""
    if verbose_enable:
        print(f"[{os.path.basename(sys.argv[0])}]: {msg}",file=sys.stderr)

def getemail():
    """Get the default email"""
    global email
    if not email:
        keys = getkeys(new=True).keys()
        if keys:
            email = list(getkeys().keys())[0]
        else:
            email = None
    return email

def addkey(apikey=None):
    """Manage NSRDB API keys"""
    global email
    global credential_file
    if not email:
        email = getemail()
    keys = getkeys(new=True)
    if email:
        if apikey or not email in keys.keys():
            keys[email] = apikey
        elif not apikey and email in keys.keys():
            del keys[email]
        with open(credential_file,"w") as f:
            json.dump(keys,f)

def getkeys(new=False):
    """Get all NSRDB API keys"""
    global credential_file
    try:
        os.mkdir(f"{os.getenv('HOME')}/.nsrdb")
    except FileExistsError:
        pass
    except Exception as err:
        warning(f"unable to create $HOME/.nsrdb folder for credentials ({err})")        
    try:
        with open(credential_file,"r") as f: 
            keys = json.load(f)
    except:
        if new:
            return {}
        raise Exception("unable to get API key for NSRDB data - see `gridlabd nsrdb_weather help` for detail on NSRDB access credentials")
    return keys

def getkey(email=None):
    """Get a single NSRDB API key"""
    if not email:
        email = getemail()
    if email:
        try:
            return getkeys()[email]
        except:
            return {}
    else:
        return None

def getyears(years,lat,lon,concat=True):
    """Get NSRDB weather data for multiple years"""
    try:
        result = {}
        for year in years:
            data = getyear(year,lat,lon)
            if result:
                for key,value in result.items():
                    result[key].extend(data[key])
            else:
                result = data
        if concat:
            result["DataFrame"] = pandas.concat(result["DataFrame"])
        if interpolate_time:
            final = []
            if concat:
                dflist = [result["DataFrame"]]
            else:
                dflist = result["DataFrame"]
            for data in dflist:
                verbose(f"getyears(years={years},lat={lat},lon={lon}): interpolating {interval} minute data to {interpolate_time} minutes using {interpolate_method} method")
                starttime = data.index.min()
                stoptime = data.index.max()
                daterange = pandas.DataFrame(index=pandas.date_range(starttime,stoptime,freq=f"{interpolate_time}min"))
                final.append(data.join(daterange,how="outer",sort=True).interpolate(interpolate_method))
            if concat:
                result["DataFrame"] = pandas.concat(final)
            else:
                result["DataFrame"] = final
        return result
    except Exception as err:
        if verbose_enable:
            raise
        else:
            error(f"unable to get data ({err})",2)

def heat_index(T,RH):
    """Compute the heat index for a temperature T (in degF) and relative humidity RH (in %)"""
    if T < 80 :
        return 0.75*T + 0.25*( 61.0+1.2*(T-68.0)+0.094*RH)
    else:
        HI = -42.379 \
            + 2.04901523*T \
            + 10.14333127*RH \
            - 0.22475541*T*RH \
            - 0.00683783*T*T \
            - 0.05481717*RH*RH \
            + 0.00122874*T*T*RH \
            + 0.00085282*T*RH*RH \
            - 0.00000199*T*T*RH*RH
        if RH < 13 and T < 112:
            return HI - ((13-RH)/4)*sqrt((17-fabs(T-95.))/17)
        elif RH > 85 and T < 87:
            return HI + ((RH-85)/10) * ((87-T)/5)
        else:
            return HI

def getcache(year,lat,lon,refresh=False):
    cache = f"{cachedir}/nsrdb/{year}/{geohash(lat,lon)}.csv"
    os.makedirs(os.path.dirname(cache),exist_ok=True)
    api = getkey()
    if not os.path.exists(cache) or refresh:
        with open(cache,"w") as fout:
            url = f"{server}?wkt=POINT({lon}%20{lat})&names={year}&leap_day={str(leap).lower()}&interval={interval}&utc={str(utc).lower()}&api_key={api}&attributes={attributes}&email={email}&full_name=None&affiliation=None&mailing_list=false&reason=None"
            verbose(f"getyear(year={year},lat={lat},lon={lon}): downloading data from {url}")
            fout.write(requests.get(url).content.decode("utf-8"))
            verbose(f"getyear(year={year},lat={lat},lon={lon}): saved data to {cache}")
    return cache

def getyear(year,lat,lon):
    """Get NSRDB weather data for a single year"""
    api = getkey()
    url = f"{server}?wkt=POINT({lon}%20{lat})&names={year}&leap_day={str(leap).lower()}&interval={interval}&utc={str(utc).lower()}&api_key={api}&attributes={attributes}&email={email}&full_name=None&affiliation=None&mailing_list=false&reason=None"
    cache = f"{cachedir}/nsrdb/{year}/{geohash(lat,lon)}.csv"
    try:
        result = pandas.read_csv(cache,nrows=1).to_dict(orient="list")
        try:
            result.update(dict(Year=[year],DataFrame=[pandas.read_csv(cache,skiprows=2)]))
            verbose(f"getyear(year={year},lat={lat},lon={lon}): reading data from {cache}")
        except Exception as err:
            os.remove(cache)
            raise Exception(f"cache file '{cache}' is not readable ({err}), try again later")
    except:
        result = None
    if not result:
        os.makedirs(os.path.dirname(cache),exist_ok=True)
        with open(cache,"w") as fout:
            verbose(f"getyear(year={year},lat={lat},lon={lon}): downloading data from {url}")
            fout.write(requests.get(url).content.decode("utf-8"))
            verbose(f"getyear(year={year},lat={lat},lon={lon}): saved data to {cache}")
        try:
            result = pandas.read_csv(cache,nrows=1).to_dict(orient="list")
        except Exception as err:
            os.remove(cache)
            raise Exception(f"cache file '{cache}' is not readable ({err}), try again later")
        result.update(dict(Year=[year],DataFrame=[pandas.read_csv(cache,skiprows=2)]))
    for data in result["DataFrame"]:
        data["datetime"] = list(map(lambda x: datetime.datetime(x[0],x[1],x[2],x[3],0,0),numpy.array([data.Year,data.Month,data.Day,data.Hour]).transpose()))
        data.set_index("datetime",inplace=True)
        data.drop(columns=["Year","Day","Month","Hour","Minute"],inplace=True)
        data.columns = [
            "solar_global[W/sf]",
            "solar_horizontal[W/sf]",
            "solar_direct[W/sf]",
            "clouds",
            "dewpoint[degF]",
            "temperature[degF]",
            "ground_reflectivity[pu]",
            "wind_speed[m/s]",
            "wind_dir[rad]",
            "solar_altitude[deg]",
            "humidity[%]",
            "pressure[mbar]",
            ]
        data["clouds"] = data["clouds"].abs()
        data["solar_global[W/sf]"] /= 10.7639
        data["solar_horizontal[W/sf]"] /= 10.7639
        data["solar_direct[W/sf]"] /= 10.7639
        data["dewpoint[degF]"] = data["dewpoint[degF]"]*9/5+32
        data["temperature[degF]"] = data["temperature[degF]"]*9/5+32
        data["wind_dir[rad]"] *= 3.141592635/180
        data["heat_index[degF]"] = list(map(lambda x:heat_index(x[0],x[1]),zip(data["temperature[degF]"],data["humidity[%]"])))
        data.index.name = "datetime"
    return result

def decode_exactly(geohash):
    """
    Decode the geohash to its exact values, including the error
    margins of the result.  Returns four float values: latitude,
    longitude, the plus/minus error for latitude (as a positive
    number) and the plus/minus error for longitude (as a positive
    number).
    """
    __base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    __decodemap = { }
    for i in range(len(__base32)):
        __decodemap[__base32[i]] = i
    del i
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    lat_err, lon_err = 90.0, 180.0
    is_even = True
    for c in geohash:
        cd = __decodemap[c]
        for mask in [16, 8, 4, 2, 1]:
            if is_even: # adds longitude info
                lon_err /= 2
                if cd & mask:
                    lon_interval = ((lon_interval[0]+lon_interval[1])/2, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], (lon_interval[0]+lon_interval[1])/2)
            else:      # adds latitude info
                lat_err /= 2
                if cd & mask:
                    lat_interval = ((lat_interval[0]+lat_interval[1])/2, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], (lat_interval[0]+lat_interval[1])/2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lat, lon, lat_err, lon_err

def geocode(geohash):
    """
    Decode geohash, returning two strings with latitude and longitude
    containing only relevant digits and with trailing zeroes removed.
    """
    lat, lon, lat_err, lon_err = decode_exactly(geohash)
    from math import log10
    # Format to the number of decimals that are known
    lats = "%.*f" % (max(1, int(round(-log10(lat_err)))) - 1, lat)
    lons = "%.*f" % (max(1, int(round(-log10(lon_err)))) - 1, lon)
    if '.' in lats: lats = lats.rstrip('0')
    if '.' in lons: lons = lons.rstrip('0')
    return float(lats), float(lons)

def geohash(latitude, longitude, precision=geocode_precision):
    """Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.
    """
    from math import log10
    __base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    __decodemap = { }
    for i in range(len(__base32)):
        __decodemap[__base32[i]] = i
    del i
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bits = [ 16, 8, 4, 2, 1 ]
    bit = 0
    ch = 0
    even = True
    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(geohash)


def writeglm(data, glm=None, name=None, csv=None):
    """Write weather object based on NSRDB data

    Default GLM and CSV values are handled as follows

    GLM    CSV    Output
    ------ ------ -------------------------------
    None   None   CSV->stdout 
    GLM    None   GLM, CSV->GLM/.glm/.csv
    None   CSV    GLM->stdout, CSV
    GLM    CSV    GLM, CSV

    The default name is "weather@GEOCODE"

    The WEATHER global is set to the list of weather object names.
    """
    lat = data['Latitude'][0]
    lon = data['Longitude'][0]
    if not name:
        name = f"weather@{geohash(lat,lon,geocode_precision)}"
    if type(data["DataFrame"]) is list:
        weather = pandas.concat(data["DataFrame"])
    else:
        weather = data["DataFrame"]
    if not csv and not glm:
        csv = "/dev/stdout"
    elif not csv:
        csv = f"{name}.csv"
    elif not glm:
        glm = "/dev/stdout"
    if glm and glm != "/dev/null":
        with open(glm,"w") as f:
            f.write("class weather\n{\n")
            for column in weather.columns:
                if column != "clouds":
                    f.write(f"\tdouble {column};\n")
                else:
                    f.write("\tenumeration {CLEAR=0,PROBABLY_CLEAR=1, FOG=2, WATER=3, SUPERCOOLED_WATER=4, MIXED=5, OPAQUE_ICE=6, CIRRUS=7, OVERLAPPING=8, OVERSHOOTING=9, UNKNOWN=10, DUST=11, SMOKE=12, NA=15} clouds;\n")
            f.write("}\n")
            weather.columns = list(map(lambda x:x.split('[')[0],weather.columns))
            f.write("module tape;\n")
            f.write("#ifdef WEATHER\n")
            f.write(f"#set WEATHER=$WEATHER {name}\n")
            f.write("#else\n")
            f.write(f"#define WEATHER={name}\n")
            f.write("#endif\n")
            f.write("object weather\n{\n")
            f.write(f"\tname \"{name}\";\n")
            f.write(f"\tlatitude {lat};\n")
            f.write(f"\tlongitude {lon};\n")
            f.write("\tobject player\n\t{\n")
            f.write(f"\t\tfile \"{csv}\";\n")
            f.write(f"\t\tproperty \"{','.join(weather.columns)}\";\n")
            f.write("\t};\n")
            f.write("}\n")
            weather.to_csv(csv,header=False,float_format=float_format,date_format="%s")
            return dict(glm=glm,csv=csv,name=name)
    else:
        weather.to_csv(csv,header=True,float_format=float_format,date_format=date_format)
        return dict(glm=None,csv=csv,name=None)


year = None
position = None
glm = None
csv = None
name = None

def main(inputs,outputs,options={}):
    
    global position
    global year
    global name
    global glm
    global csv

    if type(options) is list:
        for option in options:
            if option[0] == "-":
                raise Exception(f"flag '{option}' is invalid")
            elif "=" in option:
                spec = option.split("=")
                if spec[0] in globals().keys():
                    globals()[spec[0]] = "=".join(spec[1:])
                else:
                    raise Exception(f"option name '{spec[0]}' is not found")
            else:
                raise Exception(f"{options} is invalid ")
    else:
        for option, value in options.items():
            globals()[option] = value

    if not position:
        raise Exception("position not specified")
    elif type(position) is str:
        position = list(map(lambda x:float(x),position.split(",")))

    if not year:
        raise Exception("year not specified")
    elif type(year) is str:
        year = list(map(lambda x:int(x),year.split(",")))

    if inputs and inputs != ['/dev/null']:
        raise Exception("weather does not take inputs")

    if not type(outputs) is list:
        raise Exception("outputs list is not valid")

    csv = outputs[0]
    if len(outputs) > 1:
        glm = outputs[1]

    try:
        data = getyears(year,float(position[0]),float(position[1]))
        writeglm(data,glm,name,csv)
    
    except Exception as err:
    
        if not debug_enable:
            error(err,1)
        raise

if __name__ == "__main__":

    if len(sys.argv) == 1:
        syntax(1)
    for arg in sys.argv[1:]:
        args = arg.split("=")
        if type(args) is list and len(args) > 1:
            token = args[0]
            value = args[1]
        elif type(args) is list:
            token = args[0]
            value = None
        else:
            token = args
            value = None
        if token in ["-h","--help","help"]:
            syntax()
        elif token == "--debug":
            debug_enable = True
        elif token in ["-y","--year"]:
            year = []
            for y in value.split(","):
                yy = y.split("-")
                if len(yy) == 1:
                    year.append(int(yy[0]))
                elif len(yy) == 2:
                    year.extend(range(int(yy[0]),int(yy[1])+1))
                else:
                    raise Exception("'{value}' is not a valid invalid year specification")
        elif token in ["-p","--position"]:
            position = value.split(",")
            if len(position) != 2:
                error("position is not a tuple",1)
        elif token in ["-i","--interpolate"]:
            try:
                interpolate_time = int(value)
            except:
                if value:
                    interpolate_method = value
                else:
                    interpolate_time = None
        elif token in ["-g","--glm"]:
            glm = value
        elif token in ["-n","--name"]:
            name = value
        elif token in ["-c","--csv"]:
            csv = value
        elif token == "--test":
            year = [2014,2015]
            position = [45.62,-122.70]
            glm = "test.glm"
            writeglm(getyears(year,float(position[0]),float(position[1])),glm,name,csv)
            exit(os.system(f"gridlabd {glm}"))
        elif token == "--signup":
            if not value:
                error("you must provide an email address for the new credential",1)
            credentials = getkeys(new=True)
            if getemail() in credentials.keys():
                error(f"you already have credentials for {value}",1)
            else:
                email = value
                addkey("PASTE_YOUR_APIKEY_HERE")
            import webbrowser
            webbrowser.open("https://developer.nrel.gov/signup/")
            print(f"use `gridlabd nsrdb_weather --apikey=<your-apikey>` to set your api key")
        elif token == "--apikey":
            if not getemail():
                error(f"you have not signed up yet, use `gridlabd {os.path.basename(sys.argv[0]).replace('.py','')} --signup=<your-email>` to sign up",1)
            key = getkey(email)
            addkey(value)
            if not value:
                print(f"key for {email} deleted, use `gridlabd {os.path.basename(sys.argv[0]).replace('.py','')} --apikey={key}` to restore it")
        elif token == "--whoami":
            if not getemail():
                error(f"you have not signed up yet, use `gridlabd {os.path.basename(sys.argv[0]).replace('.py','')} --signup=<your-email>` to sign up",1)
            print(email,file=sys.stdout)
        elif token in ["-v","--verbose"]:
            verbose_enable = not verbose_enable
        elif token in ["-e","--encode"]:
            position = value.split(",")
            if len(position) != 2:
                error("position is not a tuple",1)
            print(geohash(float(position[0]),float(position[1])),file=sys.stdout)
        elif token in ["--clear"]:
            import shutil
            shutil.rmtree(cachedir)
        else:
            error(f"option '{token}' is not valid",1)
    
    main(inputs=None,outputs=[csv,glm])
