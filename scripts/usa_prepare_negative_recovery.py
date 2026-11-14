"""Merge reviewed camera negatives with train/valid without consuming test."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.usa_annotations_to_coco import convert_annotations

FIELDS = ['image_file','split','source_group','x','y','width','height']


def prepare(base_dataset: Path, base_annotations: Path, negative_pack: Path,
            output: Path) -> dict:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f'Refusing to overwrite existing preparation: {output}')
    staging = output / 'source_images'
    staging.mkdir(parents=True, exist_ok=True)
    with base_annotations.open(encoding='utf-8-sig',newline='') as handle:
        base_rows = [row for row in csv.DictReader(handle)
                     if row['split'].lower() in {'train','valid','val'}]
    with (negative_pack/'manual_scene_annotations_negatives.csv').open(encoding='utf-8-sig',newline='') as handle:
        negative_rows = list(csv.DictReader(handle))
    if {row['split'] for row in negative_rows} != {'train','valid'}:
        raise ValueError('Reviewed negative pack must have train and valid only.')
    if any(any(str(row.get(k,'') or '').strip() for k in ('x','y','width','height'))
           for row in negative_rows):
        raise ValueError('A negative row must have no plate box.')
    rows = base_rows + negative_rows
    names = {}
    for row in base_rows:
        name = row['image_file']; relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe image name in base annotations.')
        split = 'valid' if row['split']=='val' else row['split']
        source = base_dataset/split/'images'/relative
        if not source.is_file():
            raise FileNotFoundError(source)
        names[name] = source
    for row in negative_rows:
        name = row['image_file']; relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or name in names:
            raise ValueError('Unsafe or duplicate negative image name.')
        names[name] = negative_pack/'images'/relative
    for name,source in names.items():
        destination = staging/name; destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
    manifest = output/'annotations_train_valid.csv'
    with manifest.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS,extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
    summary=convert_annotations(staging,manifest,output,verify_hashes=True,splits=('train','valid'))
    result={'splits':summary,'test_included':False,'test_evaluated':False,
            'negative_pack':negative_pack.name,
            'target_camera_grouping':'recording day; all March 23 train, March 19 valid',
            'final_test_blocker':'A previously unexamined target-camera recording/day with negatives is required.'}
    (output/'recovery_dataset_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # The final COCO copies are self-contained. Staging is only this new run's
    # temporary copy and can be removed after conversion succeeds.
    shutil.rmtree(staging)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dataset',type=Path,required=True)
    parser.add_argument('--base-annotations',type=Path,required=True)
    parser.add_argument('--negative-pack',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(prepare(args.base_dataset,args.base_annotations,args.negative_pack,args.output),indent=2))


if __name__=='__main__':
    main()
