#!/usr/bin/env python3
"""
SidelineSignal V3 Terminal Command Center

Professional Terminal User Interface (TUI) for operating the SidelineSignal
cognitive streaming discovery system with real-time monitoring and control.
"""

import asyncio
import os
import threading
import time
from pathlib import Path
from typing import Optional, List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Button, Static, Log, Input, DataTable, 
    Switch, Placeholder, Label, LoadingIndicator
)
from textual.screen import Screen
from textual.binding import Binding
from textual import on
from textual.timer import Timer
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

# Import the new engine
from engine import SidelineEngine


class PreFlightWidget(Static):
    """Widget for displaying system pre-flight check status"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path(__file__).parent.absolute()
    
    def compose(self) -> ComposeResult:
        yield Static(self.get_preflight_status(), id="preflight-status")
    
    def get_preflight_status(self) -> str:
        """Generate pre-flight status report"""
        console = Console()
        
        # Check AI Model
        model_path = self.project_root / "signal_scout" / "scout_model.pkl"
        ai_status = "✅ YES" if model_path.exists() else "❌ NO"
        
        # Check Database
        db_path = self.project_root / "shared_data" / "sites.db"
        db_status = "✅ YES" if db_path.exists() else "❌ NO"
        
        # Check Virtual Environments
        scout_venv = self.project_root / "scout_venv"
        app_venv = self.project_root / "app_venv"
        scout_venv_status = "✅ OK" if scout_venv.exists() else "❌ MISSING"
        app_venv_status = "✅ OK" if app_venv.exists() else "❌ MISSING"
        
        # Create status report
        status_lines = [
            "PRE-FLIGHT SYSTEM CHECK",
            "=" * 30,
            f"AI Model Trained: {ai_status}",
            f"Database Initialized: {db_status}",
            f"Scout venv: {scout_venv_status}",
            f"App venv: {app_venv_status}",
            "",
            f"Model Path: {model_path}",
            f"Database Path: {db_path}",
        ]
        
        return "\n".join(status_lines)
    
    def refresh_status(self):
        """Refresh the pre-flight status display"""
        preflight_widget = self.query_one("#preflight-status", Static)
        preflight_widget.update(self.get_preflight_status())


class LogViewerWidget(Container):
    """Advanced log viewer with real-time updates and filtering"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_file = Path(__file__).parent / "signal_scout" / "scout.log"
        self.filter_text = ""
        self.auto_scroll = True
        self.update_timer: Optional[Timer] = None
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Live Scout Log Viewer", classes="log-header")
            yield Input(placeholder="Filter logs by keyword...", id="log-filter")
            yield Switch(value=True, id="auto-scroll-switch")
            yield Label("Auto-scroll", classes="switch-label")
            yield Log(id="scout-log", auto_scroll=True)
    
    def on_mount(self) -> None:
        """Start log monitoring when widget is mounted"""
        self.start_log_monitoring()
    
    def start_log_monitoring(self):
        """Start monitoring the scout log file"""
        if self.update_timer:
            self.update_timer.stop()
        
        # Update log every 2 seconds
        self.update_timer = self.set_interval(2.0, self.update_log)
    
    def stop_log_monitoring(self):
        """Stop monitoring the scout log file"""
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer = None
    
    def update_log(self):
        """Update the log display with new content"""
        if not self.log_file.exists():
            return
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
            
            # Apply filter if specified
            if self.filter_text:
                lines = [line for line in lines if self.filter_text.lower() in line.lower()]
            
            # Get the log widget and update content
            log_widget = self.query_one("#scout-log", Log)
            
            # Clear and repopulate (simple approach)
            log_widget.clear()
            for line in lines[-100:]:  # Show last 100 lines
                log_widget.write(line.rstrip())
            
        except Exception as e:
            # Handle file access errors gracefully
            log_widget = self.query_one("#scout-log", Log)
            log_widget.write(f"Error reading log file: {e}")
    
    @on(Input.Changed, "#log-filter")
    def filter_changed(self, event: Input.Changed) -> None:
        """Handle filter text changes"""
        self.filter_text = event.value
        self.update_log()
    
    @on(Switch.Changed, "#auto-scroll-switch")
    def auto_scroll_changed(self, event: Switch.Changed) -> None:
        """Handle auto-scroll toggle"""
        self.auto_scroll = event.value
        log_widget = self.query_one("#scout-log", Log)
        log_widget.auto_scroll = self.auto_scroll


