from meteorite_project.app import create_app
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--debug", type=int, choices=[0,1], default=1)
    args = parser.parse_args()

    app = create_app()
    app.run_server(host=args.host, port=args.port, debug=bool(args.debug))

if __name__ == "__main__":
    main()
