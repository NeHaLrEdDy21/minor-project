# AI Defense Lawyer System - Setup & Usage Guide

## Overview

The system has been enhanced with:
- 🤖 **LLM Defense Analyzer** - Llama-powered defense arguments (weighted 70% in verdict scoring)
- 🎵 **Text-to-Speech** - coqui-tts audio verdict narration
- 🌐 **Web Interface** - Interactive Flask web UI for case analysis
- ⚖️ **Blended Scoring** - Combines symbolic logic with AI-generated arguments

## Installation

### 1. Install Core Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `spacy` - NLP for fact extraction
- `langchain` - LLM orchestration
- `TTS` - coqui audio synthesis
- `pyttsx3` - Fallback TTS
- `flask` - Web framework

### 2. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 3. Setup Local Llama (for LLM Defense Analysis)

#### Option A: Using Ollama (Recommended)

1. **Install Ollama** from https://ollama.ai
2. **Start the Ollama server:**
   ```bash
   ollama serve
   ```
   (Runs in background, listens on localhost:11434)

3. **Pull Llama model:**
   ```bash
   ollama pull llama2:7b
   ```
   Other options: `neural-chat`, `dolphin-phi`, `mistral`

The system will automatically detect and use ollama for LLM analysis.

#### Option B: Using llama-cpp-python (Local)

For GPU support or standalone operation, use llama-cpp-python instead.

### 4. Verify Installation

```bash
python -c "from minor import *; print('✓ Core system loaded')"
python -c "from app import *; print('✓ Web app loaded')"
```

## Usage

### Method 1: Command-Line Analysis

#### Basic Analysis (Symbolic Rules Only)
```bash
python analyze_case.py sample_case.txt
```

#### With LLM Defense Arguments (70% LLM Weight)
```bash
python analyze_case.py sample_case.txt \
    --llm-weight 0.7 \
    --llm-model llama2
```

#### Generate Audio Verdict
```bash
python analyze_case.py sample_case.txt \
    --audio \
    --llm-weight 0.7
```

#### With Custom Burden of Proof Threshold
```bash
python analyze_case.py sample_case.txt \
    --theta 0.4  # More likely to find guilty (lower threshold)
```

#### All Options Combined
```bash
python analyze_case.py case.txt \
    --llm-weight 0.7 \
    --llm-model llama2 \
    --audio \
    --theta 0.6 \
    --verbose
```

#### View All CLI Options
```bash
python analyze_case.py --help
```

**Output:**
- `VERDICT_{CASE_NUMBER}.txt` - Full analysis report
- `VERDICT_{CASE_NUMBER}_AUDIO.wav` - Audio narration (if --audio enabled)

### Method 2: Web Interface

#### Launch Web UI
```bash
python app.py
```

Or via CLI:
```bash
python analyze_case.py --web
```

#### Access the Interface
Open browser: **http://localhost:5000**

**Features:**
- 📄 Upload case document or paste text
- ⚙️ Adjust LLM weight (0-100%)
- 🎯 Set burden of proof threshold
- 🎵 Enable audio narration
- 📊 View verdict with confidence scores
- 🛡️ See AI-generated defense arguments
- 🎵 Audio player for verdict

### Method 3: Python API

```python
from minor import DocumentParser, analyze_case_document

# Load case
doc = DocumentParser.load_from_file("case.txt")

# Analyze with LLM
result = analyze_case_document(
    doc,
    theta=0.6,           # Burden of proof
    llm_weight=0.7,      # 70% LLM, 30% symbolic
    llm_model="llama2",  # LLM model
    enable_audio=True    # Generate audio
)

# Access results
for verdict in result['verdicts']:
    print(f"{verdict.charge}: {verdict.verdict}")
    print(f"  Confidence: {verdict.confidence * 100:.1f}%")
    print(f"  LLM Arguments: {verdict.llm_arguments}")

# Save report & audio
result['report_generator'].save_report("report.txt")
result['report_generator'].generate_verdict_audio()
```

## Case Document Format

```
CASE NUMBER: 2024-CR-001234
PLAINTIFF: State of New York
DEFENDANT: John Smith
COURT: Supreme Court
JUDGE: Hon. Judge Name
DATE FILED: 2024-01-15
LOCATION: County Name
CHARGES: Assault on Minor, Battery
NARRATIVE:
On January 10, 2024, at approximately 3:45 PM, a physical altercation occurred.
John Smith assaulted Mary Johnson, age 14, a minor. The defendant struck the 
victim multiple times with his fists...
```

## Configuration

Edit `config.py` to customize:

```python
# LLM Settings
LLM_MODEL_NAME = "llama2"          # Model name
LLM_WEIGHT_DEFAULT = 0.7           # Default LLM weight
LLM_TEMPERATURE = 0.3              # Legal consistency

# TTS Settings
TTS_BACKEND = "coqui"              # "coqui" or "pyttsx3"
TTS_ENABLED = False                # Enable by default

# Burden of Proof
THETA_DEFAULT = 0.6                # 60% prosecution advantage needed

# Web Interface
WEB_PORT = 5000                    # Flask port
MAX_UPLOAD_SIZE = 10 * 1024 * 1024 # 10MB max file
```

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│             Case Document (Text/File)              │
└────────────────────┬────────────────────────────────┘
                     ▼
           ┌─────────────────────┐
           │  Neural Extraction  │  (spaCy NLP)
           │  Extract Facts      │
           └────────┬────────────┘
                    ▼
          ┌──────────────────────┐
          │  Symbolic Grounding  │  (Knowledge Base)
          │  Ground to KB Facts  │
          └────────┬─────────────┘
                   ▼
       ┌────────────────────────────┐
       │ Burden of Proof Reasoning  │  (Prosecution vs Defense)
       │ Calculate Scores           │
       └────────┬───────────────────┘
                ▼
       ┌─────────────────────────┐
       │ LLM Defense Analysis    │◄────── NEW: Local Llama 7B
       │ Generate Arguments      │        (70% weight)
       └────────┬────────────────┘
                ▼
       ┌─────────────────────────┐
       │ Blended Scoring         │
       │ 30% Symbolic + 70% LLM  │
       └────────┬────────────────┘
                ▼
       ┌─────────────────────────┐
       │ Jury Decision           │
       │ Final Verdict           │
       └────────┬────────────────┘
                ▼
    ┌──────────────────────────────┐
    │ Report Generation & TTS       │◄────── NEW: Audio Narration
    │ Save to File + MP3/WAV        │        (coqui-tts)
    └──────────────────────────────┘
