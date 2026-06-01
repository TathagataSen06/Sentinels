#! /bin/bash

CONF="/etc/sentinelsd/sentinels.conf"
TEMP_CONF="/etc/sentinelsd/.sentinels.conf"

if [ ! -z "$SENTINELS_CONFIG_URL" ]; then
    echo "INFO: Fetching dynamic configuration from $SENTINELS_CONFIG_URL"
    wget -qO $CONF "$SENTINELS_CONFIG_URL" || curl -sLo $CONF "$SENTINELS_CONFIG_URL"
    if [ $? -eq 0 ]; then
        echo "INFO: Successfully downloaded dynamic configuration."
    else
        echo "ERROR: Failed to download dynamic configuration from $SENTINELS_CONFIG_URL."
    fi
fi

if [ -f $CONF ]; then
	echo "INFO: Main configuration file found"
	sentinelsd --start
elif [ -f $TEMP_CONF ]; then
	echo "INFO: Temp configuration file found"
	sentinelsd --dev
else
	sentinelsd --copyconfig && echo "A Config file was generated at /etc/sentinelsd/.sentinels.conf."
fi
