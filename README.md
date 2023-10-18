# SpatialEval

## Task 1. Draw some points in 2d grid

1. Synthesize data
```
python scripts/2d_grid.py <n_samples> <points_in_a_grid> <grid_size>
```
The data will be saved in `data/2d_grid_samples<n_samples>_points<points_in_a_grid>_size<grid_size>.json`.

2. Evaluate and save results
```
python eval_2d_grid.py <file_path>
```
We can get an accuracy after the evaluation.