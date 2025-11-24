"""
Stage 2: Generate Newsletter HTML
Takes narrative JSON and creates final HTML email with dark mode support.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def format_percentage(value: float, include_sign: bool = True) -> str:
    """Format percentage with appropriate sign and color class"""
    if include_sign:
        sign = '+' if value > 0 else ''
        return f"{sign}{value:.2f}%"
    return f"{value:.2f}%"

def get_performance_color_class(value: float) -> str:
    """Return CSS class based on performance value"""
    return 'positive' if value >= 0 else ''

def generate_html(narrative_data: Dict[str, Any]) -> str:
    """
    Generate complete HTML email from narrative JSON.
    
    Args:
        narrative_data: Dictionary containing newsletter narrative data
        
    Returns:
        Complete HTML string with dark mode support
    """
    week_num = narrative_data['week_number']
    date_range = narrative_data.get('date_range', '')
    subject = narrative_data['subject_line']
    preheader = narrative_data['preheader']
    opening = narrative_data['opening_paragraph']
    insights = narrative_data['key_insights']
    perf_data = narrative_data['performance_data']
    market_context = narrative_data['market_context']
    benchmark = narrative_data['benchmark_comparison']
    cta_url = narrative_data['call_to_action_url']
    
    # Format performance values
    weekly_change = perf_data['weekly_change']
    total_return = perf_data['total_return']
    weekly_sign = '+' if weekly_change >= 0 else ''
    total_sign = '+' if total_return >= 0 else ''
    
    # Banner color based on performance
    banner_color = '#28a745' if weekly_change >= 0 else '#dc3545'
    
    # Format benchmark percentages
    portfolio_weekly = benchmark['portfolio_weekly']
    sp500_weekly = benchmark['sp500_weekly']
    bitcoin_weekly = benchmark['bitcoin_weekly']
    benchmark_summary = benchmark['summary']
    
    # Format top/worst performer
    top_performer = perf_data['top_performer']
    worst_performer = perf_data['worst_performer']
    
    # Generate insights HTML
    insights_html = []
    for insight in insights:
        insights_html.append(f'''                <div class="insight-card">
                    <h3>{insight['title']}</h3>
                    <p>{insight['description']}</p>
                </div>''')
    
    insights_section = '\n\n'.join(insights_html)
    
    # Complete HTML template with dark mode support
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>{subject}</title>
    <style>
        :root {{
            color-scheme: light dark;
            supported-color-schemes: light dark;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .date-range {{
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .performance-banner {{
            background-color: {banner_color};
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
            font-size: 18px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .preheader {{
            font-size: 14px;
            color: #666;
            font-style: italic;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .opening {{
            font-size: 16px;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        .insights {{
            margin: 30px 0;
        }}
        .insights h2 {{
            font-size: 20px;
            color: #667eea;
            margin-bottom: 20px;
        }}
        .insight-card {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        .insight-card h3 {{
            margin: 0 0 8px 0;
            font-size: 16px;
            color: #333;
        }}
        .insight-card p {{
            margin: 0;
            font-size: 14px;
            color: #555;
        }}
        .performance-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 30px 0;
        }}
        .performance-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .performance-item .ticker {{
            font-weight: 600;
            color: #667eea;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .performance-item .return {{
            font-size: 20px;
            font-weight: 700;
            color: #dc3545;
        }}
        .performance-item .name {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .performance-item.positive .return {{
            color: #28a745;
        }}
        .market-context {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .market-context h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            color: #856404;
        }}
        .market-context p {{
            margin: 0;
            font-size: 14px;
            color: #856404;
            line-height: 1.6;
        }}
        .benchmark-summary {{
            background-color: #e8eaf6;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        .benchmark-summary p {{
            margin: 0;
            font-size: 14px;
            color: #333;
            line-height: 1.6;
        }}
        .cta-button {{
            display: inline-block;
            background-color: #667eea;
            color: white !important;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #eee;
        }}
        .footer a {{
            color: #667eea;
            text-decoration: none;
        }}

        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #e0e0e0;
            }}
            .email-container {{
                background-color: #2d2d2d;
            }}
            .header {{
                background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            }}
            .performance-banner {{
                background-color: {('#16a34a' if weekly_change >= 0 else '#b91c1c')};
            }}
            .content {{
                background-color: #2d2d2d;
            }}
            .preheader {{
                color: #a0a0a0;
                border-bottom: 1px solid #404040;
            }}
            .opening {{
                color: #e0e0e0;
            }}
            .insights h2 {{
                color: #8b9cf6;
            }}
            .insight-card {{
                background-color: #1f1f1f;
                border-left: 4px solid #8b9cf6;
            }}
            .insight-card h3 {{
                color: #e0e0e0;
            }}
            .insight-card p {{
                color: #b0b0b0;
            }}
            .performance-item {{
                background-color: #1f1f1f;
                border: 1px solid #404040;
            }}
            .performance-item .ticker {{
                color: #8b9cf6;
            }}
            .performance-item .return {{
                color: #ef4444;
            }}
            .performance-item .name {{
                color: #a0a0a0;
            }}
            .performance-item.positive .return {{
                color: #34d399;
            }}
            .market-context {{
                background-color: #2a2520;
                border-left: 4px solid #f97316;
            }}
            .market-context h3 {{
                color: #fb923c;
            }}
            .market-context p {{
                color: #d1d5db;
            }}
            .benchmark-summary {{
                background-color: #1e1b3a;
                border-left: 4px solid #8b9cf6;
            }}
            .benchmark-summary p {{
                color: #d1d5db;
            }}
            .cta-button {{
                background-color: #5a67d8;
            }}
            .cta-button:hover {{
                background-color: #4c51bf;
            }}
            .footer {{
                background-color: #1f1f1f;
                color: #a0a0a0;
                border-top: 1px solid #404040;
            }}
            .footer a {{
                color: #8b9cf6 !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <h1>{subject}</h1>
            <p class="date-range">{date_range}</p>
        </div>

        <!-- Performance Banner -->
        <div class="performance-banner">
            Weekly Return: {weekly_sign}{weekly_change:.2f}% | Total Return: {total_sign}{total_return:.2f}%
        </div>

        <!-- Main Content -->
        <div class="content">
            <!-- Preheader -->
            <div class="preheader">
                {preheader}
            </div>

            <!-- Opening Paragraph -->
            <div class="opening">
                {opening}
            </div>

            <!-- Key Insights -->
            <div class="insights">
                <h2>📊 Key Insights</h2>
                
{insights_section}
            </div>

            <!-- Performance Grid - Top/Worst Performers -->
            <h2 style="color: #667eea; margin-top: 30px;">🎯 Performance Highlights</h2>
            <div class="performance-grid">
                <div class="performance-item {get_performance_color_class(top_performer['change'])}">
                    <div class="ticker">{top_performer['ticker']}</div>
                    <div class="return">{format_percentage(top_performer['change'])}</div>
                    <div class="name">Best Performer</div>
                </div>
                <div class="performance-item {get_performance_color_class(worst_performer['change'])}">
                    <div class="ticker">{worst_performer['ticker']}</div>
                    <div class="return">{format_percentage(worst_performer['change'])}</div>
                    <div class="name">Worst Performer</div>
                </div>
            </div>

            <!-- Market Context -->
            <div class="market-context">
                <h3>🌍 Market Context & Outlook</h3>
                <p>{market_context}</p>
            </div>

            <!-- Benchmark Comparison -->
            <h2 style="color: #667eea; margin-top: 30px;">📊 Benchmark Comparison</h2>
            <div class="benchmark-summary">
                <p><strong>Performance Summary:</strong> {benchmark_summary}</p>
            </div>
            <div class="performance-grid" style="grid-template-columns: repeat(3, 1fr);">
                <div class="performance-item {get_performance_color_class(portfolio_weekly)}">
                    <div class="ticker">Portfolio</div>
                    <div class="return">{format_percentage(portfolio_weekly)}</div>
                    <div class="name">Weekly</div>
                </div>
                <div class="performance-item {get_performance_color_class(sp500_weekly)}">
                    <div class="ticker">S&P 500</div>
                    <div class="return">{format_percentage(sp500_weekly)}</div>
                    <div class="name">Weekly</div>
                </div>
                <div class="performance-item {get_performance_color_class(bitcoin_weekly)}">
                    <div class="ticker">Bitcoin</div>
                    <div class="return">{format_percentage(bitcoin_weekly)}</div>
                    <div class="name">Weekly</div>
                </div>
            </div>

            <!-- CTA -->
            <div style="text-align: center;">
                <a href="{cta_url}" class="cta-button">📈 View Full Portfolio Analysis</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>QuantumInvestor Digest</strong></p>
            <p>This newsletter is for informational purposes only and does not constitute investment advice.</p>
            <p><a href="#">Unsubscribe</a> | <a href="#">View in Browser</a></p>
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python generate_newsletter_html.py <week_number>")
        sys.exit(1)
    
    try:
        week_num = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid week number '{sys.argv[1]}'. Must be an integer.")
        sys.exit(1)
    
    # Paths
    base_dir = Path(__file__).parent.parent
    json_path = base_dir / 'newsletters' / f'week{week_num}_narrative.json'
    output_path = base_dir / 'newsletters' / f'week{week_num}_newsletter.html'
    
    # Validate JSON exists
    if not json_path.exists():
        logging.error(f"Narrative JSON not found: {json_path}")
        print(f"❌ Error: {json_path} does not exist.")
        print(f"   Run Stage 1 first: python scripts/generate_newsletter_narrative.py {week_num}")
        sys.exit(1)
    
    # Load narrative data
    logging.info(f"Loading narrative data from {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            narrative_data = json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {json_path}: {e}")
        print(f"❌ Error: Invalid JSON format in {json_path}")
        sys.exit(1)
    
    # Generate HTML
    logging.info(f"Generating HTML for Week {week_num}")
    html_content = generate_html(narrative_data)
    
    # Save HTML
    logging.info(f"Saving HTML to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Success message
    print("\n" + "="*60)
    print("📧 STAGE 2 COMPLETE")
    print("="*60)
    print(f"✅ Newsletter HTML created")
    print(f"📂 Output file: newsletters/week{week_num}_newsletter.html")
    print(f"📝 Subject: {narrative_data['subject_line']}")
    print(f"🎨 Dark mode: Enabled")
    print("\n🔍 NEXT STEPS:")
    print(f"1. Open newsletters/week{week_num}_newsletter.html in browser to preview")
    print(f"2. Test dark mode by switching OS theme")
    print(f"3. Send test email via your email service provider")
    print("="*60)
    
    logging.info("Newsletter generation complete")

if __name__ == "__main__":
    main()
