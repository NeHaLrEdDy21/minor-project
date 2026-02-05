# Legal Case Analysis System

A **Neuro-Symbolic AI** system that analyzes legal case documents and generates comprehensive jury verdict reports with confidence levels and detailed reasoning.

## ✨ Features

### Document Analysis
- **Load case documents** from text files or string input
- **Structured parsing** of case metadata (plaintiff, defendant, charges, court info)
- **Flexible narrative** analysis supporting complex multi-party cases

### Intelligent Fact Extraction
- **Neural extraction** using spacy NLP for dependency parsing
- **Entity recognition** for persons, weapons, property, status markers
- **Temporal reasoning** for self-defense and evidence ordering
- **Confidence scoring** for each extracted fact

### Legal Reasoning Engine
- **Burden of proof** calculation with configurable threshold (theta)
- **Dual-sided reasoning** with prosecution and defense arguments
- **Rule-based inference** with weighted evidence
- **Automatic charge evaluation** for applicable charges

### Jury Decision System
- **Verdict determination** per charge
- **Confidence levels** based on evidence strength
- **Smart recommendations** (Guilty, Not Guilty, Insufficient Evidence)
- **Detailed justification** with prosecution/defense scoring

### Comprehensive Reporting
- **Professional case summaries** with chronological timeline
- **Evidence analysis** (actus reus, mens rea, circumstantial)
- **Mitigating and aggravating factors** extraction
- **Full verdict reports** saved to text files

---

## 🚀 Quick Start

### Installation
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Analyze a Case

**From file:**
```python
from minor import DocumentParser, analyze_case_document

doc = DocumentParser.load_from_file("case.txt")
result = analyze_case_document(doc, theta=0.6)

for verdict in result['verdicts']:
    print(f"{verdict.charge}: {verdict.verdict} ({verdict.confidence*100:.1f}%)")

result['report_generator'].save_report("verdict.txt")
```

**From string:**
```python
case_text = """CASE NUMBER: 2024-001
PLAINTIFF: State
DEFENDANT: John Doe
COURT: District Court
JUDGE: Hon. Judge
DATE FILED: 2024-01-15
NARRATIVE:
John attacked Mary, a minor, without provocation."""

doc = DocumentParser.parse_text_document(case_text)
result = analyze_case_document(doc)
```

### Using the Example Script
```bash
python analyze_case.py sample_case.txt
```

---

## 📋 Case Document Format

```
CASE NUMBER: [identifier]
PLAINTIFF: [name1, name2]
DEFENDANT: [name1, name2]
COURT: [court name]
JUDGE: [judge name]
DATE FILED: [date]
LOCATION: [location]
CHARGES: [charge1, charge2]
NARRATIVE:
[Case narrative describing events, evidence, timeline...]
```

**Example:** See [sample_case.txt](sample_case.txt)

---

## 📊 Output Structure

### Verdicts with Confidence
```
Charge: Theft
  Verdict: Guilty
  Confidence: 92.5%
  Recommendation: Guilty (Strong Evidence)
  Prosecution Score: 0.925
  Defense Score: 0.0
```

### Complete Report
Generated report includes:
- Case details and parties
- Chronological timeline
- Evidence analysis
- Mitigating/aggravating factors
- Jury verdict per charge
- Legal methodology
- Recommendations

---

## 🧠 System Architecture

```
Document Loading
      ↓
Neural Extraction (spacy NLP)
      ↓
Symbolic Grounding (Facts → Rules)
      ↓
Burden of Proof Reasoning
      ↓
Jury Decision (Verdicts + Confidence)
      ↓
Report Generation
      ↓
Text File Output
```

### Layers

1. **Neural Layer**: Extracts facts using spacy dependency parsing
2. **Symbolic Layer**: Grounds facts in knowledge base with inference rules
3. **Reasoning Layer**: Evaluates charges using burden of proof
4. **Decision Layer**: Determines verdicts with confidence scores
5. **Reporting Layer**: Generates comprehensive legal analysis

---

## 🎯 Supported Charges

