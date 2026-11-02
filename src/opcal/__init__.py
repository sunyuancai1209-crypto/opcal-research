"""Descriptive evaluation utilities. No conformal or causal guarantee is claimed."""
from .core import calibrate, fpr_report, pooling_report, grouped_ap_bootstrap, source_diagnostics
__version__='0.1.2'
__all__=['calibrate','fpr_report','pooling_report','grouped_ap_bootstrap','source_diagnostics']
