# Measurements

When running `python ./harness/run_submission.py <size>`, it will generate measurement files in a sub-directory under this directory.
Specifically, the sub-directories that it uses are `toy`, `small`, `medium` and `large`, one per instance size, for runs of the maximum mini-workload (`--mini_workload 0`, the default), and `ip_toy`, `ip_small`, `ip_medium` and `ip_large` for runs of the inner-product mini-workload (`--mini_workload 1`).
If it is run with argument `--num_runs <n>` it will generate `<n>` measurement files called `results-1.json`, ..., `results-<n>.json`, all in the same sub-directory.

Before submitting your implementation, run the `run_submission.py` script with argument `--num_runs 3` for each instance size and each mini-workload you want to submit. Then commit all these results files to your fork, the average of these three runs will be the numbers reported for your submission.

## Results for the reference implementation

The sub-directories `toy` and `small` contain the results of the reference implementation
(three runs each, with the maximum mini-workload), generated in July 2026. The reference
implementation supports the toy, small and medium instance sizes.