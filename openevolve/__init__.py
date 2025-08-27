"""
OpenEvolve: An open-source implementation of AlphaEvolve
"""

from openevolve._version import __version__
from openevolve.controller import OpenEvolve
from openevolve.evolution import run_evolution

__all__ = ["OpenEvolve", "__version__", "run_evolution"]
