"""
Indus Valley Script Decipherment Package

This package provides tools for analyzing the Indus Valley script
and reproducing the revolutionary findings that it represents
humanity's first secular democracy.
"""

__version__ = "1.0.0"
__author__ = "RBT Research Team"
__description__ = "Computational decipherment of the Indus Valley script"

# Core functionality imports
from .validate import validate_data
from .analysis import load_translations, analyze_vocabulary
from .utils import pct

__all__ = [
    "validate_data",
    "load_translations", 
    "analyze_vocabulary",
    "pct"
] 