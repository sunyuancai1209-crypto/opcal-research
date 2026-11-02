# ������궨����� opcal

�о�����0.1.2��MIT���ɣ�ֻ��NumPy��ʵ��ͨ��ͳ�����⣬�������쳣�������Ԥѵ��Ȩ�ػ���ʽ���α�֤��������׼ͳ�Ʒ���ð���㷨���¡������ڱ��ֿ⹫������δ�ϴ�PyPI��

��װ���ڲֿ��Ŀ¼ִ�� `python -m pip install .`����Ҫ����PyPI���б���Ŀͬ������

## ����������

Python APIͨ�� `from opcal import calibrate, fpr_report, pooling_report, grouped_ap_bootstrap, source_diagnostics` ʹ�á�����/������£�

- `calibrate(normal_scores, independent_unit=..., calibration_ids=..., evaluation_ids=..., q=.99)`��N��H��W�����궨���֣���ʽ��ɫ���ݸ��룻�������Ծ����λ��ֵ�������ͼ����ͬID��������ΨһID�ƣ������԰��ػ����ּơ�����������������������ͬ��
- `fpr_report(scores, masks, normal_images, threshold)`��ͬ�ζ�Ԫȱ����Ĥ��ÿͼ������ǣ����������ͼ����FPR��ȫ��������FPR��ȱ�������ٻأ������������ĸ��ʹ���ϸ� `score > threshold`�����ĸ����None��
- `pooling_report(scores, masks, edges)`�������ͼֱ��ͼ�ɼ��ԣ����澫ȷ�ػ�AP������AP�����������õ���β������������������ɵ��÷��ṩ��������ñ궨���ݶ��ᣬ���ܿ����Ա�ǩѡ�䡣
- `grouped_ap_bootstrap(scores_a, scores_b, masks, independent_unit=..., object_ids=..., edges=..., repeats=2000, seed=0)`����Զ���/ͼ����顢����/��ȱ����ֲ�bootstrap������a��b�ĳػ�AP��ͷ���ٷ�λ�������䡣һ�������ͼʼ��ͬ��ͬ�������ǿ�����AP��ƽ����Ҳ���Զ�����𷺻��������������侫ȷ�����ܰѽ������䵱��ȷֵ��
- `source_diagnostics(source_fpr, target_fpr)`������ͬ�Ρ��ο�����������������ʵ��FPR�������V1���Ļ�p90��V2��Բ���λ��V3�ο���λȫ���������G1�����÷���������������ɫ/��Դ���壻�����������������ֽ⣬�㲨����׼���뵥�н��͡�

������λ������ʽΪ`object`��`image`���ܾ�`pixel`��objectģʽҪ��ID��imageģʽ�������ظ�IDαװ����ͼ���������ܼ��ӿ�һ���ԣ����ܺ���ʵ����������/���ι�ϵ����ͬ����ID����Ȼ��ζ�Ŷ�������������

�����У�`python -m opcal ����.npz --output �±���.json --unit object`��

NPZ���������calibration_scores��calibration_ids��scores��masks��normal_images��object_ids�������÷�object dtype�ַ���������ͼN��H��W��normal_images�Ƕ�ԪN�������궨ͼ�����÷�����Ϊ���������߲���ȡͼƬ������ǩ��α������ļ����벻���ڣ���ֹ���ǡ�

`examples/ten_minute.py`������ȷ���Խ�ѧNPZ�������JSON�����Ǻϳɽӿ�ʾ������ʵ��Թ����о����ݵĶ����鵵��ַΪ�������䡿��

## ���������

����q99�����ڴ�����������������split conformal���ռ�������ز��ṩ����������֤��������������ָ��������̶����֣��޷��Զ��޸��ֲ�ƫ�ơ������س鲻��֤�����ؼ����������ޡ����ߴ����������ײ��»������֤��

����Ŀͳ��ʵ���������д����׼֪ʶ�ο���Tibshirani�ȡ�Conformal Prediction Under Covariate Shift��(NeurIPS2019)��https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html ������δ���Ƹ��Ļ������쳣����㷨ʵ�֡�ʹ�ñ����ߵ��о�Ӧ�������ݰ汾��֧��/�궨/�������ݡ�������Ԫ����ĸ����ֵ���Ⱥš����������ӺͲ�ͨ�������


## Third-party reproduction in approximately ten minutes

Python 3.10+ is required. From a clean clone:

```text
python -m venv .venv
# Activate the environment using your operating system's standard command.
python -m pip install .
python examples/ten_minute.py --output example_output
python -m opcal example_output/input.npz --output example_output/cli_report.json --unit object
```

Both reports use the same calibration threshold, FPR denominators and pooled AP. The example verifies additive histogram counts. These are generated interface data, not experimental performance results. No bootstrap experiment is run by this quick start. Optional developer tests: `python -m pip install ".[test]"` then `python -m pytest tests -q`.

For a real detector, replace the NPZ arrays with separate normal calibration maps and evaluation maps/masks. Supply genuine grouping IDs; keep calibration and evaluation identities disjoint. Public experiment archive: �������䡿.
