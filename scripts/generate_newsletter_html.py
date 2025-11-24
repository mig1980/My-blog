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
    
    # Determine banner gradient based on performance
    banner_gradient = 'linear-gradient(90deg, #16a34a 0%, #22c55e 100%)' if weekly_change >= 0 else 'linear-gradient(90deg, #991b1b 0%, #dc2626 100%)'
    banner_border = 'rgba(34, 197, 94, 0.3)' if weekly_change >= 0 else 'rgba(220, 38, 38, 0.3)'
    
    # Format date range for display
    formatted_date = date_range.replace('to', '–')
    
    # Complete HTML template with modern professional design
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #E0E0E0;
            background-color: #000000;
            padding: 40px 20px;
        }}
        
        .email-container {{
            max-width: 680px;
            margin: 0 auto;
            background-color: #111111;
            border: 1px solid #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .header {{
            position: relative;
            background: linear-gradient(135deg, #3b0764 0%, #7c3aed 50%, #a855f7 100%);
            padding: 48px 32px;
            text-align: center;
            border-bottom: 1px solid rgba(168, 85, 247, 0.3);
        }}
        
        .logo {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 16px;
            font-weight: 600;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 12px;
            line-height: 1.2;
        }}
        
        .date-range {{
            font-size: 14px;
            color: rgba(255, 255, 255, 0.75);
            letter-spacing: 0.02em;
        }}
        
        .performance-banner {{
            background: {banner_gradient};
            padding: 20px 32px;
            text-align: center;
            border-bottom: 1px solid {banner_border};
        }}
        
        .performance-banner-content {{
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 0.01em;
        }}
        
        .content {{
            padding: 40px 32px;
            background-color: #111111;
        }}
        
        .preheader {{
            font-size: 15px;
            color: #9ca3af;
            font-style: italic;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid #1a1a1a;
        }}
        
        .opening {{
            font-size: 16px;
            line-height: 1.75;
            color: #E0E0E0;
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 22px;
            font-weight: 700;
            color: #a855f7;
            margin: 40px 0 24px 0;
            letter-spacing: -0.02em;
        }}
        
        .insights {{
            margin: 32px 0;
        }}
        
        .insight-card {{
            background: rgba(168, 85, 247, 0.05);
            border-left: 3px solid #a855f7;
            padding: 20px;
            margin-bottom: 16px;
            border-radius: 8px;
            transition: transform 0.2s ease, background 0.2s ease;
        }}
        
        .insight-card:hover {{
            background: rgba(168, 85, 247, 0.08);
            transform: translateX(2px);
        }}
        
        .insight-card h3 {{
            font-size: 17px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 8px;
        }}
        
        .insight-card p {{
            font-size: 15px;
            color: #9ca3af;
            line-height: 1.6;
        }}
        
        .performance-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin: 32px 0;
        }}
        
        .performance-grid.three-col {{
            grid-template-columns: repeat(3, 1fr);
        }}
        
        .performance-item {{
            background-color: #1a1a1a;
            border: 1px solid #222222;
            padding: 24px 20px;
            border-radius: 8px;
            text-align: center;
            transition: border-color 0.2s ease, transform 0.2s ease;
        }}
        
        .performance-item:hover {{
            border-color: #a855f7;
            transform: translateY(-2px);
        }}
        
        .performance-item .ticker {{
            font-weight: 700;
            color: #a855f7;
            font-size: 15px;
            margin-bottom: 8px;
            letter-spacing: 0.05em;
        }}
        
        .performance-item .return {{
            font-size: 26px;
            font-weight: 700;
            color: #ef4444;
            margin: 8px 0;
        }}
        
        .performance-item.positive .return {{
            color: #4ade80;
        }}
        
        .performance-item .name {{
            font-size: 13px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 8px;
        }}
        
        .market-context {{
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(168, 85, 247, 0.03) 100%);
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 8px;
            padding: 24px;
            margin: 32px 0;
        }}
        
        .market-context h3 {{
            font-size: 17px;
            font-weight: 600;
            color: #a855f7;
            margin-bottom: 12px;
        }}
        
        .market-context p {{
            font-size: 15px;
            color: #9ca3af;
            line-height: 1.7;
        }}
        
        .benchmark-summary {{
            background-color: #1a1a1a;
            border-left: 3px solid #a855f7;
            padding: 20px;
            margin: 24px 0;
            border-radius: 6px;
        }}
        
        .benchmark-summary p {{
            font-size: 15px;
            color: #9ca3af;
            line-height: 1.7;
        }}
        
        .benchmark-summary strong {{
            color: #E0E0E0;
        }}
        
        .cta-container {{
            text-align: center;
            margin: 40px 0 32px 0;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
            color: #ffffff !important;
            padding: 16px 40px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            letter-spacing: 0.01em;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
        }}
        
        .footer {{
            background-color: #000000;
            border-top: 1px solid #1a1a1a;
            padding: 32px;
            text-align: center;
        }}
        
        .footer-brand {{
            font-size: 16px;
            font-weight: 600;
            color: #a855f7;
            margin-bottom: 12px;
            letter-spacing: 0.02em;
        }}
        
        .footer-text {{
            font-size: 13px;
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 16px;
        }}
        
        .footer-links {{
            font-size: 13px;
        }}
        
        .footer-links a {{
            color: #9ca3af;
            text-decoration: none;
            transition: color 0.2s ease;
        }}
        
        .footer-links a:hover {{
            color: #a855f7;
        }}
        
        .divider {{
            color: #6b7280;
            margin: 0 8px;
        }}
        
        /* Light Mode Support */
        @media (prefers-color-scheme: light) {{
            body {{
                background-color: #f5f5f5;
                color: #1a1a1a;
            }}
            
            .email-container {{
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
            }}
            
            .header {{
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            }}
            
            .performance-banner {{
                background: {'linear-gradient(90deg, #16a34a 0%, #22c55e 100%)' if weekly_change >= 0 else 'linear-gradient(90deg, #dc2626 0%, #ef4444 100%)'};
                border-bottom: 1px solid {'rgba(34, 197, 94, 0.3)' if weekly_change >= 0 else 'rgba(239, 68, 68, 0.3)'};
            }}
            
            .content {{
                background-color: #ffffff;
            }}
            
            .preheader {{
                color: #6b7280;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            .opening {{
                color: #1f2937;
            }}
            
            .section-title {{
                color: #7c3aed;
            }}
            
            .insight-card {{
                background: rgba(124, 58, 237, 0.05);
                border-left: 3px solid #7c3aed;
            }}
            
            .insight-card h3 {{
                color: #111827;
            }}
            
            .insight-card p {{
                color: #4b5563;
            }}
            
            .performance-item {{
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
            }}
            
            .performance-item:hover {{
                border-color: #7c3aed;
            }}
            
            .performance-item .ticker {{
                color: #7c3aed;
            }}
            
            .performance-item .return {{
                color: #dc2626;
            }}
            
            .performance-item.positive .return {{
                color: #16a34a;
            }}
            
            .performance-item .name {{
                color: #6b7280;
            }}
            
            .market-context {{
                background: linear-gradient(135deg, rgba(124, 58, 237, 0.08) 0%, rgba(124, 58, 237, 0.03) 100%);
                border: 1px solid rgba(124, 58, 237, 0.2);
            }}
            
            .market-context h3 {{
                color: #7c3aed;
            }}
            
            .market-context p {{
                color: #4b5563;
            }}
            
            .benchmark-summary {{
                background-color: #f9fafb;
                border-left: 3px solid #7c3aed;
            }}
            
            .benchmark-summary p {{
                color: #4b5563;
            }}
            
            .benchmark-summary strong {{
                color: #111827;
            }}
            
            .cta-button {{
                background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
                box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
            }}
            
            .cta-button:hover {{
                box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4);
            }}
            
            .footer {{
                background-color: #f9fafb;
                border-top: 1px solid #e5e7eb;
            }}
            
            .footer-brand {{
                color: #7c3aed;
            }}
            
            .footer-text {{
                color: #6b7280;
            }}
            
            .footer-links a {{
                color: #6b7280;
            }}
            
            .footer-links a:hover {{
                color: #7c3aed;
            }}
            
            .divider {{
                color: #9ca3af;
            }}
        }}
        
        @media (max-width: 640px) {{
            body {{
                padding: 20px 12px;
            }}
            
            .email-container {{
                border-radius: 8px;
            }}
            
            .header {{
                padding: 32px 20px;
            }}
            
            .header h1 {{
                font-size: 22px;
            }}
            
            .performance-banner {{
                padding: 16px 20px;
            }}
            
            .performance-banner-content {{
                font-size: 16px;
            }}
            
            .content {{
                padding: 28px 20px;
            }}
            
            .section-title {{
                font-size: 20px;
            }}
            
            .performance-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            
            .performance-grid.three-col {{
                grid-template-columns: 1fr;
            }}
            
            .cta-button {{
                padding: 14px 32px;
                font-size: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Quantum Investor Digest</div>
            <h1>{subject}</h1>
            <p class="date-range">{formatted_date}</p>
        </div>

        <!-- Performance Banner -->
        <div class="performance-banner">
            <div class="performance-banner-content">Weekly Return: {weekly_sign}{weekly_change:.2f}% | Total Return: {total_sign}{total_return:.2f}%</div>
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
                <h2 class="section-title">📊 Key Insights</h2>
                
{insights_section}
            </div>

            <!-- Performance Grid - Top/Worst Performers -->
            <h2 class="section-title">🎯 Performance Highlights</h2>
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
            <h2 class="section-title">📊 Benchmark Comparison</h2>
            <div class="benchmark-summary">
                <p><strong>Performance Summary:</strong> {benchmark_summary}</p>
            </div>
            <div class="performance-grid three-col">
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
            <div class="cta-container">
                <a href="{cta_url}" class="cta-button">📈 View Full Portfolio Analysis</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <div class="footer-brand">Quantum Investor Digest</div>
            <p class="footer-text">This newsletter is for informational purposes only and does not constitute investment advice.</p>
            <div class="footer-links">
                <a href="#">Unsubscribe</a>
                <span class="divider">|</span>
                <a href="https://quantuminvestor.net/newsletters/week{week_num}_newsletter.html">View in Browser</a>
            </div>
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
    print(f"🎨 Professional design with light/dark mode support")
    print("\n🔍 NEXT STEPS:")
    print(f"1. Open newsletters/week{week_num}_newsletter.html in browser to preview")
    print(f"2. Test both light and dark modes by switching OS theme")
    print(f"3. Send test email via your email service provider")
    print("="*60)
    
    logging.info("Newsletter generation complete")

if __name__ == "__main__":
    main()
