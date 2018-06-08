#!/usr/bin/env bash

function new_file {
	file=$1
	new_file=${file%.dist}

	if [[ ! -f "$new_file" ]]
	then
		cp $file $new_file
	fi
}

new_file ../shopelectro/settings/local.py.dist
