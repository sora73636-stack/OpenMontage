---
tags:
- ltx-video
- image-to-video
pinned: true
language:
- en
license: other
pipeline_tag: text-to-video
library_name: diffusers
---

# LTX-Video Model Card
This model card focuses on the model associated with the LTX-Video model, codebase available [here](https://github.com/Lightricks/LTX-Video).

LTX-Video is the first DiT-based video generation model capable of generating high-quality videos in real-time. It produces 30 FPS videos at a 1216×704 resolution faster than they can be watched. Trained on a large-scale dataset of diverse videos, the model generates high-resolution videos with realistic and varied content.
We provide a model for both text-to-video as well as image+text-to-video usecases

<img src="./media/trailer.gif" alt="trailer" width="512">


| | | | |
|:---:|:---:|:---:|:---:|
| ![example1](./media/ltx-video_example_00001.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman with long brown hair and light skin smiles at another woman...</summary>A woman with long brown hair and light skin smiles at another woman with long blonde hair. The woman with brown hair wears a black jacket and has a small, barely noticeable mole on her right cheek. The camera angle is a close-up, focused on the woman with brown hair's face. The lighting is warm and natural, likely from the setting sun, casting a soft glow on the scene. The scene appears to be real-life footage.</details> | ![example2](./media/ltx-video_example_00002.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman walks away from a white Jeep parked on a city street at night...</summary>A woman walks away from a white Jeep parked on a city street at night, then ascends a staircase and knocks on a door. The woman, wearing a dark jacket and jeans, walks away from the Jeep parked on the left side of the street, her back to the camera; she walks at a steady pace, her arms swinging slightly by her sides; the street is dimly lit, with streetlights casting pools of light on the wet pavement; a man in a dark jacket and jeans walks past the Jeep in the opposite direction; the camera follows the woman from behind as she walks up a set of stairs towards a building with a green door; she reaches the top of the stairs and turns left, continuing to walk towards the building; she reaches the door and knocks on it with her right hand; the camera remains stationary, focused on the doorway; the scene is captured in real-life footage.</details> | ![example3](./media/ltx-video_example_00003.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman with blonde hair styled up, wearing a black dress...</summary>A woman with blonde hair styled up, wearing a black dress with sequins and pearl earrings, looks down with a sad expression on her face. The camera remains stationary, focused on the woman's face. The lighting is dim, casting soft shadows on her face. The scene appears to be from a movie or TV show.</details> | ![example4](./media/ltx-video_example_00004.gif)<br><details style="max-width: 300px; margin: auto;"><summary>The camera pans over a snow-covered mountain range...</summary>The camera pans over a snow-covered mountain range, revealing a vast expanse of snow-capped peaks and valleys.The mountains are covered in a thick layer of snow, with some areas appearing almost white while others have a slightly darker, almost grayish hue. The peaks are jagged and irregular, with some rising sharply into the sky while others are more rounded. The valleys are deep and narrow, with steep slopes that are also covered in snow. The trees in the foreground are mostly bare, with only a few leaves remaining on their branches. The sky is overcast, with thick clouds obscuring the sun. The overall impression is one of peace and tranquility, with the snow-covered mountains standing as a testament to the power and beauty of nature.</details> |
| ![example5](./media/ltx-video_example_00005.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman with light skin, wearing a blue jacket and a black hat...</summary>A woman with light skin, wearing a blue jacket and a black hat with a veil, looks down and to her right, then back up as she speaks; she has brown hair styled in an updo, light brown eyebrows, and is wearing a white collared shirt under her jacket; the camera remains stationary on her face as she speaks; the background is out of focus, but shows trees and people in period clothing; the scene is captured in real-life footage.</details> | ![example6](./media/ltx-video_example_00006.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A man in a dimly lit room talks on a vintage telephone...</summary>A man in a dimly lit room talks on a vintage telephone, hangs up, and looks down with a sad expression. He holds the black rotary phone to his right ear with his right hand, his left hand holding a rocks glass with amber liquid. He wears a brown suit jacket over a white shirt, and a gold ring on his left ring finger. His short hair is neatly combed, and he has light skin with visible wrinkles around his eyes. The camera remains stationary, focused on his face and upper body. The room is dark, lit only by a warm light source off-screen to the left, casting shadows on the wall behind him. The scene appears to be from a movie.</details> | ![example7](./media/ltx-video_example_00007.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A prison guard unlocks and opens a cell door...</summary>A prison guard unlocks and opens a cell door to reveal a young man sitting at a table with a woman. The guard, wearing a dark blue uniform with a badge on his left chest, unlocks the cell door with a key held in his right hand and pulls it open; he has short brown hair, light skin, and a neutral expression. The young man, wearing a black and white striped shirt, sits at a table covered with a white tablecloth, facing the woman; he has short brown hair, light skin, and a neutral expression. The woman, wearing a dark blue shirt, sits opposite the young man, her face turned towards him; she has short blonde hair and light skin. The camera remains stationary, capturing the scene from a medium distance, positioned slightly to the right of the guard. The room is dimly lit, with a single light fixture illuminating the table and the two figures. The walls are made of large, grey concrete blocks, and a metal door is visible in the background. The scene is captured in real-life footage.</details> | ![example8](./media/ltx-video_example_00008.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman with blood on her face and a white tank top...</summary>A woman with blood on her face and a white tank top looks down and to her right, then back up as she speaks. She has dark hair pulled back, light skin, and her face and chest are covered in blood. The camera angle is a close-up, focused on the woman's face and upper torso. The lighting is dim and blue-toned, creating a somber and intense atmosphere. The scene appears to be from a movie or TV show.</details> |
| ![example9](./media/ltx-video_example_00009.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A man with graying hair, a beard, and a gray shirt...</summary>A man with graying hair, a beard, and a gray shirt looks down and to his right, then turns his head to the left. The camera angle is a close-up, focused on the man's face. The lighting is dim, with a greenish tint. The scene appears to be real-life footage. Step</details> | ![example10](./media/ltx-video_example_00010.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A clear, turquoise river flows through a rocky canyon...</summary>A clear, turquoise river flows through a rocky canyon, cascading over a small waterfall and forming a pool of water at the bottom.The river is the main focus of the scene, with its clear water reflecting the surrounding trees and rocks. The canyon walls are steep and rocky, with some vegetation growing on them. The trees are mostly pine trees, with their green needles contrasting with the brown and gray rocks. The overall tone of the scene is one of peace and tranquility.</details> | ![example11](./media/ltx-video_example_00011.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A man in a suit enters a room and speaks to two women...</summary>A man in a suit enters a room and speaks to two women sitting on a couch. The man, wearing a dark suit with a gold tie, enters the room from the left and walks towards the center of the frame. He has short gray hair, light skin, and a serious expression. He places his right hand on the back of a chair as he approaches the couch. Two women are seated on a light-colored couch in the background. The woman on the left wears a light blue sweater and has short blonde hair. The woman on the right wears a white sweater and has short blonde hair. The camera remains stationary, focusing on the man as he enters the room. The room is brightly lit, with warm tones reflecting off the walls and furniture. The scene appears to be from a film or television show.</details> | ![example12](./media/ltx-video_example_00012.gif)<br><details style="max-width: 300px; margin: auto;"><summary>The waves crash against the jagged rocks of the shoreline...</summary>The waves crash against the jagged rocks of the shoreline, sending spray high into the air.The rocks are a dark gray color, with sharp edges and deep crevices. The water is a clear blue-green, with white foam where the waves break against the rocks. The sky is a light gray, with a few white clouds dotting the horizon.</details> |
| ![example13](./media/ltx-video_example_00013.gif)<br><details style="max-width: 300px; margin: auto;"><summary>The camera pans across a cityscape of tall buildings...</summary>The camera pans across a cityscape of tall buildings with a circular building in the center. The camera moves from left to right, showing the tops of the buildings and the circular building in the center. The buildings are various shades of gray and white, and the circular building has a green roof. The camera angle is high, looking down at the city. The lighting is bright, with the sun shining from the upper left, casting shadows from the buildings. The scene is computer-generated imagery.</details> | ![example14](./media/ltx-video_example_00014.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A man walks towards a window, looks out, and then turns around...</summary>A man walks towards a window, looks out, and then turns around. He has short, dark hair, dark skin, and is wearing a brown coat over a red and gray scarf. He walks from left to right towards a window, his gaze fixed on something outside. The camera follows him from behind at a medium distance. The room is brightly lit, with white walls and a large window covered by a white curtain. As he approaches the window, he turns his head slightly to the left, then back to the right. He then turns his entire body to the right, facing the window. The camera remains stationary as he stands in front of the window. The scene is captured in real-life footage.</details> | ![example15](./media/ltx-video_example_00015.gif)<br><details style="max-width: 300px; margin: auto;"><summary>Two police officers in dark blue uniforms and matching hats...</summary>Two police officers in dark blue uniforms and matching hats enter a dimly lit room through a doorway on the left side of the frame. The first officer, with short brown hair and a mustache, steps inside first, followed by his partner, who has a shaved head and a goatee. Both officers have serious expressions and maintain a steady pace as they move deeper into the room. The camera remains stationary, capturing them from a slightly low angle as they enter. The room has exposed brick walls and a corrugated metal ceiling, with a barred window visible in the background. The lighting is low-key, casting shadows on the officers' faces and emphasizing the grim atmosphere. The scene appears to be from a film or television show.</details> | ![example16](./media/ltx-video_example_00016.gif)<br><details style="max-width: 300px; margin: auto;"><summary>A woman with short brown hair, wearing a maroon sleeveless top...</summary>A woman with short brown hair, wearing a maroon sleeveless top and a silver necklace, walks through a room while talking, then a woman with pink hair and a white shirt appears in the doorway and yells. The first woman walks from left to right, her expression serious; she has light skin and her eyebrows are slightly furrowed. The second woman stands in the doorway, her mouth open in a yell; she has light skin and her eyes are wide. The room is dimly lit, with a bookshelf visible in the background. The camera follows the first woman as she walks, then cuts to a close-up of the second woman's face. The scene is captured in real-life footage.</details> |

# Models

| Model              | Version | Notes                                                                     | inference.py config                                                                                                        | ComfyUI workflow (Recommended) |
|--------------------|---------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|------------------|
| ltxv-13b           | 0.9.7   | Highest quality, requires more VRAM                                       | [ltxv-13b-0.9.7-dev.yaml](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-13b-0.9.7-dev.yaml)               | [ltxv-13b-i2v-base.json](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/ltxv-13b-i2v-base.json)             |
| ltxv-13b-fp8       | 0.9.7   | Quantized model                                                           | Coming soon                                                                                                                | [ltxv-13b-i2v-base-fp8.json](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/ltxv-13b-i2v-base-fp8.json)             |
| ltxv-2b            | 0.9.6   | Good quality, lower VRAM requirement than ltxv-13b                        | [ltxv-2b-0.9.6-dev.yaml](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-2b-0.9.6-dev.yaml)                 | [ltxvideo-i2v.json](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/low_level/ltxvideo-i2v.json)             |
| ltxv-2b-distilled  | 0.9.6   | 15× faster, real-time capable, fewer steps needed, no STG/CFG required    | [ltxv-2b-0.9.6-distilled.yaml](https://github.com/Lightricks/LTX-Video/blob/main/configs/ltxv-2b-0.9.6-distilled.yaml)     | [ltxvideo-i2v-distilled.json](https://github.com/Lightricks/ComfyUI-LTXVideo/blob/master/example_workflows/low_level/ltxvideo-i2v-distilled.json)             |


## Model Details
- **Developed by:** Lightricks
- **Model type:** Diffusion-based text-to-video and image-to-video generation model
- **Language(s):** English


## Usage

### Direct use
You can use the model for purposes under the license:
- 2B version 0.9: [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.license.txt)
- 2B version 0.9.1 [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.1.license.txt)
- 2B version 0.9.5 [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltx-video-2b-v0.9.5.license.txt)
- 2B version 0.9.6-dev [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-2b-0.9.6-dev-04-25.license.txt)
- 2B version 0.9.6-distilled [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-2b-0.9.6-distilled-04-25.license.txt)
- 13B version 0.9.7-dev [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-13b-0.9.7-dev.license.txt)
- 13B version 0.9.7-dev-fp8 [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-13b-0.9.7-dev-fp8.license.txt)
- Temporal upscaler version 0.9.7 [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-temporal-upscaler-0.9.7.license.txt)
- Spatial upscaler version 0.9.7 [license](https://huggingface.co/Lightricks/LTX-Video/blob/main/ltxv-spatial-upscaler-0.9.7.license.txt)


### General tips:
* The model works on resolutions that are divisible by 32 and number of frames that are divisible by 8 + 1 (e.g. 257). In case the resolution or number of frames are not divisible by 32 or 8 + 1, the input will be padded with -1 and then cropped to the desired resolution and number of frames.
* The model works best on resolutions under 720 x 1280 and number of frames below 257.
* Prompts should be in English. The more elaborate the better. Good prompt looks like `The turquoise waves crash against the dark, jagged rocks of the shore, sending white foam spraying into the air. The scene is dominated by the stark contrast between the bright blue water and the dark, almost black rocks. The water is a clear, turquoise color, and the waves are capped with white foam. The rocks are dark and jagged, and they are covered in patches of green moss. The shore is lined with lush green vegetation, including trees and bushes. In the background, there are rolling hills covered in dense forest. The sky is cloudy, and the light is dim.`

### Online demo
The model is accessible right away via the following links:
- [LTX-Studio image-to-video](https://app.ltx.studio/ltx-video)
- [Fal.ai text-to-video](https://fal.ai/models/fal-ai/ltx-video)
- [Fal.ai image-to-video](https://fal.ai/models/fal-ai/ltx-video/image-to-video)
- [Replicate text-to-video and image-to-video](https://replicate.com/lightricks/ltx-video)

### ComfyUI
To use our model with ComfyUI, please follow the instructions at a dedicated [ComfyUI repo](https://github.com/Lightricks/ComfyUI-LTXVideo/).

### Run locally

#### Installation

The codebase was tested with Python 3.10.5, CUDA version 12.2, and supports PyTorch >= 2.1.2.

```bash
git clone https://github.com/Lightricks/LTX-Video.git
cd LTX-Video

# create env
python -m venv env
source env/bin/activate
python -m pip install -e .\[inference-script\]
```

#### Inference

To use our model, please follow the inference code in [inference.py](https://github.com/Lightricks/LTX-Video/blob/main/inference.py):

##### For text-to-video generation:

```bash
python inference.py --prompt "PROMPT" --height HEIGHT --width WIDTH --num_frames NUM_FRAMES --seed SEED --pipeline_config ltxv-13b-0.9.7-dev.yaml
```

##### For image-to-video generation:

```bash
python inference.py --prompt "PROMPT" --input_image_path IMAGE_PATH --height HEIGHT --width WIDTH --num_frames NUM_FRAMES --seed SEED --pipeline_config ltxv-13b-0.9.7-dev.yaml
```

### Diffusers 🧨

LTX Video is compatible with the [Diffusers Python library](https://huggingface.co/docs/diffusers/main/en/index). It supports both text-to-video and image-to-video generation.

Make sure you install `diffusers` before trying out the examples below.

```bash
pip install -U git+https://github.com/huggingface/diffusers
```

Now, you can run the examples below:

```py
import torch
from diffusers import LTXPipeline
from diffusers.utils import export_to_video

pipe = LTXPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.bfloat16)
pipe.to("cuda")

prompt = "A woman with long brown hair and light skin smiles at another woman with long blonde hair. The woman with brown hair wears a black jacket and has a small, barely noticeable mole on her right cheek. The camera angle is a close-up, focused on the woman with brown hair's face. The lighting is warm and natural, likely from the setting sun, casting a soft glow on the scene. The scene appears to be real-life footage"
negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted"

video = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    width=704,
    height=480,
    num_frames=161,
    num_inference_steps=50,
).frames[0]
export_to_video(video, "output.mp4", fps=24)
```

For image-to-video:

```py
import torch
from diffusers import LTXImageToVideoPipeline
from diffusers.utils import export_to_video, load_image

pipe = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video", torch_dtype=torch.bfloat16)
pipe.to("cuda")

image = load_image(
    "https://huggingface.co/datasets/a-r-r-o-w/tiny-meme-dataset-captioned/resolve/main/images/8.png"
)
prompt = "A young girl stands calmly in the foreground, looking directly at the camera, as a house fire rages in the background. Flames engulf the structure, with smoke billowing into the air. Firefighters in protective gear rush to the scene, a fire truck labeled '38' visible behind them. The girl's neutral expression contrasts sharply with the chaos of the fire, creating a poignant and emotionally charged scene."
negative_prompt = "worst quality, inconsistent motion, blurry, jittery, distorted"

video = pipe(
    image=image,
    prompt=prompt,
    negative_prompt=negative_prompt,
    width=704,
    height=480,
    num_frames=161,
    num_inference_steps=50,
).frames[0]
export_to_video(video, "output.mp4", fps=24)
```

To learn more, check out the [official documentation](https://huggingface.co/docs/diffusers/main/en/api/pipelines/ltx_video). 

Diffusers also supports directly loading from the original LTX checkpoints using the `from_single_file()` method. Check out [this section](https://huggingface.co/docs/diffusers/main/en/api/pipelines/ltx_video#loading-single-files) to learn more.

## Limitations
- This model is not intended or able to provide factual information.
- As a statistical model this checkpoint might amplify existing societal biases.
- The model may fail to generate videos that matches the prompts perfectly.
- Prompt following is heavily influenced by the prompting-style.