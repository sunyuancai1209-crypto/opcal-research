"""Deterministic interface demonstration; no experimental bootstrap."""
from pathlib import Path
import argparse,json
import numpy as np
from opcal import calibrate,fpr_report,pooling_report
p=argparse.ArgumentParser();p.add_argument('--output',default='example_output');a=p.parse_args()
out=Path(a.output);out.mkdir(exist_ok=False)
rng=np.random.default_rng(45);cal=rng.random((4,8,8));s=rng.random((8,8,8));y=np.zeros(s.shape,bool);y[4:,2:4,2:4]=True;s[y]+=1
cids=np.array(['c0','c1','c2','c3']);ids=np.array([f'e{i}' for i in range(8)]);good=np.arange(8)<4
np.savez(out/'input.npz',calibration_scores=cal,calibration_ids=cids,scores=s,masks=y,normal_images=good,object_ids=ids)
c=calibrate(cal,independent_unit='object',calibration_ids=cids,evaluation_ids=ids)
r={'kind':'synthetic interface example, not benchmark evidence','calibration':c,'operating_point':fpr_report(s,y,good,c['threshold']),'pooling':pooling_report(s,y,np.linspace(0,float(cal.max())*4,1025))}
assert r['pooling']['additive_count_max_error']==0
(out/'api_report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('EXAMPLE_PASS',out.resolve())
