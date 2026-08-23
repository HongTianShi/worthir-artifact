# MuSiQue post-gate cost sensitivity

This is a frozen-action sensitivity, not a refit or a second preregistered gate. The official-validation `A_dev` action vector is unchanged; only the declared preference weight and corresponding fixed references are rescored.

| lambda | F_dev | delta raw | delta cost | delta utility (95% CI) | kappa |
|---:|---|---:|---:|---:|---:|
| 0.00 | V2 | 0.004946 | -0.112795 | 0.004946 [-0.002601, 0.012403] | 4.26% |
| 0.02 | V2 | 0.004946 | -0.112795 | 0.007202 [-0.000356, 0.014633] | 6.11% |
| 0.04 | V2 | 0.004946 | -0.112795 | 0.009458 [0.001919, 0.016919] | 7.90% |
| 0.08 | V2 | 0.004946 | -0.112795 | 0.013970 [0.006425, 0.021461] | 11.29% |
| 0.16 | V2 | 0.004946 | -0.112795 | 0.022994 [0.015405, 0.030550] | 17.30% |
| 0.32 | V0 | 0.048909 | 0.164702 | -0.003796 [-0.013326, 0.005628] | -3.42% |

The analysis tests whether the held-out conclusion is tied to the single headline weight. It does not claim policy transfer because the action vector was development-selected at lambda=.08.
