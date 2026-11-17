# Original six-photo Ecuador execution

These files preserve the metrics and warnings printed by the user-run notebook in commit
`0b7bcb7739f43d1b41f0a1dbc5c58e3f9207f491`. They are historical evidence, not a new execution.
The original executed notebook remains available in that commit.

The set has four training, one validation and one test image, all positive scenes.
The run reached epoch 30; the best displayed validation loss was 3.944046 at epoch 30.
Validation AP was zero. The one-image test reported AP50=1 and AP50:95=0.7,
but TP=0, FP=0 and FN=1 at confidence 0.70. AP and fixed-confidence counts answer different questions.
These numbers require re-evaluation after checkpoint restoration and geometry verification.

The training table's displayed training loss is the latest logging interval, not an epoch average.
The test image has already been inspected; a fresh acceptance study needs new independent groups.
Actual Ecuador weights were not found. The candidate in the Drive Ecuador-named directory
identifies itself as USA seed 1; it must not be relabeled or activated as Ecuador.
