"""PATCH 2 - in konsumo/cli.py, replace `cmd_serve` with this version."""


def cmd_serve(args):
    from .web.app import run_server
    print(f"Dashboard at http://{args.host}:{args.port}")
    run_server(args.db, args.host, args.port)
