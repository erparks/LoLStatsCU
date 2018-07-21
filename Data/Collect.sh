#!/bin/sh
gnome-terminal -e "python3 ../Python/Collect_Data.py $1 NA1"

gnome-terminal -e "python3 ../Python/Collect_Data.py $1 EUW1"

gnome-terminal -e "python3 ../Python/Collect_Data.py $1 KR"
