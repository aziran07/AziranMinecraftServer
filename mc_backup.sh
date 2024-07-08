#!/bin/bash


timevar=$(date +"%Y-%m-%d_%T")
cd /home/pilon1945/AziranMinecraftServer
tar -cf ./minecraft_backups/${timevar}_world.tar ./server-data/world
find ./minecraft_backups/ -type f -mmin +290 | xargs rm -f
