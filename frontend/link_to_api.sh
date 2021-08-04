#!/bin/bash
clear
echo Fetching API endpoint from Cache ...

tmp_file="/tmp/hermes_stored_endpoint.bin"
config_json="./src/config.json"

if [ -f $tmp_file ] ; then
    echo Used cached file !
    varendpoint=$(cat $tmp_file)
    echo OK ! This is the endpoint: $varendpoint
else
    echo API endpoint not found, please type it : \(eg: https://api.website.com or :443 for relative URL with frontend\)
    read varendpoint
    echo OK ! This is the endpoint: $varendpoint
    echo Will store it in cache !
    echo $varendpoint >> $tmp_file
fi

echo Creating the config file for the frontend ...
if [ -f $config_json ] ; then
    rm $config_json
fi

echo " 
{
    \"api_url\": \"$varendpoint\",
    \"api_default_timeout\": 15000
}
" >> $config_json

exit 0