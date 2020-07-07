#!/bin/bash
chmod 777 logs
service nginx start
uwsgi --ini uwsgi.ini