"""Material and default array parameters for TENG tactile simulation.

The ranges in this module are literature-guided assumptions for simulation
pre-research. They are not experimentally calibrated parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


Range = tuple[float, float]


@dataclass(frozen=True)
class MaterialConfig:
    """Parameter ranges for one TENG material pair."""

    key: str
    label: str
    material_a: str
    electrode: str
    sigma_range_uc_m2: Range
    tau_range_s: Range
    alpha_range_n: Range
    epsilon_r_range: Range
    description: str

    def midpoint(self) -> dict[str, float | str]:
        """Return deterministic midpoint values for smoke tests and demos."""
        return {
            "key": self.key,
            "label": self.label,
            "sigma_uc_m2": midpoint(self.sigma_range_uc_m2),
            "tau_s": midpoint(self.tau_range_s),
            "alpha_n": midpoint(self.alpha_range_n),
            "epsilon_r": midpoint(self.epsilon_r_range),
        }


@dataclass(frozen=True)
class ArrayConfig:
    """Default geometric and acquisition settings for the simulated array."""

    array_shape: tuple[int, int] = (8, 8)
    spacing_mm: float = 5.0
    sample_rate_hz: int = 200
    duration_s: float = 1.0
    force_range_n: Range = (1.0, 20.0)
    radius_range_mm: Range = (3.0, 12.0)
    contact_frequency_range_hz: Range = (1.0, 3.0)
    snr_range_db: Range = (30.0, 50.0)
    gain_variation: float = 0.20
    crosstalk_range: Range = (0.0, 0.15)
    fault_ratio_range: Range = (0.0, 0.15)

    @property
    def channel_count(self) -> int:
        """Number of sensing channels in the array."""
        return self.array_shape[0] * self.array_shape[1]

    @property
    def sample_count(self) -> int:
        """Number of time samples per generated waveform."""
        return int(round(self.sample_rate_hz * self.duration_s))

    @property
    def coordinate_range_mm(self) -> tuple[Range, Range]:
        """Inclusive x/y coordinate ranges for array cell centers."""
        rows, cols = self.array_shape
        return (
            (0.0, (cols - 1) * self.spacing_mm),
            (0.0, (rows - 1) * self.spacing_mm),
        )


DEFAULT_ARRAY_CONFIG = ArrayConfig()


MATERIAL_CONFIGS: dict[str, MaterialConfig] = {
    "ptfe_al": MaterialConfig(
        key="ptfe_al",
        label="PTFE/Al",
        material_a="PTFE",
        electrode="Al",
        sigma_range_uc_m2=(70.0, 140.0),
        tau_range_s=(0.8, 1.8),
        alpha_range_n=(6.0, 10.0),
        epsilon_r_range=(2.0, 2.2),
        description="High-output negative triboelectric material pair.",
    ),
    "pdms_al": MaterialConfig(
        key="pdms_al",
        label="PDMS/Al",
        material_a="PDMS",
        electrode="Al",
        sigma_range_uc_m2=(60.0, 130.0),
        tau_range_s=(0.5, 1.4),
        alpha_range_n=(7.0, 12.0),
        epsilon_r_range=(2.5, 3.2),
        description="Flexible material with smoother pressure response.",
    ),
    "kapton_al": MaterialConfig(
        key="kapton_al",
        label="Kapton/Al",
        material_a="Kapton",
        electrode="Al",
        sigma_range_uc_m2=(50.0, 120.0),
        tau_range_s=(0.8, 2.0),
        alpha_range_n=(8.0, 13.0),
        epsilon_r_range=(3.1, 3.6),
        description="Stable polyimide film material pair.",
    ),
    "nylon_cu": MaterialConfig(
        key="nylon_cu",
        label="Nylon/Cu",
        material_a="Nylon",
        electrode="Cu",
        sigma_range_uc_m2=(35.0, 100.0),
        tau_range_s=(0.6, 1.5),
        alpha_range_n=(5.0, 9.0),
        epsilon_r_range=(3.0, 4.0),
        description="Medium-to-high output pair with wider assumed variability.",
    ),
    "paper_cu": MaterialConfig(
        key="paper_cu",
        label="Paper/Cu",
        material_a="Paper",
        electrode="Cu",
        sigma_range_uc_m2=(20.0, 60.0),
        tau_range_s=(0.3, 1.0),
        alpha_range_n=(4.0, 8.0),
        epsilon_r_range=(2.0, 3.5),
        description="Low-cost, lower-output pair with stronger humidity sensitivity.",
    ),
    "leather_ag": MaterialConfig(
        key="leather_ag",
        label="Leather/Ag",
        material_a="Leather",
        electrode="Ag",
        sigma_range_uc_m2=(25.0, 70.0),
        tau_range_s=(0.4, 1.2),
        alpha_range_n=(6.0, 11.0),
        epsilon_r_range=(2.5, 4.0),
        description="Touch-scenario material pair with moderate assumed output.",
    ),
}


def midpoint(value_range: Range) -> float:
    """Return the midpoint of a numeric range."""
    low, high = value_range
    return (low + high) / 2.0


def material_keys() -> list[str]:
    """Return material keys in stable class-index order."""
    return list(MATERIAL_CONFIGS)


def material_labels() -> list[str]:
    """Return display labels in stable class-index order."""
    return [config.label for config in MATERIAL_CONFIGS.values()]


def material_index_map() -> dict[str, int]:
    """Return key-to-class-index mapping used by generated datasets."""
    return {key: index for index, key in enumerate(material_keys())}


def get_material_config(key: str) -> MaterialConfig:
    """Return the material config for a key.

    Raises:
        KeyError: If the material key is unknown.
    """
    try:
        return MATERIAL_CONFIGS[key]
    except KeyError as exc:
        valid = ", ".join(material_keys())
        raise KeyError(f"Unknown material key {key!r}. Valid keys: {valid}") from exc


def validate_range(name: str, value_range: Range) -> None:
    """Validate that a range is finite, positive, and increasing."""
    low, high = value_range
    if low <= 0 or high <= 0:
        raise ValueError(f"{name} must be positive, got {value_range!r}")
    if low >= high:
        raise ValueError(f"{name} must be increasing, got {value_range!r}")


def validate_material_configs(
    configs: Mapping[str, MaterialConfig] = MATERIAL_CONFIGS,
) -> None:
    """Validate all configured material ranges."""
    if not configs:
        raise ValueError("At least one material config is required.")

    for key, config in configs.items():
        if key != config.key:
            raise ValueError(f"Material dict key {key!r} does not match config key {config.key!r}")
        validate_range(f"{key}.sigma_range_uc_m2", config.sigma_range_uc_m2)
        validate_range(f"{key}.tau_range_s", config.tau_range_s)
        validate_range(f"{key}.alpha_range_n", config.alpha_range_n)
        validate_range(f"{key}.epsilon_r_range", config.epsilon_r_range)

