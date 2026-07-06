# Measurements

When running `python ./harness/run_submission.py <size>`, it will generate measurement files in a sub-directory under this directory.
Specifically, the sub-directories that it uses are `toy`, `small`, `medium` and `large`, one per instance size.
If it is run with argument `--num_runs <n>` it will generate `<n>` measurement files called `results-1.json`, ..., `results-<n>.json`, all in the same sub-directory.

Before submitting your implementation, run the `run_submission.py` script with argument `--num_runs 3` for each instance size (and each mini-workload you want to submit, selected with `--mini_workload`: `0` for the maximum, `1` for the inner product). Then commit all these results files to your fork, the average of these three runs will be the numbers reported for your submission.

## Results for the reference implementation