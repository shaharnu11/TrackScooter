---
license: apache-2.0
pipeline_tag: text-generation
language:
- en
- he
tags:
- pretrained
- mlx
- mlx-my-repo
inference:
  parameters:
    temperature: 0.6
base_model: dicta-il/DictaLM-3.0-1.7B-Instruct
---

# ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit

The Model [ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit](https://huggingface.co/ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit) was converted to MLX format from [dicta-il/DictaLM-3.0-1.7B-Instruct](https://huggingface.co/dicta-il/DictaLM-3.0-1.7B-Instruct) using mlx-lm version **0.29.1**.

## Use with mlx

```bash
pip install mlx-lm
```

```python
from mlx_lm import load, generate

model, tokenizer = load("ssdataanalysis/DictaLM-3.0-1.7B-Instruct-mlx-8Bit")

prompt="hello"

if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
    messages = [{"role": "user", "content": prompt}]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

response = generate(model, tokenizer, prompt=prompt, verbose=True)
```
