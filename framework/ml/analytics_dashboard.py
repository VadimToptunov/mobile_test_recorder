"""
Analytics Dashboard for test execution and coverage reporting.

Provides interactive HTML dashboards with charts, metrics, and insights.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("plotly not available - interactive charts disabled")


class AnalyticsDashboard:
    """
    Generate interactive analytics dashboards.

    Features:
    - Test execution metrics
    - Coverage analysis
    - Trend analysis
    - Selector stability report
    - Flow coverage heatmap
    - Performance metrics
    """

    def __init__(self):
        """Initialize dashboard generator."""
        self.report_data = {}

    def generate_execution_report(
        self,
        test_results: List[Dict[str, Any]],
        output_path: Path
    ):
        """
        Generate test execution report with charts.

        Args:
            test_results: List of test execution results
            output_path: Output HTML file path
        """
        if not PLOTLY_AVAILABLE:
            raise RuntimeError("plotly required for dashboard generation")

        # Calculate metrics
        total_tests = len(test_results)
        passed = sum(1 for r in test_results if r.get('status') == 'passed')
        failed = sum(1 for r in test_results if r.get('status') == 'failed')
        skipped = sum(1 for r in test_results if r.get('status') == 'skipped')

        pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Test Results Distribution',
                'Pass Rate Trend',
                'Execution Time by Test',
                'Failure Categories'
            ),
            specs=[
                [{'type': 'pie'}, {'type': 'scatter'}],
                [{'type': 'bar'}, {'type': 'pie'}]
            ]
        )

        # 1. Results pie chart
        fig.add_trace(
            go.Pie(
                labels=['Passed', 'Failed', 'Skipped'],
                values=[passed, failed, skipped],
                marker=dict(colors=['#28a745', '#dc3545', '#ffc107']),
                hole=0.3
            ),
            row=1, col=1
        )

        # 2. Pass rate trend (mock data for now)
        runs = list(range(1, 11))
        pass_rates = [85, 87, 86, 90, 89, 91, 88, 92, 91, pass_rate]

        fig.add_trace(
            go.Scatter(
                x=runs,
                y=pass_rates,
                mode='lines+markers',
                line=dict(color='#28a745', width=2),
                marker=dict(size=8)
            ),
            row=1, col=2
        )

        # 3. Execution time bar chart
        test_names = [r.get('name', f"Test {i}") for i, r in enumerate(test_results[:10])]
        exec_times = [r.get('duration', 0) for r in test_results[:10]]

        fig.add_trace(
            go.Bar(
                x=test_names,
                y=exec_times,
                marker=dict(color='#007bf')
            ),
            row=2, col=1
        )

        # 4. Failure categories
        failure_reasons = defaultdict(int)
        for result in test_results:
            if result.get('status') == 'failed':
                reason = result.get('failure_reason', 'Unknown')
                failure_reasons[reason] += 1

        if failure_reasons:
            fig.add_trace(
                go.Pie(
                    labels=list(failure_reasons.keys()),
                    values=list(failure_reasons.values()),
                    marker=dict(colors=['#dc3545', '#fd7e14', '#ffc107'])
                ),
                row=2, col=2
            )

        # Update layout
        fig.update_layout(
            title_text=f"Test Execution Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            showlegend=True,
            height=800
        )

        # Add summary metrics
        # summary_html =  # Unused """
        # DISABLED: <div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px;">
            # DISABLED: <h2> Summary Metrics</h2>
            # DISABLED: <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 20px;">
                # DISABLED: <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    # DISABLED: <div style="font-size: 32px; font-weight: bold; color: #007bff;">{total_tests}</div>
                    # DISABLED: <div style="color: #6c757d; margin-top: 5px;">Total Tests</div>
                # DISABLED: </div>
                # DISABLED: <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    # DISABLED: <div style="font-size: 32px; font-weight: bold; color: #28a745;">{passed}</div>
                    # DISABLED: <div style="color: #6c757d; margin-top: 5px;">Passed</div>
                # DISABLED: </div>
                # <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    # <div style="font-size: 32px; font-weight: bold; color: #dc3545;">{failed}</div>
                    # <div style="color: #6c757d; margin-top: 5px;">Failed</div>
                # </div>
                # <div style="background: white; padding: 15px; border-radius: 5px; text-align: center;">
                    # <div style="font-size: 32px; font-weight: bold; color: #17a2b8;">{pass_rate:.1f}%</div>
                    # <div style="color: #6c757d; margin-top: 5px;">Pass Rate</div>
                # </div>
            # </div>
        # </div>
        # """

        # Generate HTML
        # html_content = """
        # HTML generation temporarily disabled due to syntax issues
        # DISABLED: return """
        # DISABLED: <html>
        # DISABLED: <body>
            # DISABLED: <h1>Dashboard Temporarily Unavailable</h1>
            # DISABLED: <p>HTML dashboard generation is currently disabled.</p>
        # DISABLED: </body>
        # DISABLED: </html>
        # DISABLED: """

        # Save report
        # DISABLED: output_path.parent.mkdir(parents=True, exist_ok=True)
        # DISABLED: output_path.write_text(html_content)

        # DISABLED: logger.info(f"Execution report saved to {output_path}")

    # DISABLED: def generate_coverage_report(
        # DISABLED: self,
        # DISABLED: app_model: Any,
        # DISABLED: executed_flows: List[str],
        # DISABLED: output_path: Path
    # DISABLED: ):
        # DISABLED: """
        # DISABLED: Generate coverage analysis report.

        # DISABLED: Args:
            # DISABLED: app_model: AppModel with screens, flows, etc.
            # DISABLED: executed_flows: List of executed flow names
            # DISABLED: output_path: Output HTML file path
        # DISABLED: """
        # DISABLED: if not PLOTLY_AVAILABLE:
            raise RuntimeError("plotly required for dashboard generation")

        # Calculate coverage metrics
        total_screens = len(app_model.screens)
        total_flows = len(app_model.flows)
        executed_flow_count = len(executed_flows)

        flow_coverage = (executed_flow_count / total_flows * 100) if total_flows > 0 else 0

        # Screen coverage (screens involved in executed flows)
        covered_screens = set()
        for flow in app_model.flows:
            if flow.name in executed_flows:
                for step in flow.steps:
                    screen_id = step.get('screen')
                    if screen_id:
                        covered_screens.add(screen_id)

        screen_coverage = (len(covered_screens) / total_screens * 100) if total_screens > 0 else 0

        # API coverage
        total_apis = len(app_model.api_calls)
        covered_apis = set()
        for flow in app_model.flows:
            if flow.name in executed_flows:
                for step in flow.steps:
                    api_id = step.get('api_call')
                    if api_id:
                        covered_apis.add(api_id)

        api_coverage = (len(covered_apis) / total_apis * 100) if total_apis > 0 else 0

        # Create coverage chart
        fig = go.Figure()

        categories = ['Screens', 'Flows', 'API Calls']
        covered = [len(covered_screens), executed_flow_count, len(covered_apis)]
        total = [total_screens, total_flows, total_apis]
        uncovered = [total[i] - covered[i] for i in range(3)]

        fig.add_trace(go.Bar(
            name='Covered',
            x=categories,
            y=covered,
            marker=dict(color='#28a745')
        ))

        fig.add_trace(go.Bar(
            name='Uncovered',
            x=categories,
            y=uncovered,
            marker=dict(color='#dc3545')
        ))

        fig.update_layout(
            title='Test Coverage by Component',
            barmode='stack',
            yaxis_title='Count',
            height=500
        )

        # Coverage percentages gauge
        fig_gauge = make_subplots(
            rows=1, cols=3,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=('Screen Coverage', 'Flow Coverage', 'API Coverage')
        )

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=screen_coverage,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#28a745"}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=1)

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=flow_coverage,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#007bff"}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=2)

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=api_coverage,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#17a2b8"}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=3)

        fig_gauge.update_layout(height=300)

        # Generate HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coverage Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    # INVALID_LITERAL: box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    # INVALID_LITERAL: border-radius: 8px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1> Test Coverage Dashboard</h1>
                <p style="color: #6c757d;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                <div id="gauges"></div>
                <div id="coverage-bars"></div>

                <div class="metric-card">
                    <h2> Coverage Summary</h2>
                    <ul>
                        # INVALID_LITERAL: <li><strong>Screens:</strong> {len(covered_screens)}/{total_screens} covered ({screen_coverage:.1f}%)</li>
                        # INVALID_LITERAL: <li><strong>Flows:</strong> {executed_flow_count}/{total_flows} executed ({flow_coverage:.1f}%)</li>
                        # INVALID_LITERAL: <li><strong>API Calls:</strong> {len(covered_apis)}/{total_apis} tested ({api_coverage:.1f}%)</li>
                    </ul>
                </div>

                <div class="metric-card">
                    <h2> Uncovered Areas</h2>
                    <ul>
                        <li>Uncovered Screens: {total_screens - len(covered_screens)}</li>
                        <li>Unexecuted Flows: {total_flows - executed_flow_count}</li>
                        <li>Untested APIs: {total_apis - len(covered_apis)}</li>
                    </ul>
                </div>
            </div>
            <script>
                {fig_gauge.to_html(include_plotlyjs=False, div_id='gauges')}
                {fig.to_html(include_plotlyjs=False, div_id='coverage-bars')}
            </script>
        </body>
        </html>
        """

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content)

        logger.info(f"Coverage report saved to {output_path}")

    def generate_selector_stability_report(
        self,
        app_model: Any,
        output_path: Path
    ):
        """
        Generate selector stability analysis report.

        Args:
            app_model: AppModel with selector information
            output_path: Output HTML file path
        """
        if not PLOTLY_AVAILABLE:
            raise RuntimeError("plotly required for dashboard generation")

        # Analyze selector stability
        stability_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
        fragile_selectors = []

        for screen_id, screen in app_model.screens.items():
            for element in screen.elements:
                if element.selector:
                    stability = element.selector.stability.value if element.selector.stability else 'UNKNOWN'
                    stability_counts[stability] += 1

                    if stability == 'LOW' or stability == 'UNKNOWN':
                        fragile_selectors.append({
                            'screen': screen_id,
                            'element': element.id,
                            'stability': stability,
                            'selector': str(element.selector)
                        })

        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=list(stability_counts.keys()),
            values=list(stability_counts.values()),
            marker=dict(colors=['#28a745', '#ffc107', '#dc3545', '#6c757d']),
            hole=0.3
        )])

        fig.update_layout(
            title='Selector Stability Distribution',
            height=500
        )

        # Fragile selectors table
        fragile_table_html = ""
        if fragile_selectors:
            fragile_table_html = """
            <div class="metric-card">
                <h2> Fragile Selectors (Needs Attention)</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 10px; text-align: left;">Screen</th>
                            <th style="padding: 10px; text-align: left;">Element</th>
                            <th style="padding: 10px; text-align: left;">Stability</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            for sel in fragile_selectors[:20]:  # Show first 20
                fragile_table_html += """
                    <tr style="border-bottom: 1px solid #dee2e6;">
                        <td style="padding: 10px;">{sel['screen']}</td>
                        <td style="padding: 10px;">{sel['element']}</td>
                        <td style="padding: 10px;">
                            <span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">
                                {sel['stability']}
                            </span>
                        </td>
                    </tr>
                """

            fragile_table_html += """
                    </tbody>
                </table>
            </div>
            """

        # Generate HTML
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Selector Stability Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    # INVALID_LITERAL: box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .metric-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    # INVALID_LITERAL: border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1> Selector Stability Report</h1>
                <p style="color: #6c757d;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

                <div id="stability-chart"></div>

                <div class="metric-card">
                    <h2> Stability Breakdown</h2>
                    <ul>
                        <li><strong>HIGH:</strong> {stability_counts['HIGH']} selectors (Stable, test ID based)</li>
                        <li><strong>MEDIUM:</strong> {stability_counts['MEDIUM']} selectors (Moderately stable, text based)</li>
                        <li><strong>LOW:</strong> {stability_counts['LOW']} selectors (Fragile, XPath based)</li>
                        <li><strong>UNKNOWN:</strong> {stability_counts['UNKNOWN']} selectors (Not assessed)</li>
                    </ul>
                </div>

                {fragile_table_html}

                <div class="metric-card">
                    <h2> Recommendations</h2>
                    <ul>
                        <li>Consider adding test IDs to elements with LOW stability selectors</li>
                        <li>Use ML-based selector healing for fragile selectors</li>
                        <li>Review XPath-based selectors for optimization opportunities</li>
                    </ul>
                </div>
            </div>
            <script>
                {fig.to_html(include_plotlyjs=False, div_id='stability-chart')}
            </script>
        </body>
        </html>
        """

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content)

        logger.info(f"Selector stability report saved to {output_path}")
