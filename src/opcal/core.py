"""Independently written standard numerical evaluation, not a new detector."""
import numpy as np

def _unit(unit):
    if unit not in ('image','object'):raise ValueError('independent_unit must be image or object; pixels are not independent units')

def _maps(scores,masks=None):
    s=np.asarray(scores,dtype=np.float64)
    if s.ndim!=3 or not s.size or not np.isfinite(s).all():raise ValueError('finite nonempty N x H x W scores required')
    if masks is None:return s
    y=np.asarray(masks)
    if y.shape!=s.shape or not np.isin(y,[0,1]).all():raise ValueError('aligned binary masks required')
    return s,y.astype(bool)

def calibrate(normal_scores,*,independent_unit,calibration_ids,evaluation_ids,q=.99):
    _unit(independent_unit);s=_maps(normal_scores)
    ids=np.asarray(calibration_ids).astype(str)
    if ids.shape!=(len(s),) or not len(evaluation_ids):raise ValueError('explicit calibration and evaluation identity lists required')
    if independent_unit=='image' and len(set(ids))!=len(ids):raise ValueError('repeated calibration identities require object grouping')
    if set(ids)&set(str(x) for x in evaluation_ids):raise ValueError('calibration and evaluation identities overlap')
    if not 0<q<1:raise ValueError('q must lie in (0,1)')
    return {'threshold':float(np.quantile(s,q,method='linear')),'q':q,'independent_unit':independent_unit,'calibration_images':len(s),'calibration_units':len(set(ids)),'rule':'strict >','guarantee':'empirical quantile only; no finite-sample conformal guarantee'}

def fpr_report(scores,masks,normal_images,threshold):
    s,y=_maps(scores,masks);flags=np.asarray(normal_images)
    if not np.isin(flags,[0,1]).all():raise ValueError('binary normal-image flags required')
    normal=flags.astype(bool)
    if normal.shape!=(len(s),) or np.any(y[normal]):raise ValueError('normal-image flags must align and normal masks must be empty')
    if not np.isfinite(threshold):raise ValueError('finite threshold required')
    hit=s>threshold;good=np.broadcast_to(normal[:,None,None],s.shape);negative=~y
    def rate(mask):
        n=int(mask.sum());k=int((hit&mask).sum())
        return {'numerator':k,'denominator':n,'rate':k/n if n else None}
    return {'normal_image_pixel_FPR':rate(good),'all_negative_pixel_FPR':rate(negative),'defect_pixel_recall':rate(y),'decision_rule':'score > threshold','note':'pixel FPR is not image rejection rate'}

def _ap(y,s):
    y=np.asarray(y,bool).ravel();s=np.asarray(s,float).ravel()
    if not y.any():return None
    order=np.argsort(-s,kind='stable');yy=y[order];ss=s[order]
    end=np.r_[np.flatnonzero(np.diff(ss)),len(ss)-1];tp=np.cumsum(yy)[end]
    return float(np.sum(np.diff(np.r_[0,tp/y.sum()])*tp/(end+1)))

def _hist(s,y,edges):
    e=np.asarray(edges,float)
    if e.ndim!=1 or len(e)<3 or not np.isfinite(e).all() or np.any(np.diff(e)<=0):raise ValueError('finite strictly increasing bin edges required')
    index=np.clip(np.searchsorted(e,s,side='right')-1,0,len(e)-2)
    p=np.stack([np.bincount(i[m],minlength=len(e)-1) for i,m in zip(index,y)])
    n=np.stack([np.bincount(i[~m],minlength=len(e)-1) for i,m in zip(index,y)])
    return p,n

def _hist_ap(p,n):
    tp=np.cumsum(p[...,::-1],axis=-1);fp=np.cumsum(n[...,::-1],axis=-1)
    total=tp[...,-1:];r=np.divide(tp,total,out=np.zeros_like(tp,dtype=float),where=total>0)
    precision=np.divide(tp,tp+fp,out=np.zeros_like(tp,dtype=float),where=(tp+fp)>0)
    return np.sum(np.diff(np.concatenate([np.zeros((*r.shape[:-1],1)),r],axis=-1),axis=-1)*precision,axis=-1)

