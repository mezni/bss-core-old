import tomllib

import ecommerce


def test_package_import():
    """Assert that ecommerce imports successfully."""
    import sys

    assert "ecommerce" in sys.modules


def test_package_version():
    """Assert that ecommerce.__version__ matches pyproject.toml version."""
    with open("pyproject.toml", "rb") as f:
        metadata = tomllib.load(f)
    version = metadata["project"]["version"]
    assert ecommerce.__version__ == version
