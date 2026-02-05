#!/usr/bin/env python3
"""
Example script demonstrating the complete legal case analysis system.
Run with: python analyze_case.py <case_file>
"""

import sys
from minor import DocumentParser, analyze_case_document

def main():
    if len(sys.argv) < 2:
        # Use sample case if no argument provided
        case_file = "sample_case.txt"
        print(f"No case file specified. Using {case_file}")
    else:
        case_file = sys.argv[1]
    
    print("\n" + "="*80)
    print("LEGAL CASE ANALYSIS SYSTEM")
    print("="*80 + "\n")
    
    # Load case document
    print(f"[1/5] Loading case document: {case_file}")
    doc = DocumentParser.load_from_file(case_file)
    
    if not doc:
        print("❌ Failed to load case document")
        return
    
    print(f"✓ Case loaded: {doc}")
    
    # Analyze case
    print("\n[2/5] Analyzing case with burden of proof (theta=0.6)...")
    result = analyze_case_document(doc, theta=0.6)
    
    # Print verdicts
    print("\n[3/5] Jury Verdicts:")
    print("-" * 80)
    
    for verdict in result['verdicts']:
        print(f"\nCHARGE: {verdict.charge}")
        print(f"  Verdict: {verdict.verdict}")
        print(f"  Confidence: {verdict.confidence * 100:.1f}%")
        print(f"  Recommendation: {verdict.recommendation}")
        print(f"  Prosecution Score: {verdict.prosecution_score}")
        print(f"  Defense Score: {verdict.defense_score}")
        print(f"  Threshold: {verdict.theta_threshold}")
    
    # Display evidence summary
    print("\n[4/5] Evidence Summary:")
    print("-" * 80)
    
    summary = result['case_summary']
    
    if summary.get('events'):
        print("\nTimeline of Events:")
        for event in summary['events']:
            print(f"  [{event['time']}] {event['event']}")
    
    if summary.get('mitigating_factors'):
        print("\nMitigating Factors:")
        for factor in summary['mitigating_factors']:
            print(f"  • {factor}")
    
    if summary.get('aggravating_factors'):
        print("\nAggravating Factors:")
        for factor in summary['aggravating_factors']:
            print(f"  • {factor}")
    
    # Save detailed report
    print("\n[5/5] Generating comprehensive report...")
    report_path = f"VERDICT_{doc.case_number}.txt"
    result['report_generator'].save_report(report_path)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nDetailed report saved to: {report_path}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    guilty_count = sum(1 for v in result['verdicts'] if v.verdict == "Guilty")
    total_charges = len(result['verdicts'])
    avg_confidence = sum(v.confidence for v in result['verdicts']) / total_charges if result['verdicts'] else 0
    
    print(f"  Total Charges: {total_charges}")
    print(f"  Guilty Verdicts: {guilty_count}")
    print(f"  Not Guilty Verdicts: {total_charges - guilty_count}")
    print(f"  Average Confidence: {avg_confidence * 100:.1f}%")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
