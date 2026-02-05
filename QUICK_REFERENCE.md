# Quick Reference - Legal Case Analysis System

## 🚀 Get Started in 30 Seconds

```bash
# 1. Run the example
python analyze_case.py sample_case.txt

# Output: VERDICT_2024-CR-005678.txt with complete analysis
```

---

## 💻 Basic Usage

```python
from minor import DocumentParser, analyze_case_document

# Load case
doc = DocumentParser.load_from_file("case.txt")

# Analyze (one function!)
result = analyze_case_document(doc)

# Get verdicts
for v in result['verdicts']:
    print(f"{v.charge}: {v.verdict} ({v.confidence*100:.0f}%)")

# Save report
result['report_generator'].save_report("output.txt")
```

---

## 📄 Case Document Format

```
CASE NUMBER: 2024-CR-001
PLAINTIFF: State
DEFENDANT: John Smith
COURT: District Court
JUDGE: Hon. Judge
DATE FILED: 2024-01-15
LOCATION: County Courthouse
CHARGES: Assault, Battery
NARRATIVE:
[Your case narrative here...]
```

---

## 📊 Output Structure

```python
result = {
    "document": CaseDocument,           # Parsed case
    "facts": [Fact, ...],              # Extracted facts
    "kb": SymbolicKnowledgeBase,       # Knowledge base
    "reasoning_results": Dict,         # Raw reasoning
    "case_summary": Dict,              # Summary details
    "verdicts": [VerdictReasoning, ...], # Verdicts
    "report": str,                     # Full report
    "report_generator": LegalCaseReport # Report object
}
```

---

## 🎯 Access Results

### Verdicts
```python
for v in result['verdicts']:
    print(f"{v.charge}: {v.verdict}")
    print(f"  Confidence: {v.confidence*100:.1f}%")
    print(f"  Recommendation: {v.recommendation}")
```

### Evidence
```python
summary = result['case_summary']
print("Mitigating:", summary['mitigating_factors'])
print("Aggravating:", summary['aggravating_factors'])
```

### Raw Data
```python
print("Facts:", result['facts'])
print("KB Facts:", result['kb'].facts)
print("Reasoning:", result['reasoning_results'])
```

---

## ⚙️ Customize Analysis

```python
# Stricter (need more evidence)
result = analyze_case_document(doc, theta=0.8)

# More lenient
result = analyze_case_document(doc, theta=0.4)

# Specific charges
result = analyze_case_document(
    doc, 
    charges_to_evaluate=["Theft", "Fraud"]
)
```

---

## 📁 File Structure

```
├── minor.py                     # Main system
├── analyze_case.py              # Example script
├── sample_case.txt              # Sample case
├── README.md                    # Overview
├── USAGE_GUIDE.md              # Complete API
├── EXPANSION_GUIDE.md          # Extension guide
├── FEATURES_SUMMARY.md         # Features
├── IMPLEMENTATION_SUMMARY.md   # Technical
└── COMPLETION_CHECKLIST.md     # Verification
```

---

## 🔑 Key Functions

| Function | Purpose |
|----------|---------|
| `DocumentParser.load_from_file()` | Load case from file |
| `DocumentParser.parse_text_document()` | Parse from string |
| `analyze_case_document()` | Complete analysis |
| `run_system()` | Legacy text analysis |

---

## 📋 Supported Charges

1. Assault
2. Aggravated Assault
3. Assault on Minor
4. Battery
5. Theft
6. Fraud
7. Murder

---

## 💡 Common Tasks

### Load and Analyze
```python
from minor import DocumentParser, analyze_case_document

doc = DocumentParser.load_from_file("case.txt")
result = analyze_case_document(doc)
```

### Get Verdict Summary
```python
for v in result['verdicts']:
    print(f"{v.charge}: {v.verdict}")
```

### Save Report
```python
result['report_generator'].save_report("report.txt")
```

### Adjust Threshold
```python
result = analyze_case_document(doc, theta=0.7)
```

### Add Custom Rule
```python
from minor import Rule

kb = result['kb']
kb.add_rule(Rule(
    charge="Theft",
    premises=["Theft(X,Y)"],
    weight=0.9,
    side="prosecution",
    name="Direct Evidence",
    description="Defendant stole property"
))
```

---

## 🧠 How It Works

```
Case Document
    ↓ Parse
Case Metadata + Narrative
    ↓ Extract
Facts with Confidence
    ↓ Ground
Symbolic Knowledge Base
    ↓ Reason
Prosecution vs Defense Scores
    ↓ Decide
Verdicts with Confidence
    ↓ Summarize
Complete Legal Report
    ↓ Save
Text File Output
```

---

## ⚠️ Confidence Levels

| Range | Meaning |
|-------|---------|
| 0.8-1.0 | Strong Evidence |
| 0.5-0.8 | Moderate Evidence |
| 0.3-0.5 | Weak Evidence |
| <0.3 | Insufficient Evidence |

---

## 🔧 Extend System

### Add New Charge

1. Add to `SymbolicKnowledgeBase._initialize_charges()`
2. Add verbs to `NeuralPerceptionModule.actions`
3. Add rules in `analyze_case_document()`

See EXPANSION_GUIDE.md for details.

---

## 📚 Documentation

- **README.md** - Start here
- **USAGE_GUIDE.md** - Complete API
- **EXPANSION_GUIDE.md** - Extend system
- **IMPLEMENTATION_SUMMARY.md** - Technical details

---

## ❓ Troubleshooting

### No facts extracted
- Check narrative contains action verbs
- Verify subject/object are clear
- Try improving entity recognition

### Low confidence
- Add more evidence to narrative
- Verify rule weights
- Adjust theta threshold

### File not found
- Check file path
- Use absolute paths
- Verify file format

---

## 🎯 Next Steps

1. **Run example**: `python analyze_case.py sample_case.txt`
2. **Create case**: Follow format in `sample_case.txt`
3. **Analyze**: Use `analyze_case_document()`
4. **Review**: Check generated report
5. **Extend**: Add custom rules/charges

---

## 💬 Python Example

```python
from minor import DocumentParser, analyze_case_document

# Load
doc = DocumentParser.load_from_file("sample_case.txt")

# Analyze
result = analyze_case_document(doc, theta=0.6)

# Print verdicts
print("VERDICTS:")
for v in result['verdicts']:
    print(f"  {v.charge}: {v.verdict}")
    print(f"    Confidence: {v.confidence*100:.1f}%")
    print(f"    Recommendation: {v.recommendation}\n")

# Save report
result['report_generator'].save_report("verdict.txt")
print("Report saved!")
```

---

## 📞 Support

| Topic | File |
|-------|------|
| Overview | README.md |
| Usage | USAGE_GUIDE.md |
| Extending | EXPANSION_GUIDE.md |
| Technical | IMPLEMENTATION_SUMMARY.md |
| AI Agent | .github/copilot-instructions.md |

---

**System is ready! Start with `python analyze_case.py sample_case.txt` 🚀**
