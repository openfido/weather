#!/bin/bash

OUTPUT=/dev/stdout
if [ "$1" == "-v" -o "$1" == "--verbose" ]; then
    set -x
elif [ "$1" == "-q" -o "$1" == "--quiet" ]; then
    OUTPUT=/dev/null
fi

TESTED=0
FAILED=0

# run_test()
# {
#     echo "Processing $1..." >$OUTPUT
#     TESTED=$(($TESTED+1))
#     mkdir -p $1
#     cd $1
#     shift 1
#     if ! gridlabd nsrdb_weather $* 1>openfido.out 2>openfido.err; then
#         echo "ERROR: $(basename $PWD) test failed (exit code $?)" > $OUTPUT
#         FAILED=$(($FAILED+1))
#     fi
#     cd - > /dev/null
# }

# check_file()
# {
#     if -f $1/$2 -a ! diff $1/$2 $2 1>>$1/openfido.out 2>>$1/openfido.err; then
#         echo "ERROR: $1 check of $2 failed (outputs differ)" > $OUTPUT
#         FAILED=$(($FAILED+1))
#     fi
# }

# # test simple weather query
# run_test test_weather --year=2020 --position=37.4,-122.3 --csv=weather.csv
# check_file test_weather weather.csv

# # test weather query with model
# run_test test_weather_glm --year=2020 --position=37.4,-122.3 --csv=weather_glm.csv --glm=weather_glm.glm
# check_file test_weather_glm weather_glm.csv
# check_file test_weather_glm weather_glm.glm

# # test weather query with named object
# run_test test_weather_name --year=2020 --position=37.4,-122.3 --csv=weather_name.csv --glm=weather_name.glm --name=test
# check_file test_weather_name weather_name.csv
# check_file test_weather_name weather_name.glm

export TZ=UTC

for DIR in autotest/input_*; do
    echo -n "Processing $(basename $DIR)..."
    export OPENFIDO_INPUT=$DIR
    # cp $HOME/.nsrdb/credentials.json $OPENFIDO_INPUT
    export OPENFIDO_OUTPUT=${DIR/\/input_/\/output_}
    mkdir -p $OPENFIDO_OUTPUT
    if ! sh openfido.sh 1>$OPENFIDO_OUTPUT/openfido.out 2>$OPENFIDO_OUTPUT/openfido.err; then
        FAILED=$(($FAILED+1))
        echo "RUN FAILED"
    else
        cp /dev/null $OPENFIDO_OUTPUT/openfido.diff
        DIFFER=0
        DIFFERS=""
        for FILE in ${OPENFIDO_INPUT}/*.{csv,glm}; do
            TEST="${FILE/$OPENFIDO_INPUT/$OPENFIDO_OUTPUT}"
            if [ -f "$TEST" ]; then
                if ! diff $FILE $TEST 1>>$OPENFIDO_OUTPUT/openfido.diff 2>&1; then
                    DIFFER=$(($DIFFER+1))
                    DIFFERS="$(basename $TEST) $DIFFERS"
                fi
            fi
        done
        if [ $DIFFER -gt 0 ]; then
            echo "$DIFFER FILES DIFFER: $DIFFERS"
            FAILED=$(($FAILED+1))
        else
            echo "OK"
        fi
    fi
    TESTED=$(($TESTED+1))
done

echo "$TESTED tests processed" >$OUTPUT
echo "$FAILED tests failed" >$OUTPUT

if [ $FAILED -gt 0 ]; then
    tar cfz autotest-errors.tar.gz autotest
fi

exit $FAILED
