# Experiment Artifacts Index

> Last updated: 2026-05-17

This file maps generated artifacts to their intended paper/report usage.

## 1. Simulation Sanity Checks

| Artifact | Purpose | Suggested paper location |
|---|---|---|
| `figures/generated/paper/simulation_sanity.png` | Shows material waveform differences, pressure saturation, spatial localization, and radius-dependent activation spread. | Method validation / first experiment figure |
| `figures/generated/demo_material_waveforms.png` | Separate material waveform demo. | Supplement or debugging |
| `figures/generated/demo_force_waveforms.png` | Separate pressure waveform demo. | Supplement or debugging |
| `figures/generated/demo_peak_heatmaps.png` | Separate position heatmap demo. | Supplement or debugging |

## 2. Dataset Artifacts

| Artifact | Purpose |
|---|---|
| `data/datasets/v1/` | Initial 600/120/120 dataset. |
| `data/datasets/v2_augmented/` | Augmented training distribution covering high force, small/large radius, edge contacts, and hard combined samples. Recommended for current main model training. |
| `data/generalization/v1/` | Fixed out-of-distribution evaluation splits. |
| `data/robustness/v1/` | Fixed robustness evaluation splits for SNR, faults, drift, and crosstalk. |

## 3. Model Checkpoints

| Checkpoint | Role | Recommendation |
|---|---|---|
| `checkpoints/torch_multitask_best.pt` | v1 baseline PyTorch model trained on v1 dataset. | Historical baseline only. |
| `checkpoints/torch_multitask_v2_augmented.pt` | v2 model trained on augmented distribution. | Recommended default main model. |
| `checkpoints/torch_multitask_v3_high_force.pt` | v3 high-force weighted model. | Use as high-pressure robust variant. |
| `checkpoints/torch_multitask_v4_force_dim.pt` | v4 force-dimension weighted model. | Use as balanced robust variant. |
| `checkpoints/torch_multitask_v5_grid_selected.pt` | v5 selected from short grid-search smoke run. | Keep as search record, not recommended as final model. |

## 4. Result Tables

| Artifact | Purpose |
|---|---|
| `results/paper_tables.md` | Paper-ready Markdown tables for default, generalization, and robustness results. |
| `results/generalization_model_comparison_v1_v5.csv` | Long-form v1-v5 generalization comparison. |
| `results/generalization_v1.csv` | v1 generalization results. |
| `results/generalization_v2_augmented.csv` | v2 generalization results. |
| `results/generalization_v3_high_force.csv` | v3 generalization results. |
| `results/generalization_v4_force_dim.csv` | v4 generalization results. |
| `results/generalization_v5_grid_selected.csv` | v5 generalization results. |
| `results/robustness_v1.csv` | v1 robustness results. |

## 5. Figures

| Artifact | Purpose |
|---|---|
| `figures/generated/robustness/*.png` | Robustness curves for SNR, faults, drift, and crosstalk. |
| `figures/generated/model_comparison/*.png` | v1-v5 comparison figures for each generalization split. |

## 6. Current Recommended Narrative

1. First show `simulation_sanity.png` to establish that the generator follows expected TENG trends.
2. Use v1 as the initial baseline trained on default data.
3. Show that v2 augmented training improves generalization on large-radius and combined hard splits without damaging default force/radius performance.
4. Report v3 as a targeted high-pressure robust variant because it reduces high-force MAE but hurts default-test performance.
5. Report v4 as a balanced robust variant.
6. Mention v5 as evidence that short grid-search candidates must be revalidated with full training.

## 7. Known Gaps

1. Robustness curves currently use the v1 checkpoint. If v2 becomes the main model, regenerate robustness results for v2 and update `results/paper_tables.md`.
2. Material recognition remains moderate. If the paper emphasizes material classification, improve material separability or temporal modeling.
3. High-pressure absolute force estimation remains difficult due to pressure saturation. This should be discussed as a limitation.

