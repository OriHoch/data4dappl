#!/usr/bin/env bash

SCRIPT_NAME="$@"

cd /pipelines

echo `date` running $SCRIPT_NAME | tee -a "${SCRIPT_NAME}.statuslog"
if ipython "./${SCRIPT_NAME}.py" > "${SCRIPT_NAME}.lastlog" 2>&1; then
  ls -lah "${SCRIPT_NAME}.lastlog" | tee -a "${SCRIPT_NAME}.statuslog"
  echo `date` OK | tee -a "${SCRIPT_NAME}.statuslog"
else
  ls -lah "${SCRIPT_NAME}.lastlog" | tee -a "${SCRIPT_NAME}.statuslog"
  echo `date` ERROR, check the last log
fi
