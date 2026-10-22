"""Compatibility entrypoint for `python reproof.py`."""
from reproof.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
