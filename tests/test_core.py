import numpy as np
import pytest
from sklearn.metrics import average_precision_score
from opcal import calibrate,fpr_report,pooling_report,grouped_ap_bootstrap,source_diagnostics

def test_disjoint_calibration_units_and_reject_pixels():
    score=np.ones((2,3,3))
    with pytest.raises(ValueError):calibrate(score,independent_unit='pixel',calibration_ids=['a','b'],evaluation_ids=['x'])
    with pytest.raises(ValueError):calibrate(score,independent_unit='object',calibration_ids=['a','b'],evaluation_ids=['a'])
    r=calibrate(score,independent_unit='object',calibration_ids=['a','a'],evaluation_ids=['x'])
    assert r['calibration_units']==1 and r['threshold']==1
    with pytest.raises(ValueError):calibrate(score,independent_unit='image',calibration_ids=['a','a'],evaluation_ids=['x'])

def test_fpr_denominators_and_recall_are_different():
    scores=np.array([[[2,0]],[[2,2]]],float);m=np.array([[[0,0]],[[1,0]]])
    r=fpr_report(scores,m,[True,False],1)
    assert r['normal_image_pixel_FPR']['rate']==.5
    assert r['all_negative_pixel_FPR']['rate']==pytest.approx(2/3)
    assert r['defect_pixel_recall']['rate']==1
    with pytest.raises(ValueError):fpr_report(scores,m,[True,True],1)

def test_exact_tie_AP_and_additive_histogram_counts():
    rng=np.random.default_rng(3);s=rng.integers(0,7,(4,9,9));y=rng.random(s.shape)<.2
    r=pooling_report(s,y,np.arange(-.5,7.5))
    assert r['additive_count_max_error']==0
    assert r['exact_pooled_AP']==pytest.approx(average_precision_score(y.ravel(),s.ravel()))
    assert r['AP_approximation_error_pp']==pytest.approx(0,abs=1e-12)

def test_group_bootstrap_preserves_repeated_objects_and_negative_control():
    s=np.arange(16).reshape(4,2,2)/16;y=np.zeros(s.shape,bool);y[2:,0,0]=1
    r=grouped_ap_bootstrap(s,s,y,independent_unit='object',object_ids=['a','a','b','b'],edges=np.linspace(0,1,33),repeats=30,seed=4)
    assert r['groups']==2 and r['images']==4 and r['binned_CI95_pp']==[0,0]
    with pytest.raises(ValueError):grouped_ap_bootstrap(s,s,y,independent_unit='image',object_ids=['a','a','b','b'],edges=np.linspace(0,1,33))
    with pytest.raises(ValueError):grouped_ap_bootstrap(s,s,y,independent_unit='object',edges=np.linspace(0,1,33))

def test_bootstrap_matches_exact_group_enumeration_distribution():
    # Fine bins give exact AP; 2 normal and 2 defect groups make sampling nontrivial.
    s=np.array([.1,.6,.4,.9]).reshape(4,1,1);b=1-s;y=np.array([0,0,1,1]).reshape(4,1,1)
    r=grouped_ap_bootstrap(s,b,y,independent_unit='object',object_ids=['a','b','c','d'],edges=np.linspace(0,1,101),repeats=40,seed=12)
    rng=np.random.default_rng(12);delta=[]
    for i in range(40):
        ix=np.r_[rng.choice([0,1],2,replace=True),rng.choice([2,3],2,replace=True)]
        delta.append((average_precision_score(y[ix].ravel(),s[ix].ravel())-average_precision_score(y[ix].ravel(),b[ix].ravel()))*100)
    assert r['binned_CI95_pp']==pytest.approx(np.quantile(delta,[.025,.975]))

def test_centered_source_diagnostics_not_target_error():
    a=np.full((3,10),.03);b=np.full((3,10),.01)
    r=source_diagnostics(a,b)
    assert r['V1_source_centered_p90_pp']==[0,0,0]
    assert r['V2_signed_paired_median_pp']==pytest.approx(2)
    assert r['zero_wave_scale'] and r['G1_descriptive']

def test_empty_class_and_bad_edges_are_explicit():
    s=np.zeros((1,2,2));r=pooling_report(s,s,[-1,0,1])
    assert r['exact_pooled_AP'] is None
    with pytest.raises(ValueError):pooling_report(s,s,[0,0,1])