- **Assault** - Intentional act causing apprehension of harm
- **Aggravated Assault** - Assault with weapon or serious injury
- **Battery** - Intentional physical contact
- **Assault on Minor** - Assault against person under 18
- **Theft** - Unlawful taking of property
- **Fraud** - Intentional misrepresentation
- **Murder** - Unlawful killing

Easily extensible to add more charges.

---

## ⚙️ Customization

### Adjust Burden of Proof
```python
# Stricter (require more evidence)
result = analyze_case_document(doc, theta=0.8)

# More lenient
result = analyze_case_document(doc, theta=0.4)
```

### Evaluate Specific Charges
```python
result = analyze_case_document(doc, charges_to_evaluate=["Theft", "Fraud"])
```

### Add Custom Rules
```python
from minor import Rule

kb.add_rule(Rule(
    charge="Theft",
    premises=["Theft(X,Y)", "Premeditation(X)"],
    weight=1.0,
    side="prosecution",
    name="Premeditated Theft",
    description="Evidence shows planning"
))
```

---

## 📚 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete API reference and examples
- **[EXPANSION_GUIDE.md](EXPANSION_GUIDE.md)** - Guide for extending the system
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent instructions

---

## 🔧 Project Structure

```
├── minor.py                          # Main system
├── analyze_case.py                   # Example script
├── sample_case.txt                   # Sample case document
├── USAGE_GUIDE.md                    # Complete usage guide
├── EXPANSION_GUIDE.md                # Extension guide
├── neuro_symbolic_abstrat.ipynb      # Iterative exploration
└── .github/copilot-instructions.md   # AI agent instructions
```

---

## 📈 How It Works

### 1. Document Parsing
Loads case document and extracts metadata (parties, charges, date, etc.)

### 2. Fact Extraction
Uses spacy NLP to extract actions (assault, theft, etc.) and entities (persons, weapons, property)

### 3. Knowledge Base Construction
Grounds extracted facts in symbolic knowledge base with confidence scores

### 4. Legal Reasoning
Applies inference rules with burden of proof logic:
- Score = min(premise_confidences) × rule_weight
- Verdict = Guilty if (prosecution_score - defense_score) ≥ theta

### 5. Confidence Calculation
Confidence = min(1.0, |difference| / theta)
- Higher confidence indicates clearer verdict
- Lower confidence indicates weak/insufficient evidence

### 6. Report Generation
Creates comprehensive report with all findings, verdicts, and justification

---

## 🎓 Example Verdict Report

```
CHARGE: Theft
────────────────────────────────────────────────────────
  Verdict: Guilty
  Recommendation: Guilty (Strong Evidence)
  Confidence Level: 92.5%
  
  Prosecution Score: 0.925
  Defense Score: 0.0
  Difference: 0.925
  Threshold: 0.6

  PROSECUTION ARGUMENTS:
    • Direct Evidence: 0.925 (weight: 1.0)
       Defendant stole $8,500 in cash
    • Premeditation: 0.85 (weight: 0.95)
       Defendant had prior knowledge of valuables

  DEFENSE ARGUMENTS:
    [None provided]
```

---

## ⚠️ Important Notes

- This system is designed for educational and reference purposes
- Actual legal proceedings require qualified legal representation
- Verdicts are analytical conclusions based on provided evidence
- Real court decisions are made by judges/juries with full legal authority
- The system's confidence reflects evidence consistency, not legal validity

---

## 🔄 Requirements

- Python 3.10+
- spacy library with en_core_web_sm model
- (Note: Python 3.14 currently incompatible due to spacy/pydantic issues)

---

## 📝 License

Educational project for legal AI reasoning research.

---

## 🤝 Contributing

To extend the system:

1. Add new charges to `SymbolicKnowledgeBase._initialize_charges()`
2. Add action verbs to `NeuralPerceptionModule.actions`
3. Add inference rules in `analyze_case_document()`
4. Test with sample cases

See [EXPANSION_GUIDE.md](EXPANSION_GUIDE.md) for detailed instructions.

---

## 📧 Support

For usage questions, see [USAGE_GUIDE.md](USAGE_GUIDE.md)

For technical details, see [.github/copilot-instructions.md](.github/copilot-instructions.md)

For extension guide, see [EXPANSION_GUIDE.md](EXPANSION_GUIDE.md)
