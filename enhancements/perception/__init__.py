"""
Perception Module for UFO Galaxy Realization.

This module provides environment perception capabilities including
desktop tool discovery and system environment scanning.
"""

from .environment_scanner import (
    EnvironmentScanner,
    ToolInfo,
    ToolCategory,
    ScanResult,
    scan_environment
)

__all__ = [
    "EnvironmentScanner",
    "ToolInfo",
    "ToolCategory",
    "ScanResult",
    "scan_environment"
]
