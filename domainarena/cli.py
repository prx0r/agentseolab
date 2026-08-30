"""CLI entry point for domainarena."""
import sys
import uvicorn


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8777
    uvicorn.run("domainarena.api.http:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
