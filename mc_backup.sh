#!/bin/bash


timevar=$(date +"%Y-%m-%d_%T")
tar -cf ./minecraft_backups/${timevar}_world.tar ./server-data/world
find ./minecraft_backups/ -type f -mmin +290 | xrgs rm -f