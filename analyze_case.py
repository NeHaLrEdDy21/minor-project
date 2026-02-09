#!/usr/bin/env python3
"""
Example script demonstrating the complete legal case analysis system.

Usage:
  python analyze_case.py <case_file>                           # Basic analysis
  python analyze_case.py <case_file> --audio                   # Generate verdict audio
  python analyze_case.py <case_file> --llm-weight 0.7 --audio  # With LLM defense analysis and audio
  python analyze_case.py <case_file> --web                     # Launch web interface

For full help: python analyze_case.py --help
"""

import sys
import argparse
from pathlib import Path
from minor import DocumentParser, analyze_case_document, LANGCHAIN_AVAILABLE, COQUI_AVAILABLE, PYTTSX3_AVAILABLE

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Legal Case Analysis System - Neuro-Symbolic AI with LLM Defense Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic symbolic analysis only
  python analyze_case.py sample_case.txt
  
  # With LLM-powered defense arguments (70% LLM weight, 30% symbolic)
  python analyze_case.py sample_case.txt --llm-weight 0.7 --llm-model llama2
  
  # Generate audio verdict narration
  python analyze_case.py sample_case.txt --audio
  
  # Combined: LLM defense + audio + web interface
  python analyze_case.py sample_case.txt --llm-weight 0.7 --audio --web
  
  # Custom burden of proof threshold (60% default)
  python analyze_case.py sample_case.txt --theta 0.4
  
  # Launch web interface only (interactive upload)
  python analyze_case.py --web
        """
    )
    
    parser.add_argument(
        "case_file",
        nargs="?",
        default="sample_case.txt",
        help="Path to case document file (default: sample_case.txt)"
    )
    
    parser.add_argument(
        "--llm-weight",
        type=float,
        default=0.7,
        help="LLM weight in verdict scoring (0.0-1.0; default: 0.7 = 70%% LLM, 30%% symbolic)"
    )
    
    parser.add_argument(
        "--llm-model",
        type=str,
        default="llama2",
        help="Llama model name for LLM analysis (default: llama2). Requires ollama running."
    )
    
    parser.add_argument(
        "--audio",
        action="store_true",
        help="Generate audio file for verdict (requires TTS backend: coqui or pyttsx3)"
    )
    
    parser.add_argument(
        "--theta",
        type=float,
        default=0.6,
        help="Burden of proof threshold (default: 0.6 = 60%% prosecution advantage needed)"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch interactive web interface at http://localhost:5000"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for web interface (default: 5000)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed reasoning steps"
    )
    
    return parser

def check_dependencies():
    """Check for required dependencies and warn if missing"""
    warnings = []
    
    if not LANGCHAIN_AVAILABLE:
        warnings.append("⚠ LangChain not installed. LLM defense analysis disabled.")
        warnings.append("   Install with: pip install langchain")
    
    if not COQUI_AVAILABLE and not PYTTSX3_AVAILABLE:
        warnings.append("⚠ No TTS backend detected. Audio generation disabled.")
        warnings.append("   Install coqui-tts: pip install TTS")
        warnings.append("   Or pyttsx3: pip install pyttsx3")
    
    for warning in warnings:
        print(warning)
    
    if warnings:
        print()

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    # Handle web mode
    if args.web:
        print("Launching web interface...")
        try:
            from app import create_app
            app = create_app()
            print(f"\n{'='*80}")
            print(f"Web interface running at: http://localhost:{args.port}")
            print(f"{'='*80}\n")
            app.run(debug=False, port=args.port, host="127.0.0.1")
        except ImportError:
            print("❌ Flask app not found. Please ensure app.py exists in the workspace.")
            return
        except Exception as e:
            print(f"❌ Error launching web interface: {e}")
            return
    
    # Handle file analysis mode
    case_file = args.case_file
    
    # Validate case file
    if not Path(case_file).exists():
        print(f"❌ Case file not found: {case_file}")
        print(f"   Please provide a valid case document path")
        return
    
    print("\n" + "="*80)
    print("LEGAL CASE ANALYSIS SYSTEM")
    print("="*80 + "\n")
    
    # Load case document
    print(f"[1/6] Loading case document: {case_file}")
    doc = DocumentParser.load_from_file(case_file)
    
    if not doc:
        print("❌ Failed to load case document")
        return
    
    print(f"✓ Case loaded: {doc}")
    
    # Show configuration
    print(f"\n[2/6] Configuration:")
    print(f"  Burden of Proof Threshold (θ): {args.theta}")
    print(f"  LLM Weight: {int(args.llm_weight*100)}% (Symbolic: {int((1-args.llm_weight)*100)}%)")
    if args.llm_weight > 0:
        print(f"  LLM Model: {args.llm_model}")
    print(f"  Audio Generation: {'✓ Enabled' if args.audio else '✗ Disabled'}")
    
    # Analyze case
    print(f"\n[3/6] Analyzing case with burden of proof...")
    result = analyze_case_document(
        doc,
        theta=args.theta,
        llm_weight=args.llm_weight if LANGCHAIN_AVAILABLE and args.llm_weight > 0 else 0.0,
        llm_model=args.llm_model,
        enable_audio=args.audio and (COQUI_AVAILABLE or PYTTSX3_AVAILABLE),
        audio_output=f"VERDICT_{doc.case_number}_AUDIO.wav" if args.audio else None
    )
    
    # Print verdicts
    print(f"\n[4/6] Jury Verdicts:")
    print("-" * 80)
    
    for verdict in result['verdicts']:
        print(f"\nCHARGE: {verdict.charge}")
        print(f"  Verdict: {verdict.verdict}")
        print(f"  Confidence: {verdict.confidence * 100:.1f}%")
        print(f"  Recommendation: {verdict.recommendation}")
        print(f"  Prosecution Score: {verdict.prosecution_score:.3f}")
        print(f"  Defense Score: {verdict.defense_score:.3f}")
        print(f"  Threshold: {verdict.theta_threshold}")
        
        # Show if verdict changed due to LLM
        if hasattr(result['reasoning_results'][verdict.charge], '__getitem__'):
            reasoning = result['reasoning_results'][verdict.charge]
            if reasoning.get('verdict_original') and reasoning['verdict_original'] != verdict.verdict:
                print(f"  ► CHANGED: {reasoning['verdict_original']} → {verdict.verdict} (LLM analysis)")
    
    # Display evidence summary
    print(f"\n[5/6] Evidence Summary:")
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
    
    # Display LLM defense arguments if available
    if args.llm_weight > 0 and result.get('defense_analyses'):
        print("\nLLM-Generated Defense Arguments:")
        for charge, analysis in result['defense_analyses'].items():
            if analysis and analysis.generated_arguments:
                print(f"  {charge}:")
                for arg in analysis.generated_arguments[:3]:  # Show top 3
                    print(f"    • {arg['name']} (Strength: {arg['strength']}/10)")
                    print(f"      {arg['description']}")
    
    # Save detailed report
    print(f"\n[6/6] Generating comprehensive report...")
    report_path = f"VERDICT_{doc.case_number}.txt"
    result['report_generator'].save_report(report_path)
    
    # Generate audio if requested
    audio_path = None
    if args.audio and (COQUI_AVAILABLE or PYTTSX3_AVAILABLE):
        print("Generating verdict audio (this may take a moment)...")
        audio_path = result['report_generator'].generate_verdict_audio()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nDetailed report saved to: {report_path}")
    if audio_path:
        print(f"Verdict audio saved to: {audio_path}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    guilty_count = sum(1 for v in result['verdicts'] if v.verdict == "Guilty")
    total_charges = len(result['verdicts'])
    avg_confidence = sum(v.confidence for v in result['verdicts']) / total_charges if result['verdicts'] else 0
    
    print(f"  Total Charges: {total_charges}")
    print(f"  Guilty Verdicts: {guilty_count}")
    print(f"  Not Guilty Verdicts: {total_charges - guilty_count}")
    print(f"  Average Confidence: {avg_confidence * 100:.1f}%")
    
    if args.llm_weight > 0 and LANGCHAIN_AVAILABLE:
        print(f"  LLM Weighting: {int(args.llm_weight*100)}%")
        changed_count = sum(
            1 for charge, reasoning in result['reasoning_results'].items()
            if reasoning.get('verdict_original') and reasoning['verdict_original'] != reasoning['verdict']
        )
        if changed_count > 0:
            print(f"  Verdicts Changed by LLM: {changed_count}/{total_charges}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
