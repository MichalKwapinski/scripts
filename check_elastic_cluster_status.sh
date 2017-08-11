#!/bin/bash

STATUS=`curl -s 'http://es-server-ip:9200/_cluster/health?pretty=true' | grep \"status\" | tr -d '",\ ' | awk -F: '{print $2}'`
OK=0
WARNING=1
ERROR=2


if [ "$STATUS" == "green" ]; then
        echo "$OK"
        exit $OK
elif [ "$STATUS" == "yellow" ]; then
        echo "$WARNING"
        exit $WARNING
else
        echo "$ERROR"
        exit $ERROR
fi

