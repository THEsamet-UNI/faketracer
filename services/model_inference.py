"""Model architecture helpers and weight loading for inference.
Provides a simple MobileNetV2-based binary classifier scaffold and a loader
that attempts to populate it from a given state_dict file.
"""
def build_mobilenetv2_binary(num_classes=1, pretrained=False):
    try:
        import torch
        import torchvision
        model = torchvision.models.mobilenet_v2(pretrained=pretrained)
        # replace classifier
        in_features = model.classifier[1].in_features if hasattr(model, 'classifier') else 1280
        model.classifier = torch.nn.Sequential(
            torch.nn.Dropout(p=0.2, inplace=False),
            torch.nn.Linear(in_features, num_classes)
        )
        return model
    except Exception as e:
        raise RuntimeError('PyTorch/torchvision required for model construction: ' + str(e))


def load_state_dict_into_model(model, path, map_location='cpu'):
    import torch
    try:
        sd = torch.load(path, map_location=map_location)
        # if it's a checkpoint dict with 'state_dict'
        if isinstance(sd, dict) and 'state_dict' in sd and isinstance(sd['state_dict'], dict):
            sd = sd['state_dict']
        # try to be forgiving about prefixed keys
        model_state = model.state_dict()
        try:
            model.load_state_dict(sd)
            return True, 'loaded'
        except RuntimeError:
            # attempt prefix stripping
            new_sd = {}
            for k, v in sd.items():
                nk = k.replace('module.', '')
                new_sd[nk] = v
            try:
                model.load_state_dict(new_sd)
                return True, 'loaded_after_strip'
            except Exception as e:
                return False, f'load_failed: {e}'
    except Exception as e:
        return False, str(e)


def build_and_load(path, map_location='cpu'):
    """Build a MobilenetV2 binary classifier and attempt to load weights from path.
    Returns (success_bool, model_or_error_message).
    """
    try:
        model = build_mobilenetv2_binary(num_classes=1, pretrained=False)
    except Exception as e:
        return False, f'build_failed: {e}'
    ok, msg = load_state_dict_into_model(model, path, map_location=map_location)
    if not ok:
        return False, msg
    return True, model
