# ACE - Adaptive Command Executor

> Local-first task automation using a fine-tuned 0.5B LLM. No cloud APIs, no subscriptions, runs entirely on your CPU.

[![License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](LICENSE)
[![Models](https://img.shields.io/badge/🤗-Models-yellow)](https://huggingface.co/ansh0x/ace-0.5b-gguf)

ACE detects task types automatically and generates execution plans - all running locally with a custom-trained 0.5B language model optimized for CPU inference.

## Quick Start
```bash
# Install
git clone https://github.com/ansh0x/ace
cd ace
pip install .

# Initialize (downloads models)
ace init

# Run tasks
ace run "copy /home/user/logs/*.log to /backup/"
ace run "open reddit.com"
ace run "extract emails from contacts.txt"
```

## What It Does

ACE takes natural language tasks and:
1. **Detects task type** (atomic, repetitive, or needs clarification)
2. **Generates execution plan** (CLI commands + hotkeys)
3. **Executes safely** (shows plan, optionally auto-executes)

All processing happens locally - your data never leaves your machine.

## Features

✅ **Local execution** - No cloud APIs, no data transmission  
✅ **Task type detection** - Automatic identification of atomic vs repetitive tasks  
✅ **CPU-optimized** - Runs on modern CPUs without GPU (3-10 sec on i3/i5)  
✅ **Privacy-first** - All processing happens on your machine  
✅ **Quantized models** - Efficient inference with GGUF Q4 quantization  

## Performance

| Hardware | Performance |
|----------|-------------|
| Intel i5 (2018+) / Ryzen 5 + SSD | 3-5 seconds per task |
| Intel i3 (2015+) + SSD | 5-10 seconds per task |
| Older hardware / HDD | 30-90 seconds per task |

## Current Limitations (v0.1)

⚠️ Requires full file paths (smart file search coming in v0.2)  
⚠️ Basic execution only (no visual extraction yet)  
⚠️ Limited hotkey support (Linux focus)  

See [ROADMAP](#roadmap) for planned improvements.

## Installation

### Requirements
- Python 3.8+
- 8GB RAM minimum
- 2GB disk space for models

### Setup
```bash
git clone https://github.com/yourname/ace
cd ace
pip install .
ace init  # Downloads models to ~/.ace/
```

### Manual Model Download
If `ace init` fails, download models manually:
- Task models: [HuggingFace](https://huggingface.co/ansh0x/ace-0.5b-gguf)
- Place in `~/.ace/models/llm/`

## Usage

### Basic Commands
```bash
# Run a task
ace run "your task here"

# Use quantized model (faster, slightly lower quality)
ace run -q "your task"

# Disable caching (slower but fresh results)
ace run --no-cache "your task"

# Verbose output (for debugging)
ace run --verbose "your task"
```

### List Available Hotkeys
```bash
ace hotkey list
ace hotkey list -g  # List groups
```

### Configuration
Configuration file is in `~/.ace/config.json`
- Right now there no customizations available.
- They will be avaialble in future

## Technical Details

### Architecture
- **Base Model:** Qwen2-0.5B fine-tuned with LoRA
- **Training Data:** ~1000 task examples (atomic + repetitive)
- **Quantization:** GGUF Q4_K_M (300MB)
- **Inference:** llama.cpp (CPU-optimized)
- **Search:** Semantic hotkey/file matching with sentence-transformers

### Training
Trained on custom dataset covering:
- File operations (copy, move, delete)
- Browser automation (for now only opens browser and websites, refer to example/youtube_test.mkv)
- Task classification (atomic vs repetitive vs clarification)

## Roadmap

**v0.2** (In about a month)
- Smart file path detection
- Performance optimizations (special tokens)
- Better error handling
- More customizable using the config.json 

**v0.3+**
- VLM integration for visual tasks
- YOLO for better UI navigation
- Improved repetitive task handling
- User corrections → model improvement

## Contributing

Contributions welcome! Areas that need help:
- Testing on different hardware
- Testing workflow on Windows
- Documentation improvements
- Bug reports and feature requests

Please open an issue before starting major work.

## License

### Code
**AGPL-3.0** - See [LICENSE](LICENSE)

This means:
- ✅ Free to use, modify, distribute
- ✅ Must share source code of any modifications
- ✅ Must use AGPL-3.0 for derivative works
- ❌ Cannot use in closed-source commercial products without permission

### Models
**CC BY-NC-SA 4.0** - See model repository

- ✅ Free for personal and research use
- ❌ Commercial use requires separate license
- ✅ Must credit the author
- ✅ Derivatives must use same license

### AI Training Restriction
Training of AI/ML models using this code or model weights is prohibited without explicit written permission.

For commercial licensing inquiries: [your email]

**Built with:** PyTorch • Transformers • llama.cpp • sentence-transformers

**Models:** [HuggingFace](https://huggingface.co/ansh0x/ace-0.5b-gguf) | **Discuss:** [Issues](https://github.com/ansh0x/ace/issues)
