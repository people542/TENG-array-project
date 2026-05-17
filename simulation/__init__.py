"""Simulation utilities for the TENG tactile array project."""

from simulation.material_params import (
    DEFAULT_ARRAY_CONFIG,
    MATERIAL_CONFIGS,
    ArrayConfig,
    MaterialConfig,
    get_material_config,
    material_index_map,
    material_keys,
    material_labels,
    validate_material_configs,
)

__all__ = [
    "ArrayConfig",
    "DEFAULT_ARRAY_CONFIG",
    "MATERIAL_CONFIGS",
    "MaterialConfig",
    "get_material_config",
    "material_index_map",
    "material_keys",
    "material_labels",
    "validate_material_configs",
]
