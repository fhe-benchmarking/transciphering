# Reference submission: AES transciphering with TFHE

This directory contains the reference implementation of the AES-transciphering workload. It
implements the FFT-based circuit-bootstrapping AES evaluation of

> Ruida Wang, Jincheol Ha, Xuan Shen, Xianhui Lu, Chunling Chen, Kunpeng Wang, and Jooyoung
> Lee, *"Refined TFHE Leveled Homomorphic Evaluation and Its Application"*, ACM CCS 2025.
> [ePrint 2024/1318](https://eprint.iacr.org/2024/1318)

The implementation is written in Rust against the `core_crypto` API of
[tfhe-rs](https://github.com/zama-ai/tfhe-rs) v0.5.3. The bundled `auto-base-conv` crate
(under [`cbs_lib/`](cbs_lib/)) provides the paper's refined (WWL+-style) circuit bootstrapping
with automorphism-based base conversion and the split-FFT technique.

## Approach

- The client generates the FHE key material (`client_key_generation`) and encrypts the 128-bit
  AES key under it as transciphering key material (`client_encode_encrypt`) — following the
  paper, GLWE encryptions of keyed S-box tables derived from the AES round keys, which
  integrate the AddRoundKey and SubBytes steps. This material is uploaded to the server
  together with the public evaluation keys.
- The server homomorphically evaluates the AES-128 decryption circuit over the AES-encrypted
  dataset (`server_encrypted_aes_decryption`), producing LWE ciphertexts that encrypt the bits
  of the plaintext dataset — the transciphering step.
- The server evaluates the mini-workload (`server_encrypted_compute`): the maximum of the
  dataset values, computed as a tournament of pairwise homomorphic comparisons over the
  transciphered bits.
- The client decrypts and decodes the transciphered dataset and the mini-workload result
  (`client_decrypt_decode_aes_decryption`, `client_decrypt_decode`) and reconstitutes the
  16-bit integer outputs (`client_postprocess_aes_decryption`, `client_postprocess`).

## Cryptographic parameters and security

All stages use the parameter set `AES_SET_2` defined in
[`cbs_lib/src/aes_instances.rs`](cbs_lib/src/aes_instances.rs): TFHE (CGGI-style) ciphertexts
over the native 64-bit modulus (q = 2^64), with binary secret keys and Gaussian noise.

| Parameter | Value |
|-----------|-------|
| LWE dimension n | 768 |
| LWE noise σ/q | 7.02 × 10^-6 (≈ 2^-17.1) |
| GLWE dimension k / polynomial size N | 2 / 1024 (total dimension k·N = 2048) |
| GLWE noise σ/q | 2.94 × 10^-16 (≈ 2^-51.6) |
| Ciphertext modulus q | 2^64 (native) |

These dimension/noise combinations target 128-bit classical security:

- The dimensions are those of the recommended AES parameter sets of ePrint 2024/1318
  (Appendix A, Table 11), whose noise levels were chosen with the lattice estimator to give
  128-bit security with a small margin (130.1 bits at LWE dimension 768, 130.7 bits at
  dimension 2048).
- The noise values instantiated here are those of the 128-bit-secure parameter sets shipped
  with tfhe-rs v0.5 (slightly smaller than the paper's Table 11 values): the GLWE combination
  (total dimension 2048, σ/q ≈ 2^-51.6) is exactly the tfhe-rs value for dimension-2048 GLWE
  keys (there instantiated as k = 1, N = 2048; the security of GLWE with binary secrets
  reduces to that of LWE of dimension k·N), and the LWE combination (n = 768, σ/q ≈ 2^-17.1)
  is slightly more conservative in dimension than the tfhe-rs 128-bit sets (n = 742 at
  σ/q ≈ 2^-17.1).

Submissions that modify these parameters (or use different ones) should re-validate the
security level, e.g. with the [lattice estimator](https://github.com/malb/lattice-estimator),
and document the result here.

The symmetric side of the transciphering is standard AES-128, as specified by the harness.

## Scope

- Supported instance sizes: toy (0), small (1) and medium (2). The large instance (3) is
  defined by the harness but is not supported by this reference implementation.
- Implemented mini-workload: the maximum (`--mini_workload 0`). The inner product
  (`--mini_workload 1`) is not implemented, so running the harness with it fails the final
  verification step.

## Layout

- `src/bin/` — one binary per benchmark stage (`client_*` / `server_*`), invoked by the
  harness with the instance size as argument.
- `src/` — shared helpers (I/O paths, AES reference, data structures).
- `cbs_lib/` — the `auto-base-conv` crate implementing the circuit-bootstrapping machinery
  used for the homomorphic AES evaluation.
- `Cargo.toml` — package manifest; the harness builds everything with `cargo build --release`
  via `scripts/build_task.sh`.
