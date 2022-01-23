#!/bin/bash
cd autotest

set -x

if [ -z "$(openfido show weather)" ]; then
    openfido install weather
else
    openfido update weather
fi

run_test()
{
    echo Processing $1...
    mkdir -p $1
    cd $1
    shift 1
    openfido run weather $* 1>openfido.out 2>openfido.err
    cd - > /dev/null
}

check_file()
{
    diff $1/$2 $2
}

# test simple weather query
run_test test_weather year=2020 position=37.4,-122.3 /dev/null weather.csv,/dev/null
check_file test_weather weather.csv

# test weather query with model
run_test test_weather_glm year=2020 position=37.4,-122.3 /dev/null weather_glm.csv,weather_glm.glm
check_file test_weather_glm weather_glm.csv
check_file test_weather_glm weather_glm.glm

# test weather query with named object
run_test test_weather_name year=2020 position=37.4,-122.3 /dev/null weather_name.csv,weather_name.glm name=test
check_file test_weather_name weather_name.csv
check_file test_weather_name weather_name.glm
