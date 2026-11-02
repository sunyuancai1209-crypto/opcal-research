# opcal-research

**Object-aware operating-point evaluation for anomaly score maps.**

opcal-research is a NumPy-based research tool for evaluating calibration thresholds, pixel false-positive rates, pooled average precision, and grouped resampling. It makes calibration/evaluation identities, sampling units, pixel denominators, and approximation errors explicit.

- Python 3.10+; NumPy is the only runtime dependency.
- License: MIT.
- Software creators: ZiKai Zhou and SunYuan Cai.
- Archived software version 0.1.2: [10.5281/zenodo.23878739](https://doi.org/10.5281/zenodo.23878739).

The DOI identifies the software release. Benchmark datasets, pretrained weights, and experimental score caches are not included in the archive.

## Install and run the example

From a clone or downloaded source directory:

```text
python -m venv .venv
# Activate the environment using your operating system's standard command.
python -m pip install .
python examples/ten_minute.py --output example_output
python -m opcal example_output/input.npz --output example_output/cli_report.json --unit object
```

The Python API and command-line reports use the same calibration threshold, pixel denominators, and pooled AP. The example also checks additive histogram counts. Its arrays are generated interface data, rather than benchmark results. The quick start does not run bootstrap experiments.

Use a new output directory for each example run. The CLI refuses to overwrite an existing report. This project has not been published on PyPI; install from the source directory.

Optional developer tests:

```text
python -m pip install ".[test]"
python -m pytest tests -q
```

## Inputs and Python API

```python
from opcal import (
    calibrate,
    fpr_report,
    pooling_report,
    grouped_ap_bootstrap,
    source_diagnostics,
)
```

Score maps have shape `N x H x W`. Supply separate normal calibration maps and evaluation maps, binary defect masks, normal-image flags, and genuine grouping identifiers. Keep calibration and evaluation identities disjoint.

### Calibration

`calibrate(normal_scores, independent_unit=..., calibration_ids=..., evaluation_ids=..., q=.99)`

Computes a pooled linear empirical quantile from normal calibration scores. It reports the threshold, image count, unique-unit count, and decision rule. Multiple maps of one object may share an identifier; the object count uses unique identifiers, while the quantile still pools scores from the supplied maps.

### Pixel operating point

`fpr_report(scores, masks, normal_images, threshold)`

Reports hit counts and denominators for:

- Pixel FPR over complete normal images.
- Pixel FPR over all non-defect pixels, including background pixels in anomalous images.
- Defect-pixel recall.

Decisions use the strict rule `score > threshold`. A zero denominator produces Python `None` (JSON `null`). Pixel FPR is distinct from image rejection rate.

### Pooled AP and approximation checks

`pooling_report(scores, masks, edges)`

Checks additive per-image histogram counts and reports exact pooled AP, binned pooled AP, approximation error, and counts clipped to the outer bins. Bin edges are caller-supplied; freeze them using calibration data, without selecting them against evaluation labels.

### Grouped comparison

`grouped_ap_bootstrap(scores_a, scores_b, masks, independent_unit=..., object_ids=..., edges=..., repeats=2000, seed=0)`

Returns the paired difference in pooled AP (A minus B) and a binned percentile interval. Resampling is stratified by normal/anomalous status. Maps sharing an object identifier are resampled together. The result is pooled AP rather than a macro-average of condition-level AP. Inspect the exact-versus-binned error when interpreting the approximate interval.

### Descriptive source diagnostics

`source_diagnostics(source_fpr, target_fpr)`

Accepts paired `reference x draw` FPR matrices and reports centered p90 fluctuation (V1), the median paired source contrast (V2), the range of reference medians (V3), and a descriptive G1 flag. The caller establishes pairing and source definitions. These outputs are not a causal or orthogonal variance decomposition. Treat zero-fluctuation full-pool endpoints separately.

## Command-line input

```text
python -m opcal input.npz --output report.json --unit object
```

The NPZ file must contain:

`calibration_scores`, `calibration_ids`, `scores`, `masks`, `normal_images`, and `object_ids`.

Use string identifiers with a non-object NumPy dtype. Score maps and masks must have compatible shapes; `normal_images` is a binary vector of length `N`. The caller declares calibration inputs to be normal. The tool checks interface consistency, not the correctness of image annotations.

## Interpretation and limits

- Declare the sampling unit as `object` or `image`; `pixel` is rejected. Object mode requires identifiers. Image mode rejects duplicate image identities in calibration.
- Identifiers do not establish physical independence or acquisition-batch independence. Different IDs alone are insufficient evidence of independent objects.
- Empirical q99 is not split conformal calibration with a finite-sample rank correction. Spatially correlated pixels do not provide an independent-sample coverage guarantee.
- Resampling intervals depend on the specified grouping and fixed score maps. They do not automatically correct distribution shift or establish generalization across categories.
- Repeated subsets of one fixed pool, including a zero-variability full-pool endpoint, do not establish a population sample-size lower bound.
- The package implements evaluation procedures; it does not include an anomaly detector or pretrained weights. A self-written implementation of standard statistical procedures is distinct from a claim of methodological novelty.

When reporting results, specify data versions, support/calibration/evaluation roles, grouping evidence, denominators, threshold inequality, bin edges, seeds, approximation errors, and outcomes that did not meet the stated criteria.

## Statistical reference

Tibshirani et al., *Conformal Prediction Under Covariate Shift*, NeurIPS 2019. [Official paper](https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html).

The numerical implementation and tests were written for this project. The statistical reference is acknowledged as prior work; the code does not reproduce an online anomaly-detector implementation.

## Cite the archived software

Zhou, Z., & Cai, S. (2026). *opcal-research: Object-aware operating-point evaluation for anomaly score maps* (Version 0.1.2) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23878739

For the archived release, use the version DOI above. The main branch may contain later documentation and metadata corrections.
