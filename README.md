# Icarus
**Author**: Keane Flynn\
**Organization**: Summit Lake Paiute Tribe\
**Date**: 06/20/2025\
**Contact**: keaneflynn1@gmail.com

## Overview
Icarus is a program that connects to our BirdNet detection stations around the 
reservation to pull bird and frog audio detections and append them to our respective
databases. This program will connect to the raspberry pis, gather the most recent 
detections from its SQLite database and append those records to our postgres 
database on our server. It can be run at whatever frequency desired through 
systemd or cronjob, but every hour or so should be more than adequate.

## Prerequisites
In order for this software to successfully run, there will need to be two 
database tables created in PostgreSQL one for the bird detection and one for 
frog detections. I elected to separate them as the frogs don't ever shut up for
eight months out of the year and it would bog down an already over-encumbered
bird database table. To create the bird table, issue the following command to 
create the desired schema:
```
CREATE TABLE bird_audio(
	uuid uuid,
	date date,
	time time without time zone,
	sci_name text,
	com_name text,
	confidence numeric,
	lat numeric,
	lon numeric,
	cutoff numeric,
	week smallint,
	sens numeric,
	overlap numeric,
	site_name text,
	ip_address text);
```
Then create the frog table:
```
CREATE TABLE frog_audio(
	uuid uuid,
	date date,
	time time without time zone,
	sci_name text,
	com_name text,
	confidence numeric,
	lat numeric,
	lon numeric,
	cutoff numeric,
	week smallint,
	sens numeric,
	overlap numeric,
	site_name text,
	ip_address text);
```
Finally cast the correct constraints on each table to ensure there cannot be any
duplicated records since this application runs on an upsert premise:
```
ALTER TABLE bird_audio ADD CONSTRAINT bird_constraint UNIQUE (date, time, com_name, confidence, site_name);
ALTER TABLE frog_audio ADD CONSTRAINT frog_constraint UNIQUE (date, time, com_name, confidence, site_name);
```
You will also need to ensure the PostgreSQL database service has auto-generating
UUIDs enabled, but this is already likely taken care of:
```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```
Lastly, since this relies on SCP of db files you will need to ssh into each 
client from the application server before you can run it so each client will
be in the ssh list of known hosts.

## Hardware
This software is specifically designed to extract data from a BirdNET raspberry 
pi setup and sync it to whatever server it is running on; in this case on the 
SLPT Lambda server at SCS.

Currently, the BirdNET software loaded onto the client devices is from [Patrick
McGuire's original BirdNET repository](https://github.com/mcguirepr89/BirdNET-Pi)
running on Raspberry Pi 4b+ devices with 8gb of ram. This repository is a bit 
outdated and not really maintained anymore, but can still be run on raspi running
Debian Bullseye version 11 release (just needs to be running python 3.9 and it 
will work). In the future, if the devices break it may be worthwhile to switch 
over to Raspberry Pi 5s and run [Nachtzuster's forked repo of BirdNET that is 
functional for Pi 5s and is maintained](https://github.com/Nachtzuster/BirdNET-Pi).

The only changes that will need to be made to the client configuration to each 
raspberry pi from the OEM setup is to add the custom bird species list for the
reservation put together by Megan Yount. This can be found [in the src/ directory
of the respository](https://github.com/SummitLakeNRD/Icarus/blob/main/src/bird_list.txt)
and needs to be placed in the `scripts/` subdirectory of the birdnet client build.

## Input & Output
All input parameters can be found using the `python -h` flag 

### Inputs
*Client List*: A text file with rows of the following information:
```
{
	"IP_ADDRESS_1": 
	{
		"username": "<USER>",
		"password": "<PASSWORD",
		"sqlite_path": "/PATH/TO/BIRDNET/birds.db",
		"sitename": "SITE1"
	},
	"IP_ADDRESS_2":  
    {       
		"username": "<USER>",
		"password": "<PASSWORD>",
		"sqlite_path": "/PATH/TO/BIRDNET/birds.db",
		"sitename": "SITE2"
    }
}
```
You will also need to create a .env file (place in ./src/ directory) with the
following setup:
```
DBNAME=<DBNAME>
USER=<USER>
PASSWORD=<PASSWORD>
HOST=<HOST>
PORT=<PORT>
```

### Outputs
*uuid*: uuid generated for each record\ 
*date*: YYYY-MM-DD format\
*time*: HH:MM:SS with no time zone\
*sci_name*: Scientific name of detected critter\
*com_name*: Common name of detected critter\
*confidence*: 0-1 float value confidence of critter detection\
*lat*: latitude WGS84 of station\
*lon*: longitude WGS84 of station\
*cutoff*: minimum confidence threshold to enable detection\
*week*: 1-52 week of the year\
*sens*: Sigmoid sensitivity, has to do with confidence of faint calls (no clue)\
*overlap*: If there can be a time-overlap of detection between individual detections\
*site_name*: User definied site name from client file\
*ip_address*: User defined IP address of each site from client file

## How To Use
Issue the following command in your terminal to clone the repository:
```
git clone https://github.com/SummitLakeNRD/Icarus.git
```
You will then need to `cd Icarus/` and create a python virtual environment to 
install the correct dependencies.
```
python -m venv ./
```
Then activate the virtual environment:
```
source bin/activate
```
Then install the necessary dependencies for this repository:
```
pip install -r requirements.txt
```

While this program will be run as a cronjon, it can be tested by running 
`python icarus.py -h` to view the necessary positional arguments.

### Running as Cronjob
This program is primarily designed to be run on a server as a cronjob.
To SLPT staff, in short, this means that given the proper instruction, it will
run continuously on start up and restart if the program crashes for some reason.
To make this work, you will need to modify the crontab file:
```
crontab -e
```
You will then need to insert the following line from the 
[cron/cronjobSample.txt](https://github.com/SummitLakeNRD/Icarus/blob/main/cron/cronjobSample.txt)
with updated file paths for the server:
```
0 */1 * * * cd /path/to/venv/ && /path/to/venv/bin/python3 /path/to/venv/icarus.py /path/to/venv/src/.clients > /path/to/venv/errorLogs/output.log 2>&1
```
As written above, this program will run at the top of each hour and output any
errors to the specified error log file in the repository.

## Troubleshooting
This program was written with a fair amount of error handling and will output 
an error log. This log is generated by default from the systemd service file 
and can be found in the following directory location: `./errorLogs/error.log`. 
While I have tried to make this as easy to read for the non-technically inclined, 
it should point you to at least the source of the issue. If you can't figure 
that out, email Keane at the contact email at the top of this document. 

