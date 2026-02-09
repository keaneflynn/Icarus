import os
import json
import sqlite3
from paramiko import SSHClient
from scp import SCPClient


class remoteFetch:
    @staticmethod
    def retrieveDBFile(hostname, user, passwd, dp_path, site_name):
        # Create ssh tunnel
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname, username = user, password = passwd)
        # Initialize & execute SCP of file
        scp = SCPClient(ssh.get_transport())
        scp.get(os.path.join(dp_path), 
                os.path.join(os.getcwd(), 'src', 
                             site_name + '_birds.db'))
        # Close ssh connection
        scp.close()
    
    @staticmethod
    def birdDBQuery(site_name):
        sqlite_db = os.path.join(os.getcwd(), 'src', site_name + '_' + 'birds.db')
        con = sqlite3.connect(sqlite_db)
        cur = con.cursor()
        # Fetch all bird entries from detections database
        birds = cur.execute("SELECT Date, Time, Sci_Name, Com_Name, Confidence, " \
        "Lat, Lon, Cutoff, Week, Sens, Overlap FROM detections WHERE " \
        "com_name != 'Pacific Chorus Frog'").fetchall()
        # Close SQL connection
        con.close()

        return birds
    
    @staticmethod
    def frogDBQuery(site_name):
        sqlite_db = os.path.join(os.getcwd(), 'src', site_name + '_' + 'birds.db')
        con = sqlite3.connect(sqlite_db)
        cur = con.cursor()
        # Fetch all frog entries from detections database, since we only have 
        # Pacific Chorus Frogs up there this can be done by querying 
        # species specific
        frogs = cur.execute("SELECT Date, Time, Sci_Name, Com_Name, Confidence, " \
        "Lat, Lon, Cutoff, Week, Sens, Overlap FROM detections WHERE " \
        "com_name = 'Pacific Chorus Frog'").fetchall()
        # Close SQL connection
        con.close()

        return frogs
