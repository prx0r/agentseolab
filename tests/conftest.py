"""Pytest config for the lab test suite.

test_field_protocol.py is a standalone script-style checker owned by the
field-protocol worker; it calls sys.exit at module level and breaks pytest
collection when imported as a test module. Exclude it here rather than
editing another worker's file.
"""
collect_ignore_glob = ["test_field_protocol.py"]
