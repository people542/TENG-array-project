# Experiment Artifacts Index

> Last updated: 2026-05-19

This file maps generated artifacts to their intended paper/report usage. Generated data, result CSVs, checkpoints, and figures are intentionally ignored by Git; this index records the expected local artifact paths.

## 1. Simulation Sanity Checks

| Artifact | Purpose | Suggested paper location |
|---|---|---|
| `figures/generated/paper/simulation_sanity.png` | Shows material waveform differences, pressure saturation, spatial localization, and radius-dependent activation spread. | Method validation / first experiment figure |
| `figures/generated/demo_material_waveforms.png` | Separate material waveform demo. | Supplement or debugging |
| `figures/generated/demo_force_waveforms.png` | Separate pressure waveform demo. | Supplement or debugging |
| `figures/generated/demo_peak_heatmaps.png` | Separate position heatmap demo. | Supplement or debugging |
| `figures/generated/paper/model_architecture.png` | Spatial-temporal multi-task network architecture diagram. | Method / model architecture figure |

## 2. Dataset Artifacts

| Artifact | Purpose | Status |
|---|---|---|
| `data/datasets/v1/` | Initial train/val/random-test dataset. | Complete |
| `data/datasets/v2_augmented/` | Augmented training distribution covering high force, small/large radius, edge contacts, and hard combined samples. Recommended for main model training. | Complete |
| `data/generalization/v1/` | Fixed out-of-distribution evaluation splits. | Complete |
| `data/robustness/v1/` | Fixed robustness evaluation splits for SNR, faults, drift, and crosstalk. | Complete |
| `data/demo_samples/demo_samples.npz` | Small visualization/demo sample bundle. | Complete |

## 3. Model Checkpoints

| Checkpoint | Role | Recommendation |
|---|---|---|
| `checkpoints/torch_multitask_best.pt` | v1 baseline PyTorch model trained on v1 dataset. | Historical baseline only |
| `checkpoints/torch_multitask_v2_augmented.pt` | v2 model trained on augmented distribution. | Recommended default main model |
| `checkpoints/torch_multitask_v3_high_force.pt` | v3 high-force weighted model. | High-pressure specialist |
| `checkpoints/torch_multitask_v4_force_dim.pt` | v4 force-dimension weighted model. | Balanced robust candidate |
| `checkpoints/torch_multitask_v5_grid_selected.pt` | v5 selected from short grid-search smoke run. | Search record, not final recommendation |
| `checkpoints/ablation_structural/full.pt` | Full spatial-temporal architecture trained in structural ablation. | Confirms main architecture |
| `checkpoints/ablation_structural/no_temporal.pt` | Ablation without temporal branch. | Use for architecture justification |
| `checkpoints/ablation_structural/no_spatial.pt` | Ablation without spatial branch. | Use for architecture justification |

## 4. Result Tables

| Artifact | Purpose |
|---|---|
| `results/paper_tables.md` | Paper-ready Markdown tables for default, generalization, v2 robustness, and structural ablation results. |
| `results/paper_tables.tex` | Paper-ready LaTeX tables for default, selected generalization, v2 robustness, and structural ablation results. |
| `results/generalization_model_comparison_v1_v5.csv` | Long-form v1-v5 generalization comparison. |
| `results/generalization_v1.csv` | v1 generalization results. |
| `results/generalization_v2_augmented.csv` | v2 generalization results. |
| `results/generalization_v3_high_force.csv` | v3 generalization results. |
| `results/generalization_v4_force_dim.csv` | v4 generalization results. |
| `results/generalization_v5_grid_selected.csv` | v5 generalization results. |
| `results/robustness_v1.csv` | v1 robustness results, retained as historical baseline. |
| `results/robustness_v2_augmented.csv` | v2 robustness results. Use this for the main paper table. |
| `results/robustness_v1_vs_v2.csv` | v1/v2 robustness comparison. |
| `results/ablation_structural_v1.csv` | Structural ablation results for full/no-temporal/no-spatial variants. |
| `results/force_weight_grid_smoke.csv` | Short force-weight grid-search record. |

## 5. Figures

| Artifact | Purpose |
|---|---|
| `figures/generated/robustness_v2/*.png` | Main robustness curves for v2 under SNR, faults, drift, and crosstalk. |
| `figures/generated/robustness/*.png` | Historical v1 robustness curves. |
| `figures/generated/model_comparison/*.png` | v1-v5 comparison figures for each generalization split. |
| `figures/generated/ablation/structural_ablation.png` | Structural ablation figure for architecture justification. |
| `figures/generated/paper/model_architecture.png` | Paper-ready diagram of the spatial branch, temporal branch, shared MLP, and output heads. |

## 6. Current Recommended Narrative

1. Use `simulation_sanity.png` first to establish that the generator follows expected TENG trends.
2. Treat v1 as the initial baseline trained on default data.
3. Use v2 augmented as the main model because it improves default force/radius performance and generalization without requiring specialist weighting.
4. Report v3 as a targeted high-pressure specialist because it gives the best high-force and combined-hard force MAE but hurts ordinary random-test performance.
5. Report v4 as a balanced robust candidate, especially when high-force performance matters but v3's default-test degradation is undesirable.
6. Keep v5 as a search record. It shows that short grid-search candidates must be revalidated after full training.
7. Use structural ablation to justify the spatial-temporal dual-branch model: removing the temporal branch hurts material recognition; removing the spatial branch severely hurts position and radius estimation.

## 7. Completion Status

The simulation experiment suite is complete enough for a thesis/paper draft:

| Experiment family | Status | Main artifact |
|---|---|---|
| Physics sanity visualization | Complete | `figures/generated/paper/simulation_sanity.png` |
| Default train/val/test evaluation | Complete | `results/paper_tables.md` |
| Classical baseline and PyTorch model | Complete | `results/torch_multitask_metrics.json` |
| Augmented-data main model | Complete | `checkpoints/torch_multitask_v2_augmented.pt` |
| Generalization evaluation | Complete | `results/generalization_model_comparison_v1_v5.csv` |
| Robustness evaluation | Complete for v2 main model | `results/robustness_v2_augmented.csv` |
| Hyperparameter/search record | Complete as smoke search | `results/force_weight_grid_smoke.csv` |
| Structural ablation | Complete | `results/ablation_structural_v1.csv` |
| Paper tables | Complete | `results/paper_tables.md` |

## 8. Remaining Non-Experiment Work

1. Write the method and experiment sections using the selected v2/v3/v4 narrative.
2. Discuss limitations: material recognition is moderate, high-pressure absolute force estimation is still difficult, and radius estimation degrades under low SNR and strong drift.