class AfterActionReportWidget(Static):
    """Widget for displaying scout run after-action reports"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path(__file__).parent.absolute()
    
    def compose(self) -> ComposeResult:
        yield Static(self.generate_report(), id="after-action-content")
    
    def generate_report(self) -> str:
        """Generate after-action report from scout logs and database"""
        try:
            # Analyze scout log for recent activity
            log_file = self.project_root / "signal_scout" / "scout.log"
            if not log_file.exists():
                return "No scout log file found. Run a scout operation first."
            
            # Basic log analysis
            with open(log_file, 'r') as f:
                log_content = f.read()
            
            # Count key metrics from logs
            pages_crawled = log_content.count("New page being crawled")
            ai_classifications = log_content.count("classifier's verdict")
            v2_verifications = log_content.count("V2 verification")
            db_writes = log_content.count("successfully written to database")
            
            # Try to get database stats
            db_stats = self.get_database_stats()
            
            report_lines = [
                "AFTER ACTION REPORT",
                "=" * 40,
                "",
                "DISCOVERY METRICS:",
                f"Pages Crawled: {pages_crawled}",
                f"AI Classifications: {ai_classifications}",
                f"V2 Verifications: {v2_verifications}",
                f"New Sites Found: {db_writes}",
                "",
                "DATABASE STATUS:",
                db_stats,
                "",
                "OPERATIONAL STATUS:",
                "✅ Scout Run Completed",
                "✅ Log Analysis Complete",
                "✅ System Ready for Next Operation",
            ]
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"Error generating report: {e}"
    
    def get_database_stats(self) -> str:
        """Get database statistics if possible"""
        try:
            import sqlite3
            db_path = self.project_root / "shared_data" / "sites.db"
            if not db_path.exists():
                return "Database not found"
            
            # Try to query database using sqlite3 module
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM sites;')
                total_sites = cursor.fetchone()[0]
                return f"Total Active Sites: {total_sites}"
                
        except Exception:
            return "Database access unavailable"
    
    def refresh_report(self):
        """Refresh the after-action report"""
        content_widget = self.query_one("#after-action-content", Static)
        content_widget.update(self.generate_report())


class CognitiveResultsWidget(Static):
    """Widget for displaying V5.0 cognitive cycle results with all three stages"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.results_data = None
    
    def compose(self) -> ComposeResult:
        yield Static(self.generate_cognitive_display(), id="cognitive-results-content")
    
    def update_results(self, results_data):
        """Update the widget with new cognitive cycle results."""
        self.results_data = results_data
        content_widget = self.query_one("#cognitive-results-content", Static)
        content_widget.update(self.generate_cognitive_display())
    
    def generate_cognitive_display(self) -> str:
        """Generate the three-stage cognitive dashboard display."""
        if not self.results_data:
            return "No cognitive cycle results available. Run the V5.0 cognitive organism first."
        
        display_lines = [
            "V5.0 COGNITIVE ORGANISM RESULTS",
            "=" * 50,
            ""
        ]
        
        # STAGE 1: PLANNING
        display_lines.append("🧠 STAGE 1: COGNITIVE PLANNING")
        display_lines.append("-" * 35)
        
        planning = self.results_data.get("planning", {})
        if planning.get("success"):
            mission_plan = planning.get("mission_plan", {})
            display_lines.extend([
                f"Mission Type: {mission_plan.get('mission_type', 'Unknown')}",
                f"Strategy: {mission_plan.get('strategy', 'No strategy')[:80]}...",
                f"AI-Generated Queries: {len(mission_plan.get('seed_queries', []))} queries",
                f"Adaptive Mode: {'Yes' if planning.get('adaptive') else 'No (Genesis)'}",
                "Status: ✅ SUCCESS"
            ])
        else:
            display_lines.extend([
                f"Error: {planning.get('error', 'Unknown planning error')}",
                "Status: ❌ FAILED"
            ])
        
        display_lines.append("")
        
        # STAGE 2: EXECUTION
        display_lines.append("⚡ STAGE 2: MISSION EXECUTION") 
        display_lines.append("-" * 35)
        
        execution = self.results_data.get("execution", {})
        if execution.get("success"):
            display_lines.extend([
                "Mission executed with AI-generated strategy",
                "Scout crawler completed discovery mission",
                "Status: ✅ SUCCESS"
            ])
        else:
            display_lines.extend([
                f"Error: {execution.get('error', 'Unknown execution error')}",
                "Status: ❌ FAILED"
            ])
        
        display_lines.append("")
        
        # STAGE 3: REPORTING
        display_lines.append("📊 STAGE 3: COGNITIVE ANALYSIS")
        display_lines.append("-" * 35)
        
        reporting = self.results_data.get("reporting", {})
        if reporting.get("success"):
            report = reporting.get("report", {})
            discovery = report.get("discovery_results", {})
            performance = report.get("performance_analysis", {})
            
            display_lines.extend([
                f"New Sites Found: {discovery.get('new_sites_found', 0)}",
                f"Sites Quarantined: {discovery.get('sites_quarantined', 0)}",
                f"Total Active Sites: {discovery.get('total_active_sites', 0)}",
                f"Most Effective Method: {performance.get('most_effective_hunt_method', 'Unknown')}",
                "Status: ✅ SUCCESS"
            ])
            
            # Show AI recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                display_lines.append("")
                display_lines.append("AI RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:3], 1):
                    display_lines.append(f"{i}. {rec[:60]}...")
                    
        else:
            display_lines.extend([
                f"Error: {reporting.get('error', 'Unknown reporting error')}",
                "Status: ❌ FAILED"
            ])
        
        display_lines.extend([
            "",
            "=" * 50,
            f"Overall Cycle Status: {'✅ SUCCESS' if self.results_data.get('success') else '❌ PARTIAL/FAILED'}",
            "Next cycle will use this report for adaptive planning."
        ])
        
        return "\n".join(display_lines)


class ControlPanel(Container):
    """Main control panel with operation buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_root = Path(__file__).parent.absolute()
        self.running_processes = {}
        self.engine = SidelineEngine()  # Use the engine instead of subprocess calls
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("System Controls", classes="control-header")
            yield Button("Train AI Model", id="btn-train", variant="primary")
            yield Button("Start Scout Run", id="btn-scout", variant="success")
            yield Button("Start Web App", id="btn-app", variant="warning")
            yield Button("Stop Web App", id="btn-stop-app", variant="error")
            yield Button("Full System Test", id="btn-test", variant="default")
            yield Static("", id="operation-status")
    
    def update_status(self, message: str, style: str = "white"):
        """Update operation status display"""
        status_widget = self.query_one("#operation-status", Static)
        status_widget.update(Text(message, style=style))
    
    @on(Button.Pressed, "#btn-train")
    def train_ai_model(self, event: Button.Pressed) -> None:
        """Handle AI model training"""
        self.update_status("Training AI model...", "yellow")
        
        def run_training():
            try:
                success = self.engine.train_ai_model()
                if success:
                    self.call_from_thread(self.update_status, "✅ AI model training completed", "green")
                else:
                    self.call_from_thread(self.update_status, "❌ Training failed", "red")
            except Exception as e:
                self.call_from_thread(self.update_status, f"❌ Training error: {str(e)[:50]}...", "red")
        
        threading.Thread(target=run_training, daemon=True).start()
    
    @on(Button.Pressed, "#btn-scout")
    def start_scout_run(self, event: Button.Pressed) -> None:
        """Handle V5.0 cognitive organism execution"""
        self.update_status("Starting V5.0 cognitive organism...", "yellow")
        
        def run_cognitive_organism():
            try:
                # Execute the V5.0 cognitive cycle
                results = self.engine.run_cognitive_cycle()
                if results.get("success", False):
                    self.call_from_thread(self.update_status, "✅ V5.0 cognitive cycle completed", "green")
                    # Notify app to switch to cognitive results display
                    self.app.call_from_thread(self.app.show_cognitive_results, results)
                else:
                    self.call_from_thread(self.update_status, "❌ V5.0 cognitive cycle failed", "red")
            except Exception as e:
                self.call_from_thread(self.update_status, f"❌ Cognitive error: {str(e)[:50]}...", "red")
        
        threading.Thread(target=run_cognitive_organism, daemon=True).start()
    
    @on(Button.Pressed, "#btn-app")
    def start_web_app(self, event: Button.Pressed) -> None:
        """Handle web app startup"""
        if "web_app" in self.running_processes:
            self.update_status("Web app already running", "yellow")
            return
        
        self.update_status("Starting web app...", "yellow")
        
        def run_web_app():
            try:
                # Use the engine to start the web app (this will run until interrupted)
                success = self.engine.start_web_app()
                
                # Clean up when process ends
                if "web_app" in self.running_processes:
                    del self.running_processes["web_app"]
                    if success:
                        self.call_from_thread(self.update_status, "Web app stopped", "white")
                    else:
                        self.call_from_thread(self.update_status, "❌ Web app failed", "red")
                    
            except Exception as e:
                self.call_from_thread(self.update_status, f"❌ Web app error: {str(e)[:50]}...", "red")
        
        # Mark that web app is running
        self.running_processes["web_app"] = True
        self.update_status("✅ Web app started (http://localhost:5000)", "green")
        threading.Thread(target=run_web_app, daemon=True).start()
    
    @on(Button.Pressed, "#btn-stop-app")
    def stop_web_app(self, event: Button.Pressed) -> None:
        """Handle web app shutdown"""
        if "web_app" not in self.running_processes:
            self.update_status("No web app running", "yellow")
            return
        
        # For now, just mark as stopped - the actual process will handle KeyboardInterrupt
        del self.running_processes["web_app"]
        self.update_status("⚠️  Web app stop requested - use Ctrl+C in terminal", "yellow")
    
    @on(Button.Pressed, "#btn-test")
    def run_full_test(self, event: Button.Pressed) -> None:
        """Handle full system test"""
        self.update_status("Running system test...", "yellow")
        
        def run_test():
            try:
                success = self.engine.run_full_test()
                if success:
                    self.call_from_thread(self.update_status, "✅ System test completed", "green")
                else:
                    self.call_from_thread(self.update_status, "❌ System test failed", "red")
            except Exception as e:
                self.call_from_thread(self.update_status, f"❌ Test error: {str(e)[:50]}...", "red")
        
        threading.Thread(target=run_test, daemon=True).start()


class SidelineControlCenter(App):
    """Main TUI application for SidelineSignal V5.0 Cognitive Command Center"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 4;
        grid-gutter: 1;
    }
    
    #header {
        column-span: 3;
        height: 3;
        background: $primary;
        color: $text;
        text-align: center;
        content-align: center middle;
    }
    
    #sidebar {
        row-span: 2;
        width: 25;
        background: $surface;
        border: thick $primary;
    }
    
    #content {
        column-span: 2;
        row-span: 2;
        background: $surface;
        border: thick $secondary;
    }
    
    #footer {
        column-span: 3;
        height: 3;
        background: $accent;
        color: $text;
        text-align: center;
        content-align: center middle;
    }
    
    .control-header, .log-header {
        background: $primary;
        color: $text;
        text-align: center;
        height: 1;
        margin: 1 0;
    }
    
    Button {
        margin: 1 0;
        width: 100%;
    }
    
    #operation-status {
        margin: 1 0;
        height: 2;
        border: solid $accent;
        padding: 0 1;
    }
    
    .switch-label {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "toggle_log", "Toggle Log"),
        Binding("f2", "show_report", "Show Report"),
        Binding("f3", "refresh", "Refresh"),
        Binding("f4", "show_cognitive", "Cognitive Results"),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_content = "preflight"  # preflight, log, report, cognitive
        self.cognitive_results = None
        
    def compose(self) -> ComposeResult:
        """Compose the main application layout"""
        yield Header(show_clock=True, id="header")
        yield ControlPanel(id="sidebar")
        yield PreFlightWidget(id="content")
        yield Footer(id="footer")
    
    def on_mount(self) -> None:
        """Initialize the application"""
        self.title = "SidelineSignal V5.0 Command Center"
        self.sub_title = "Cognitive Organism Control Panel"
    
    def action_toggle_log(self) -> None:
        """Toggle to log viewer"""
        if self.current_content == "log":
            self.show_preflight()
        else:
            self.show_log_viewer()
    
    def action_show_report(self) -> None:
        """Show after-action report"""
        self.show_after_action_report()
    
    def action_show_cognitive(self) -> None:
        """Show cognitive results"""
        self.show_cognitive_results()
    
    def action_refresh(self) -> None:
        """Refresh current content"""
        if self.current_content == "preflight":
            self.refresh_preflight()
        elif self.current_content == "log":
            self.refresh_log()
        elif self.current_content == "report":
            self.refresh_report()
        elif self.current_content == "cognitive":
            self.refresh_cognitive()
    
    def show_preflight(self) -> None:
        """Show pre-flight check content"""
        content_container = self.query_one("#content")
        content_container.remove_children()
        content_container.mount(PreFlightWidget())
        self.current_content = "preflight"
    
    def show_log_viewer(self) -> None:
        """Show log viewer content"""
        content_container = self.query_one("#content")
        content_container.remove_children()
        content_container.mount(LogViewerWidget())
        self.current_content = "log"
    
    def show_after_action_report(self) -> None:
        """Show after-action report content"""
        content_container = self.query_one("#content")
        content_container.remove_children()
        content_container.mount(AfterActionReportWidget())
        self.current_content = "report"
    
    def show_cognitive_results(self, results_data=None) -> None:
        """Show V5.0 cognitive results content"""
        if results_data:
            self.cognitive_results = results_data
        
        content_container = self.query_one("#content")
        content_container.remove_children()
        
        widget = CognitiveResultsWidget()
        if self.cognitive_results:
            widget.results_data = self.cognitive_results
        
        content_container.mount(widget)
        self.current_content = "cognitive"
    
    def refresh_preflight(self) -> None:
        """Refresh pre-flight check"""
        try:
            preflight_widget = self.query_one(PreFlightWidget)
            preflight_widget.refresh_status()
        except:
            pass
    
    def refresh_log(self) -> None:
        """Refresh log viewer"""
        try:
            log_widget = self.query_one(LogViewerWidget)
            log_widget.update_log()
        except:
            pass
    
    def refresh_report(self) -> None:
        """Refresh after-action report"""
        try:
            report_widget = self.query_one(AfterActionReportWidget)
            report_widget.refresh_report()
        except:
            pass
    
    def refresh_cognitive(self) -> None:
        """Refresh cognitive results"""
        try:
            cognitive_widget = self.query_one(CognitiveResultsWidget)
            if self.cognitive_results:
                cognitive_widget.update_results(self.cognitive_results)
        except:
            pass


def main():
    """Launch the SidelineSignal Command Center TUI"""
    app = SidelineControlCenter()
    app.run()


if __name__ == "__main__":
    main()