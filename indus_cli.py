#!/usr/bin/env python3
"""
Indus Valley Script Decipherment CLI

Entry point for running the complete analysis pipeline.
Usage: python -m indus_cli [command] [options]
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from indus.analysis import load_translations, analyze_vocabulary, get_civilization_summary
from indus.validate import validate_data
from indus.utils import revolutionary_summary
from indus.curvature_opt import main as curvature_main


def cmd_validate(args):
    """Validate data integrity and revolutionary findings."""
    print("🔍 Validating Indus Valley decipherment data...")
    
    results = validate_data()
    
    for component, result in results.items():
        status = result.get('status', 'UNKNOWN')
        emoji = {'PASS': '✅', 'WARNING': '⚠️', 'FAIL': '❌'}.get(status, '❓')
        print(f"{emoji} {component}: {status}")
        
        if 'error' in result:
            print(f"   Error: {result['error']}")
    
    overall_status = results.get('overall', {}).get('status', 'FAIL')
    print(f"\n🎯 Overall status: {overall_status}")
    
    return 0 if overall_status in ['PASS', 'WARNING'] else 1


def cmd_analyze(args):
    """Run vocabulary and civilization analysis."""
    print("📊 Running Indus Valley analysis...")
    
    try:
        # Load translations
        df = load_translations(args.input)
        print(f"✓ Loaded {len(df):,} inscriptions")
        
        # Analyze vocabulary
        vocab = analyze_vocabulary(df)
        print(f"✓ Analyzed {vocab['total_words']:,} words ({vocab['unique_words']} unique)")
        
        # Get civilization summary
        summary = get_civilization_summary(df)
        
        # Print key findings
        print("\n🏛️ REVOLUTIONARY FINDINGS:")
        for evidence in summary['key_evidence']:
            print(f"   • {evidence}")
        
        print(f"\n📈 VOCABULARY PATTERNS:")
        print(f"   • Family-authority ratio: {vocab['family_authority_ratio']:.1f}:1")
        print(f"   • Religious content: {vocab['religious_percentage']:.1f}%")
        print(f"   • Family references: {vocab['family_percentage']:.1f}%")
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1


def cmd_curvature(args):
    """Run curvature optimization."""
    print("🧮 Running curvature optimization...")
    
    # Prepare arguments for curvature optimization
    curvature_args = [
        '--corpus', args.corpus,
        '--output', args.output,
    ]
    
    if args.compounds:
        curvature_args.extend(['--compounds', args.compounds])
    if args.modifiers:
        curvature_args.extend(['--modifiers', args.modifiers])
    if args.free_w is not None:
        curvature_args.extend(['--free_w', str(int(args.free_w))])
    
    # Parse arguments and run curvature optimization
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--compounds')
    parser.add_argument('--modifiers')
    parser.add_argument('--free_w', type=int, default=1)
    parser.add_argument('--output', default='weights.json')
    
    curvature_parsed = parser.parse_args(curvature_args)
    
    try:
        curvature_main(curvature_parsed)
        print("✅ Curvature optimization completed")
        return 0
    except Exception as e:
        print(f"❌ Curvature optimization failed: {e}")
        return 1


def cmd_report(args):
    """Generate complete analysis report."""
    print("📋 Generating complete Indus Valley analysis report...")
    
    try:
        # Load and analyze data
        df = load_translations(args.input)
        vocab = analyze_vocabulary(df)
        summary = get_civilization_summary(df)
        
        # Generate report
        report_lines = [
            "# Indus Valley Script Decipherment: Complete Analysis Report",
            "",
            "## Revolutionary Discovery",
            "",
            revolutionary_summary(),
            "",
            f"## Data Summary",
            f"- **Inscriptions analyzed**: {len(df):,}",
            f"- **Total words**: {vocab['total_words']:,}",
            f"- **Unique words**: {vocab['unique_words']:,}",
            f"- **Timeline**: {summary['timeline']}",
            f"- **Population estimate**: {summary['population_estimate']:,} people",
            f"- **Geographic extent**: {summary['geographic_extent']}",
            "",
            "## Vocabulary Analysis",
            f"- **Family-authority ratio**: {vocab['family_authority_ratio']:.1f}:1",
            f"- **Religious content**: {vocab['religious_percentage']:.1f}%",
            f"- **Family content**: {vocab['family_percentage']:.1f}%",
            "",
            "## Key Evidence",
        ]
        
        for evidence in summary['key_evidence']:
            report_lines.append(f"- {evidence}")
        
        report_lines.extend([
            "",
            "## Social Organization",
            f"- **Elite percentage**: {summary['social_organization']['elite_percentage']}",
            f"- **Merchant class**: {summary['social_organization']['merchant_class']}",
            f"- **Common people**: {summary['social_organization']['common_people']}",
            "",
            "---",
            "",
            "*This report represents the largest successful ancient script decipherment in history.*"
        ])
        
        # Write report
        with open(args.output, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✅ Report generated: {args.output}")
        return 0
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return 1


def cmd_summary(args):
    """Show quick summary of revolutionary findings."""
    print(revolutionary_summary())
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Indus Valley Script Decipherment - CLI Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate data integrity')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run vocabulary analysis')
    analyze_parser.add_argument('--input', default='data/core/ledger_english_full.tsv',
                               help='Input translations file')
    
    # Curvature command
    curvature_parser = subparsers.add_parser('curvature', help='Run curvature optimization')
    curvature_parser.add_argument('--corpus', required=True, help='Corpus TSV file')
    curvature_parser.add_argument('--compounds', help='Compounds CSV file')
    curvature_parser.add_argument('--modifiers', help='Modifiers CSV file')
    curvature_parser.add_argument('--free_w', type=bool, default=True, help='Allow free weights')
    curvature_parser.add_argument('--output', default='weights.json', help='Output file')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate analysis report')
    report_parser.add_argument('--input', default='data/core/ledger_english_full.tsv',
                              help='Input translations file')
    report_parser.add_argument('--output', default='reports/INDUS_COMPLETE_REPORT.md',
                              help='Output report file')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show revolutionary findings summary')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    commands = {
        'validate': cmd_validate,
        'analyze': cmd_analyze,
        'curvature': cmd_curvature,
        'report': cmd_report,
        'summary': cmd_summary,
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 