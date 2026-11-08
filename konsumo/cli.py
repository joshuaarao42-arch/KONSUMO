import argparse
from .config import DEFAULT_DB_PATH
from .database import init_db
def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['seed','serve']); p.add_argument('--db',default=DEFAULT_DB_PATH); p.add_argument('--user-id',type=int,help='Account ID that owns seeded demo records'); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=5000); a=p.parse_args(); init_db(a.db)
    if a.command=='seed':
        from .seed import seed
        if not a.user_id: p.error('seed requires --user-id so demo records are assigned to one account')
        seed(a.db, user_id=a.user_id)
    else:
        from .web.app import run_server; run_server(a.db,a.host,a.port)
if __name__=='__main__': main()