```

## Verdict Scoring Example

**Case: Simple Assault**

**Symbolic Analysis (Burden of Proof):**
- Prosecution Score: 0.85 (strong assault evidence)
- Defense Score: 0.30 (no applicable defenses detected)
- Difference: 0.55 | Verdict: **NOT GUILTY** (< 0.6 threshold)

**LLM Defense Analysis (with Local Llama):**
- Generated Defense Arguments:
  1. "Mistaken Identity" (Strength: 6/10)
  2. "Self-Defense Claims" (Strength: 5/10)
  3. "Witness Credibility Issues" (Strength: 4/10)
- LLM Augmented Defense Score: 0.45

**Blended Scoring (70% LLM + 30% Symbolic):**
- Symbolic Defense: 0.30 × 0.3 = 0.09
- LLM Defense: 0.45 × 0.7 = 0.315
- **Blended Defense: 0.405**
- New Difference: 0.85 - 0.405 = 0.445
- **REVISED VERDICT: NOT GUILTY** (LLM arguments help defense!)

## Important Notes

### Ollama Setup
- Requires **ollama** running as background service
- Check status: `ollama list`
- Model size: 7B ≈ 4GB RAM, 13B ≈ 8GB RAM
- First inference may take 10-30 seconds while loading model

### TTS Audio Generation
- **coqui-tts**: Best quality (5-10s per verdict), ~500MB model
- **pyttsx3**: Fast fallback (< 1s), slightly robotic
- Audio files saved as `.wav` files (20-50 MB for 5-10 min)

### Backward Compatibility
- All existing scripts work without LLM/TTS enabled
- Default behavior unchanged (symbolic only)
- New features disabled by default via flags

## Troubleshooting

### LLM Not Available
```
⚠ LangChain not installed. LLM defense analysis disabled.
```
**Fix:** `pip install langchain`

### Ollama Connection Failed
```
⚠ LLM initialization failed: failed to connect to ollama
```
**Fix:** 
1. Start ollama: `ollama serve`
2. Pull model: `ollama pull llama2:7b`
3. Verify: `curl localhost:11434/api/tags`

### Audio Generation Failed
```
⚠ No TTS backend available. Audio generation disabled.
```
**Fix:** 
- Install coqui-tts: `pip install TTS`
- Or pyttsx3: `pip install pyttsx3`

### Web Interface Not Loading
```
⚠ Flask app not found. Please ensure app.py exists.
```
**Fix:** Verify `app.py` in current directory

### Out of Memory (Llama)
```
RuntimeError: CUDA out of memory
```
**Fix:** 
- Use smaller model: `llama2:7b` instead of `13b`
- Or disable GPU: `gpu=False` in LLMDefenseAnalyzer
- Or increase system RAM

## Performance Tips

1. **First Run**: LLM loads model (~30s), subsequent runs are faster
2. **Smaller Model**: Use `llama2:7b` for faster inference (~5-10s per case)
3. **Skip LLM**: For quick analysis: `--llm-weight 0.0`
4. **Skip Audio**: Saves ~5-10s per case
5. **Batch Processing**: Analyze multiple cases sequentially to reuse loaded model

## Example Workflow

```bash
# 1. Install all dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 2. Start ollama in background
ollama serve &       # Unix/Linux/Mac
REM or start ollama manually on Windows

# 3. Pull Llama model
ollama pull llama2:7b

# 4. Quick test (symbolic only)
python analyze_case.py sample_case.txt

# 5. Test with LLM enabled
python analyze_case.py sample_case.txt --llm-weight 0.7 --audio

# 6. Launch web interface for interactive analysis
python app.py
# Open http://localhost:5000 in browser

# 7. Analyze your own case
python analyze_case.py my_case.txt --llm-weight 0.7 --audio --theta 0.6
```

## File Structure

```
minors-main/
├── minor.py                    # Core system + LLMDefenseAnalyzer + TTSModule
├── analyze_case.py             # CLI with new flags
├── app.py                      # Flask web application
├── config.py                   # Configuration
├── requirements.txt            # Python dependencies
├── sample_case.txt             # Example case
│
├── templates/
│   ├── index.html              # Upload form
│   ├── verdict.html            # Verdict display
│   ├── 404.html                # Error page
│   └── error.html              # Error page
│
├── static/
│   ├── styles.css              # Web UI styling
│   ├── script.js               # Form handling
│   └── verdict.js              # Verdict display logic
│
├── uploads/                    # User uploaded cases
├── reports/                    # Generated reports
├── audio/                      # Generated audio files
└── temp/                       # Temporary files
```

## Support & Troubleshooting

For issues with:
- **LLM**: Check ollama service and model loading
- **TTS**: Verify system audio permissions
- **Flask**: Check port 5000 availability (`netstat -an | grep 5000`)
- **spaCy**: Verify model installation (`python -m spacy info`)

---

**System Version:** 2.0.0  
**Last Updated:** February 9, 2026  
**Status:** ✅ Complete implementation with LLM + TTS + Web UI
