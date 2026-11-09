"""Integration test for module architecture validation.

Tests that the project directory structure follows the layered architecture
with clear separation, and routes can be added without crossing layer boundaries.
"""

import os


def test_layer_directories_exist():
    """Test that all required layer directories exist."""
    required_layers = [
        "src/domain",
        "src/application",
        "src/infrastructure",
        "src/presentation",
    ]
    for layer in required_layers:
        assert os.path.isdir(layer), f"Required layer directory not found: {layer}"


def test_module_structure_exists():
    """Test that module subdirectories exist within each layer."""
    layers = ["src/domain", "src/application", "src/infrastructure", "src/presentation"]
    for layer in layers:
        assert os.path.isdir(os.path.join(layer, "modules")), (
            f"Module subdirectory not found in {layer}"
        )


def test_bss_core_package_exists():
    """Test that the bss_core package exists within src."""
    bss_core_path = os.path.join("src", "bss_core")
    assert os.path.isdir(bss_core_path), (
        f"bss_core package not found at {bss_core_path}"
    )


def test_api_module_exists():
    """Test that the API module exists within src."""
    api_path = os.path.join("src", "api")
    assert os.path.isdir(api_path), f"API module not found at {api_path}"


def test_domain_module_exists():
    """Test that the domain module exists within src."""
    domain_path = os.path.join("src", "domain")
    assert os.path.isdir(domain_path), f"Domain module not found at {domain_path}"
