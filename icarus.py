import json
from argparse import ArgumentParser
from src.postgresManagement import postgresManagement
from src.remoteQuery import remoteFetch
from sqlite3 import OperationalError as SqliteError
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException


def main():
    parser = ArgumentParser(description='Icarus program to append bird detection to DB')
    parser.add_argument('client_list', type=str, help='file with client list and info')
    args = parser.parse_args()

    with open(args.client_list) as file:
        client_data = json.load(file)
    
    postgres = postgresManagement()
    bird_list = []
    frog_list = []

    for client, client_info in client_data.items():
        # Copy DB file from remote server to local
        try:
            remoteFetch.retrieveDBFile(client, 
                                       client_info['username'], 
                                       client_info['password'],
                                       client_info['sqlite_path'],
                                       client_info['sitename'])
            
        except NoValidConnectionsError as e:
            print("NoValidConnectionsError: likely network failure or " \
            "incorrect hostname provided. Details: {}".format(e))
            continue
        except AuthenticationException as e:
            print("Authentication Error: invalid remote host credentials " \
            "provided for SCP process: {}".format(e))
            continue
        except Exception as e:
            print("An unexpected error occurred: {}".format(e))
            continue

        # Query all entries for birds from the client sqlite3 file
        try: 
            bird_iter = remoteFetch.birdDBQuery(client_info['sitename'])
        except SqliteError as e:
            print("Error obtaining sqlite3 database access, " \
            "check credentials: {}".format(e))

        # Append all bird entries from bird audio client to list
        bird_list = postgres.appendBirdList(bird_list, bird_iter, 
                                            client_info['sitename'],
                                            client)
        
        # Query all entries for frogs from the client sqlite3 file
        try:
            frog_iter = remoteFetch.frogDBQuery(client_info['sitename'])
        except SqliteError as e:
            print("Error obtaining sqlite3 database access, " \
            "check credentials: {}".format(e))

        # Append all bird entries from bird audio client to list
        frog_list = postgres.appendFrogList(frog_list, frog_iter,
                                            client_info['sitename'],
                                            client)
        
    # Append all bird entries from appended list to postgres 
    try:
        postgres.appendBirdEntries(bird_list)
    except Exception as e:
        print("An unexpected error occurred: {}".format(e))

    # Append all frog entries from appended list to postgres
    try:
        postgres.appendFrogEntries(frog_list)
    except Exception as e:
        print("An unexpected error occurred: {}".format(e))
    

if __name__ == '__main__':
    main()
