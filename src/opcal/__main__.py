"""NPZ adapter; explicit identities are required to verify disjoint roles."""
import argparse,json
from pathlib import Path
import numpy as np
from . import calibrate,fpr_report,pooling_report

def main():
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('--output',required=True);p.add_argument('--unit',required=True,choices=['object','image']);a=p.parse_args()
    z=np.load(a.input,allow_pickle=False)
    cal=calibrate(z['calibration_scores'],independent_unit=a.unit,calibration_ids=z['calibration_ids'],evaluation_ids=z['object_ids'])
    low=min(0.,float(z['calibration_scores'].min()));high=max(low+1.,float(z['calibration_scores'].max())*4)
    result={'calibration':cal,'operating_point':fpr_report(z['scores'],z['masks'],z['normal_images'],cal['threshold']),'pooling':pooling_report(z['scores'],z['masks'],np.linspace(low,high,1025))}
    with Path(a.output).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)

if __name__=='__main__':main()
