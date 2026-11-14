import csv
import json
from pathlib import Path
from PIL import Image
import pytest
from scripts.usa_annotations_to_coco import convert_annotations


def write_manifest(path, rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['image_file','split','source_group','x','y','width','height'])
        writer.writeheader(); writer.writerows(rows)


def row(name, split, group):
    return dict(image_file=name,split=split,source_group=group,x='',y='',width='',height='')


def test_train_valid_conversion_never_opens_test_image(tmp_path):
    images=tmp_path/'images';images.mkdir()
    Image.new('RGB',(20,20),'red').save(images/'train.jpg')
    Image.new('RGB',(20,20),'blue').save(images/'valid.jpg')
    manifest=tmp_path/'annotations.csv'
    write_manifest(manifest,[row('train.jpg','train','day_23'),row('valid.jpg','valid','day_19'),
                             row('test_image_that_is_not_present.jpg','test','reserved_day')])
    output=tmp_path/'prepared'
    summary=convert_annotations(images,manifest,output,splits=('train','valid'))
    assert set(summary)=={'train','valid'}
    assert not (output/'test').exists()
    assert json.loads((output/'valid/_annotations.coco.json').read_text())['annotations']==[]


def test_camera_day_cannot_cross_train_and_validation(tmp_path):
    images=tmp_path/'images';images.mkdir()
    Image.new('RGB',(20,20),'red').save(images/'a.jpg')
    Image.new('RGB',(20,20),'blue').save(images/'b.jpg')
    manifest=tmp_path/'annotations.csv'
    write_manifest(manifest,[row('a.jpg','train','same_day'),row('b.jpg','valid','same_day')])
    with pytest.raises(ValueError,match='grupo|group'):
        convert_annotations(images,manifest,tmp_path/'bad',splits=('train','valid'))