def pooling_report(scores,masks,edges):
    s,y=_maps(scores,masks);p,n=_hist(s,y,edges);e=np.asarray(edges)
    pp,nn=_hist(s.reshape(1,-1),y.reshape(1,-1),edges)
    exact=_ap(y,s);approx=float(_hist_ap(p.sum(axis=0),n.sum(axis=0))) if y.any() else None
    return {'additive_count_max_error':int(max(np.max(np.abs(p.sum(axis=0)-pp[0])),np.max(np.abs(n.sum(axis=0)-nn[0])))),'exact_pooled_AP':exact,'binned_pooled_AP':approx,'AP_approximation_error_pp':(approx-exact)*100 if exact is not None else None,'clipped_pixels':int(((s<e[0])|(s>e[-1])).sum()),'bins':len(e)-1}

def grouped_ap_bootstrap(scores_a,scores_b,masks,*,independent_unit,object_ids=None,edges,repeats=2000,seed=0):
    _unit(independent_unit);a,y=_maps(scores_a,masks);b=_maps(scores_b)
    if a.shape!=b.shape or repeats<2:raise ValueError('aligned paired scores and repeats>=2 required')
    if independent_unit=='object' and object_ids is None:raise ValueError('object IDs required for object bootstrap')
    ids=np.asarray(object_ids if object_ids is not None else np.arange(len(a))).astype(str)
    if ids.shape!=(len(a),):raise ValueError('one group identity per image required')
    if independent_unit=='image' and len(set(ids))!=len(ids):raise ValueError('repeated identities require object grouping')
    keys,inverse=np.unique(ids,return_inverse=True);groups=[np.flatnonzero(inverse==i) for i in range(len(keys))]
    strata=[np.array([i for i,g in enumerate(groups) if bool(y[g].any())==flag],int) for flag in [False,True]]
    if any(not len(x) for x in strata):raise ValueError('both normal and defect-containing groups needed for stratified bootstrap')
    counts=[]
    for s in [a,b]:
        p,n=_hist(s,y,edges);counts.append((np.stack([p[g].sum(axis=0) for g in groups]),np.stack([n[g].sum(axis=0) for g in groups])))
    rng=np.random.default_rng(seed);w=np.zeros((repeats,len(groups)),int)
    for row in w:
        for stratum in strata:row+=np.bincount(rng.choice(stratum,len(stratum),replace=True),minlength=len(groups))
    values=[_hist_ap(w@p,w@n) for p,n in counts];delta=(values[0]-values[1])*100
    return {'exact_AP_difference_pp':(_ap(y,a)-_ap(y,b))*100,'binned_CI95_pp':np.quantile(delta,[.025,.975]).tolist(),'replicates':repeats,'groups':len(groups),'images':len(a),'independent_unit':independent_unit,'scope':'pooled AP, fixed scores, paired identity clusters; binned percentile approximation, no category generalization'}

def source_diagnostics(source_fpr,target_fpr):
    a=np.asarray(source_fpr,float);b=np.asarray(target_fpr,float)
    if a.shape!=b.shape or a.ndim!=2 or not a.size or not np.isfinite(a).all() or not np.isfinite(b).all() or min(a.min(),b.min())<0 or max(a.max(),b.max())>1:raise ValueError('paired reference x draw rate matrices in [0,1] required')
    waves=[np.quantile(np.abs(x-np.median(x,axis=1,keepdims=True)),.9,axis=1)*100 for x in [a,b]]
    v2=float(np.median(a-b))*100;scale=float(np.max(waves))
    return {'V1_source_centered_p90_pp':waves[0].tolist(),'V1_target_centered_p90_pp':waves[1].tolist(),'V2_signed_paired_median_pp':v2,'V3_reference_median_range_pp':[float(np.ptp(np.median(x,axis=1)))*100 for x in [a,b]],'G1_descriptive':bool(abs(v2)>0 and abs(v2)>=2*scale),'zero_wave_scale':scale==0,'note':'conditional descriptive quantities; not orthogonal variance components, causal proof or conformal guarantees'}
