# AES Transciphering FHE Benchmark

## Cloning the workload

```console
git clone https://github.com/code-perspective/temp-fhe-transciphering
cd temp-fhe-transciphering
```

## Dependencies

The harness is written in Python and requires a few packages listed in `requirements.txt`.
```console
python3 -m venv virtualenv
source ./virtualenv/bin/activate
pip3 install -r requirements.txt
```

In this template, the submission (the encrypted computation) is written in Rust and uses 
the [tfhe-rs](https://github.com/zama-ai/tfhe-rs) library (v0.5.3) together with the
local `auto-base-conv` crate under `submission/cbs_lib`.

Building requires a Rust toolchain (`cargo`/`rustc`). You do not need to install it manually: 
[`scripts/build_task.sh`](scripts/build_task.sh) installs the Rust toolchain via `rustup` 
if it is not already present, and then builds the submission with `cargo build --release`. 
The harness invokes this script automatically, so the first run may take a while as the 
dependencies are compiled.

## Running the "AES transciphering" workload

The goal of this workload is to homomorphically transcipher a number of AES blocks into FHE 
ciphertexts encrypting the same plaintexts. We assess the "quality" of the resulting FHE 
ciphertexts by evaluating two mini-workloads after the transciphering: 1. Computing the 
maximum between the input message parsed as 16-bit unsigned integers; and 2. Computing the 
inner product modulo 2^16 of the first half of the input message parsed as 16-bit unsigned 
integers and the second half.

The mini-workload is selected with `--mini_workload` (`0` for the maximum, `1`
for the inner product). An example run is provided below.

```console
$ python3 harness/run_submission.py -h
usage: run_submission.py [-h] [--num_runs NUM_RUNS] [--seed SEED]
                         [--mini_workload MINI_WORKLOAD]
                         {0,1,2,3}

Run the AES-transciphering FHE benchmark.

positional arguments:
  {0,1,2,3}             Instance size (0-toy/1-small/2-medium/3-large)

options:
  -h, --help            show this help message and exit
  --num_runs NUM_RUNS   Number of times to run steps 4-9 (default: 1)
  --seed SEED           Random seed for dataset generation
  --mini_workload MINI_WORKLOAD
                        Specify 0 for mini workload = max and 1 for mini
                        workload = dot product.

$ python3 ./harness/run_submission.py 1 --seed 3 --num_runs 2 --mini_workload 0

[...]

All steps completed for the medium dataset!
```

After finishing the run, deactivate the virtual environment.
```console
deactivate
```

## Directory structure

```bash
Each submission to the workload in the FHE benchmarking should have the following directory structure:
[root] /
| ├─datasets/       # Holds cleartext data (plaintext db, AES key/IV, AES-encrypted db, expected outputs)
| |  ├─ toy/        # each instance-size in a separate subdirectory
| |  ├─ small/
| |  ├─ medium/
| |  ├─ large/
| ├─docs/           # Documentation (beyond the top-level README.md)
| ├─harness/        # Scripts to generate data, run workload, check results
| ├─scripts/        # Handle installing dependencies and building the project (build_task.sh)
| ├─submission/     # The implementation, this is what the submitters modify
| |  ├─ cbs_lib/    # The `auto-base-conv` Rust crate used by the submission
| |  ├─ src/        # Rust sources for the client_*/server_* executables
| |  └─ Cargo.toml  # Rust package manifest
| ├─io/             # Directory to hold the I/O between client & server parts
| |  ├─ toy/        # The reference implementation has subdirectories
| |     ├─ public_keys/             # holds the public evaluation keys
| |     ├─ secret_keys/             # holds the secret key(s)
| |     ├─ ciphertexts_upload/      # holds the ciphertexts (or other data except keys) to be uploaded by the client
| |     ├─ ciphertexts_download/    # holds the mini-workload ciphertexts to be downloaded by the client
| |     ├─ ciphertext_aes_download/ # holds the transciphered (AES-decrypted) ciphertexts to be downloaded by the client
| |     └─ intermediate/            # internal information to be passed around the functions
| |  ├─ small/
| |     …
| |  ├─ medium/
| |     …
| ├─measurements/   # Holds json files (results-<run>.json) with the results for each run
| |  ├─ toy/        # each instance-size in a separate subdirectory
| |  ├─ small/
| |  ├─ medium/
```

## Description of stages

A submitter can edit any of the `client_*` / `server_*` sources in `/submission`.
Moreover, for the particular parameters related to a workload, the submitter can modify the params files.
If the current description of the files are inaccurate, the stage names in `run_submission` can be also
modified.

The current stages are the following, targeted to a client-server scenario.
The order in which they happen in `run_submission` assumes an initialization phase which is
dataset-dependent and run only once, followed by the encrypted computation, which can be repeated
`--num_runs` times to average out run-to-run variability in the measured latency. (The computation is
deterministic, so the results are identical across runs; only the timings vary.)
Each executable takes the test-case size as its argument.


| Stage executables                     | Description |
|---------------------------------------|-------------|
| `client_preprocess`                   | Any in-the-clear computation the client wants to apply over the dataset before encryption.
| `client_key_generation`               | Generate all key material and cryptographic context at the client.
| `client_encode_encrypt`               | Plaintext encoding and encryption of the AES key at the client.
| `server_preprocess_dataset`           | (Optional) Any in-the-clear or encrypted computation the server applies over the AES-encrypted dataset.
| `server_encrypted_aes_decryption`     | Homomorphically decrypt the AES ciphertexts, producing FHE ciphertexts of the same plaintexts (the transciphering).
| `server_encrypted_compute`            | Evaluate the selected mini-workload (maximum or inner product) over the transciphered ciphertexts.
| `client_decrypt_decode_aes_decryption`| Decryption and plaintext decoding of the transciphered result at the client.
| `client_postprocess_aes_decryption`   | Any in-the-clear computation over the decrypted transciphering result (written to `result_aes.txt`).
| `client_decrypt_decode`               | Decryption and plaintext decoding of the mini-workload result at the client.
| `client_postprocess`                  | Any in-the-clear computation over the decrypted mini-workload result (written to `result.txt`).

The harness additionally runs the Python helpers `generate_dataset.py` (generate and AES-encrypt the
dataset), `cleartext_impl.py` (cleartext reference), and `verify_aes_decryption.py` / `verify_result.py`
(correctness oracles).

The outer python script measures the runtime of each stage.
The current stage separation structure requires reading and writing to files more times than minimally necessary.
For a more granular runtime measuring, which would account for the extra overhead described above, we encourage
submitters to separate and print in a log the individual times for reads/writes and computations inside each stage.
