#!/usr/bin/env sh

service jetty8 restart

sleep 2

tail -f /var/log/jetty8/out.log
