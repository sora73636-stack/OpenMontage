---
license: apache-2.0
library_name: pytorch
pipeline_tag: depth-estimation
---

# Video Depth Anything

This repository contains the model described in [Video Depth Anything: Consistent Depth Estimation for Super-Long Videos](https://huggingface.co/papers/2501.12375).

Project Page: https://videodepthanything.github.io

## About
This model is based on [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2), and can be applied to arbitrarily long videos without compromising quality, consistency, or generalization ability. Compared with other diffusion-based models, it enjoys faster inference speed, fewer parameters, and higher consistent depth accuracy.

## Usage
```bash
git clone https://github.com/DepthAnything/Video-Depth-Anything
cd Video-Depth-Anything
pip install -r requirements.txt
```

Download the checkpoints listed [here](#pre-trained-models) and put them under the `checkpoints` directory.
```bash
bash get_weights.sh
```

### Inference a video
```bash
python3 run.py --input_video ./assets/example_videos/davis_rollercoaster.mp4 --output_dir ./outputs --encoder vitl
```