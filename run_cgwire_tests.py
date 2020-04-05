import sys
import nose
import os
import warnings
import subprocess
import requests
import pymongo

# Try/Except for prevent error in import testing.
try:
    import gazu
except ImportError:
    pass

warnings.filterwarnings("ignore", category=DeprecationWarning)

if __name__ == "__main__":

    argv = sys.argv[:]
    argv.extend([

        # Sometimes, files from Windows accessed
        # from Linux cause the executable flag to be
        # set, and Nose has an aversion to these
        # per default.
        "--exe",

        "--verbose",
        "--with-doctest",

        "--with-coverage",
        "--cover-html",
        "--cover-tests",
        "--cover-erase",
        "--cover-package=avalon.cgwire"
    ])

    os.chdir("avalon/cgwire")

    subprocess.Popen("/opt/zou/start_zou.sh")

    # Wait for CGWire server to come online.
    host = "http://127.0.0.1/api"
    gazu.client.set_host(host)
    while True:
        try:
            response = gazu.client.requests_session.post(
                gazu.client.get_full_url(host),
                json={
                    "email": "admin@example.com",
                    "password": "mysecretpassword"
                },
                headers=gazu.client.make_auth_header()
            )
            if response.status_code != 502:
                break
        except requests.exceptions.ConnectionError:
            pass
        except gazu.exception.ServerErrorException:
            pass

    # Clear database for testing.
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    for collection in db.list_collection_names():
        db[collection].drop()

    nose.main(argv=argv)
