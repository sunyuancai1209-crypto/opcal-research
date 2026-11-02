# 工作点标定评测库 opcal

研究工具0.1.2，MIT许可，只需NumPy。实现通用统计评测，不包含异常检测器、预训练权重或正式共形保证；不将标准统计方法冒称算法创新。代码在本仓库公开，尚未上传PyPI。

安装：在仓库根目录执行 `python -m pip install .`。不要假设PyPI已有本项目同名包。

## 输入与运行

Python API通过 `from opcal import calibrate, fpr_report, pooling_report, grouped_ap_bootstrap, source_diagnostics` 使用。参数/输出如下：

- `calibrate(normal_scores, independent_unit=..., calibration_ids=..., evaluation_ids=..., q=.99)`：N×H×W正常标定评分，显式角色身份隔离；返回线性经验分位阈值。对象多图可以同ID，件数按唯一ID计，像素仍按池化评分计。对象样本量与像素数不等同。
- `fpr_report(scores, masks, normal_images, threshold)`：同形二元缺陷掩膜、每图正常标记，输出正常整图像素FPR、全部负像素FPR及缺陷像素召回；含命中数与分母。使用严格 `score > threshold`。零分母返回None。
- `pooling_report(scores, masks, edges)`：检查逐图直方图可加性；报告精确池化AP、分箱AP、近似误差及被裁到首尾箱的像素数。箱网格由调用方提供；建议仅用标定数据冻结，不能看测试标签选箱。
- `grouped_ap_bootstrap(scores_a, scores_b, masks, independent_unit=..., object_ids=..., edges=..., repeats=2000, seed=0)`：配对对象/图像成组、正常/含缺陷组分层bootstrap，返回a减b的池化AP差和分箱百分位近似区间。一个对象多图始终同进同出；不是跨条件AP宏平均，也不自动推类别泛化。必须另看分箱精确误差，不能把近似区间当精确值。
- `source_diagnostics(source_fpr, target_fpr)`：两组同形“参考×抽样次数”的已实现FPR矩阵。输出V1中心化p90、V2配对差中位、V3参考中位全距和描述性G1。调用方负责配对意义与角色/来源定义；不是因果或正交方差分解，零波动基准必须单列解释。

采样单位必须显式为`object`或`image`，拒绝`pixel`；object模式要求ID。image模式不能用重复ID伪装独立图。声明仅能检查接口一致性，不能核验实际物理独立/批次关系。不同对象ID不必然意味着独立物理工件。

命令行：`python -m opcal 输入.npz --output 新报告.json --unit object`。

NPZ必须包含：calibration_scores、calibration_ids、scores、masks、normal_images、object_ids。身份用非object dtype字符串，评分图N×H×W，normal_images是二元N向量。标定图被调用方声明为正常；工具不读取图片鉴定标签真伪。输出文件必须不存在，防止覆盖。

`examples/ten_minute.py`可生成确定性教学NPZ，并输出JSON；它是合成接口示例。真实配对光照研究数据的独立归档地址为【待补充】。

## 限制与出处

经验q99不等于带有限样本秩修正的split conformal；空间相关像素不提供独立样本保证。所有区间依赖指定分组与固定评分，无法自动修复分布偏移。几次重抽不能证明像素级样本量下限。工具打包不替代文献查新或独立验证。

本项目统计实现与测试自写，标准知识参考：Tibshirani等《Conformal Prediction Under Covariate Shift》(NeurIPS2019)，https://papers.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html 。代码未复制该文或网络异常检测算法实现。使用本工具的研究应报告数据版本、支持/标定/评价身份、独立单元、分母、阈值不等号、箱网格、种子和不通过结果。


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

For a real detector, replace the NPZ arrays with separate normal calibration maps and evaluation maps/masks. Supply genuine grouping IDs; keep calibration and evaluation identities disjoint. Public experiment archive: 【待补充】.
