# Caikit NLP

`caikit_nlp` is a [Caikit](https://github.com/caikit/caikit) library that currently provides functionalities including:
- [PEFT prompt tuning](https://github.com/huggingface/peft)
- MPT (multi-task prompt tuning)
- General NLP module data models and capabilities such as tokenization, text and token classification, etc.

#### Prompt tuning details
- More information on MPT can be found at: https://arxiv.org/abs/2303.02861
- Currently causal language models and sequence-to-sequence models are supported.

#### Notes

- The data model for text generative capabilities is baked into this repository itself at `caikit_nlp/data_model/generation.py`.
