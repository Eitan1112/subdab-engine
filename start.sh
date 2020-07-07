#!/bin/bash
chmod 777 logs
uwsgi --ini uwsgi.ini
service nginx start