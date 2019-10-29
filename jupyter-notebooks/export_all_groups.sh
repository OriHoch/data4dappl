#!/usr/bin/env sh

date
echo running export all groups
if ipython "./export all groups.py" > "export all groups.log" 2>&1; then
  echo OK
else
  echo ERROR, check the log
fi
