from src.train import compatible_training_arguments


def test_old_transformers_keeps_supported_values():
    def legacy(*,warmup_ratio,save_safetensors,per_device_train_batch_size,num_train_epochs): pass
    values=dict(warmup_ratio=.05,save_safetensors=True,per_device_train_batch_size=8,num_train_epochs=50)
    assert compatible_training_arguments(legacy,values,train_examples=249)==values


def test_new_transformers_converts_warmup_to_steps_and_keeps_unknown_settings():
    def modern(*,warmup_steps,per_device_train_batch_size,num_train_epochs): pass
    values=dict(warmup_ratio=.05,save_safetensors=True,per_device_train_batch_size=8,num_train_epochs=50,
                unsupported_option='must not disappear')
    result=compatible_training_arguments(modern,values,train_examples=249)
    assert result['warmup_steps']==80
    assert 'warmup_ratio' not in result and 'save_safetensors' not in result
    assert result['unsupported_option']=='must not disappear'
