# mmchatbot
Multi-Modal Care Chatbot with Diffusion Model

## Installation
### conda environment
```
conda create -n rasa python=3.8
conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia
```

### diffusion model
```
pip install --upgrade diffusers[torch]
pip install accelerate
pip install transformers
pip install controlnet_aux

```

### rasa
```
pip install rasa
pip install spacy
pip install chardet
pip install --upgrade rasa # for legacy error
```

### web ui
```
pip install flask
```

### optional
```
pip install chardet
pip install cchardet
```

## Rasa train
```
cd rasa
rasa train
```
