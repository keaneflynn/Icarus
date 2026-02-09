import os
import psycopg
from dotenv import load_dotenv


class postgresManagement:
    def __init__(self):
        load_dotenv(override=True)
        self.dbname = os.getenv('DBNAME')
        self.user = os.getenv('USER')
        self.password = os.getenv('PASSWORD')
        self.host = os.getenv('HOST')
        self.port = os.getenv('PORT')

    def appendBirdList(self, bird_list, bird_iter, site_name, ip_address):
        # Add site name and ip address to record to be appended to db
        bird_iter = [tuple(list(element) + [site_name] + [ip_address] + 
                           [str(element[0] + ' ' + element[1])]) 
                           for element in bird_iter]
        bird_list += bird_iter
        # ADD IN HERE TO ADD COLUMN FOR DATETIME IN ADDITION TO DATE, TIME
        return bird_list
    
    def appendFrogList(self, frog_list, frog_iter, site_name, ip_address):
        # Add site name and ip address to record to be appended to db
        frog_iter = [tuple(list(element) + [site_name] + [ip_address] + 
                           [str(element[0] + ' ' + element[1])]) 
                           for element in frog_iter]
        frog_list += frog_iter
        # ADD IN HERE TO ADD COLUMN FOR DATETIME IN ADDITION TO DATE, TIME
        return frog_list

    def appendBirdEntries(self, bird_list):
        # Create connection to Postgres DB
        with psycopg.connect(
            dbname = self.dbname,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port) as conn:

            # Create connection pipeline for commands
            with conn.cursor() as cur:

                # Execute SQL command and store values
                cur.executemany(
                    # STILL NEED TO ADD DATETIME AND %S IN HERE THEN UPDATE DB
                    """INSERT INTO bird_audio 
                    (uuid, date, time, sci_name, com_name, confidence, 
                    latitude, longitude, cutoff, week, sens, overlap, 
                    site, ip_address, datetime) 
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s) ON CONFLICT 
                    (date, time, com_name, confidence, site) DO NOTHING""",
                    bird_list)
                
            # Commit changes 
            conn.commit()    
                
            # Close postgres connection    
            cur.close()
            conn.close()

    def appendFrogEntries(self, frog_list):
        # Create connection to Postgres DB
        with psycopg.connect(
            dbname = self.dbname,
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port) as conn:

            # Create connection pipeline for commands
            with conn.cursor() as cur:

                # Execute SQL command and store values
                cur.executemany(
                    # STILL NEED TO ADD DATETIME AND %S IN HERE THEN UPDATE DB
                    """INSERT INTO frog_audio 
                    (uuid, date, time, sci_name, com_name, confidence, 
                    latitude, longitude, cutoff, week, sens, overlap, 
                    site, ip_address, datetime)  
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s) ON CONFLICT 
                    (date, time, com_name, confidence, site) DO NOTHING""",
                    frog_list)
                
            # Commit changes 
            conn.commit()    
                
            # Close postgres connection    
            cur.close()
            conn.close()

 
