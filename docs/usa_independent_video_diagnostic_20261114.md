# USA independent-recording diagnostic: automatic access remains blocked

The selected seed-2 RT-DETRv2-S checkpoint was evaluated on the UCSD recording from **2005-04-06**, a different recording day from the March development clips. The diagnostic completed and failed qualification. It does not establish production readiness.

400 frames were uniformly sampled from 8,856 concatenated JPEGs before selected-checkpoint inference. The assisted reference was frozen and saved before inference. Full-scene review resolved 319 frames: 200 positive and 119 negative, containing 256 reference plates. The other 81 frames have uncertain regions and are excluded as whole frames from primary detection scoring, never counted as negatives. An independent human annotation audit is pending.

| Measurement | Observed result |
|---|---:|
| Frozen detector confidence / matching IoU | 0.70 / 0.50 |
| True positives / unmatched detections / false negatives | 141 / 5 / 115 |
| Detection precision / recall | 96.58% / 55.08% |
| Negative frames with false detections | 3 / 119 |
| Provisional resolved-reference mAP50–95 / mAP50 | 0.4748 / 0.8006 |
| Exact serial OCR on reference crops | 24 / 47 (51.06%) |
| Exact scene serial above OCR confidence 0.94 | 17 / 47 (36.17%) |
| Usable jurisdiction predictions on detected crops | 0 / 181 |
| Confirmed automatic decisions | 0 |

The detector's descriptive 95% Wilson precision interval is 92.23–98.53%; recall is 48.95–61.05%. Consecutive-block bootstrap intervals are in the aggregate JSON. These intervals describe this recording and do not estimate between-day or between-camera uncertainty. Frames and repeated vehicles are correlated. The new results use different data from the historical 0.8321 Roboflow validation figure.

Four unmatched detections are non-plate objects: NISSAN tailgate lettering, a cyclist helmet, and a BMW dealer insert in two frames. One unmatched detection is on a real plate but misses the frozen IoU criterion. The post-run error review did not alter the frozen reference or retune confidence.

Serial reference covers 47 instances and 32 distinct identifiers. Of the 15 reference crops above minimum character probability 0.94, 14 are correct. Earlier OCR diagnostic exposure to some UCSD plate sequences and base-model training provenance are not fully audited. Do not call this a certified unseen OCR benchmark.

Five provisional California jurisdiction labels cover three identifiers, with zero correct state reads. Two temporal decision cases were predeclared, one simulated allow and one deny; both remain manual. No accepted state-plus-serial frames exist, so the two-frame / 7.5-second rule cannot produce an automatic event. Zero false grants with zero total grants is not a successful access-control test.

The first OCR continuation was blocked by automatic review over a possible external dependency connection. The completed 75-frame partial was retained; the remaining 325 frames ran with kernel-denied network socket syscalls and ONNX Runtime telemetry disabled. The network denial was verified before importing the runtime. Detector uses native OpenVINO CPU; OCR uses ONNX Runtime CPU on the AMD host.

`independent_recording_diagnostic_evaluated=true`, `recording_consumed_for_evaluation=true`, `final_test_protocol_complete=false`, `usable_for_access_decisions=false`, and `operational_threshold=null`. The retained `final_test_evaluated=false` field refers to the incomplete qualified final protocol; the April recording diagnostic **has run**. This recording cannot be reused as unseen data after tuning.

Complete a human audit of the uncertain frames and state/serial references. Improve detection and jurisdiction OCR using development recordings and representative negatives, excluding this consumed recording. Reserve a different untouched recording date for the next qualification. The original 42-positive reserved test was not run here. No Space deployment or automatic authorization is included.

Aggregate evidence: [usa_independent_video_diagnostic_20261114.json](../results/metrics/usa_independent_video_diagnostic_20261114.json). Raw frames, source serials, OCR rows, reference annotations, model artifacts and hashes remain in private evidence storage. The frozen protocol narrative understates jurisdiction identity support as two; actual frozen annotations contain three, including one single-frame identity, while the two predeclared temporal cases are unchanged.

Source: [UCSD/Calit2 Car Database](https://belongielab.org/car_data.html). The original UCSD rights notice is retained with private evidence; no blanket commercial-use or redistribution permission for footage is asserted.
