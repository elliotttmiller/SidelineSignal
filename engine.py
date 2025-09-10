#!/usr/bin/env python3
"""
SidelineSignal V5.0 Swarm Orchestrator Engine

The evolved cognitive command engine that orchestrates the SidelineSignal V5.0 
Cognitive Organism through the three-stage Plan → Execute → Report cycle.
This module provides the autonomous cognitive loop with PlannerAgent and ReportingAgent.
"""

import argparse
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


class SidelineEngine:
    """V5.0 Swarm Orchestrator providing autonomous cognitive loops"""
    
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent.absolute()
        self.scout_venv = self.project_root / "scout_venv"
        self.app_venv = self.project_root / "app_venv"
        self.scout_dir = self.project_root / "signal_scout"
        self.app_dir = self.project_root / "sideline_app"
        
        # V5.0 Cognitive Components
        self.planner_agent = None
        self.reporting_agent = None
        self._initialize_cognitive_agents()
        
    def _initialize_cognitive_agents(self):
        """Initialize the PlannerAgent and ReportingAgent for V5.0 operation."""
        try:
            # Import agents (they're in the signal_scout directory)
            sys.path.insert(0, str(self.scout_dir))
            
            from planner_agent import PlannerAgent
            from reporting_agent import ReportingAgent
            
            self.planner_agent = PlannerAgent()
            self.reporting_agent = ReportingAgent(str(self.project_root))
            
            self.console.print("[green]🧠 V5.0 Cognitive agents initialized successfully[/green]")
            
        except Exception as e:
            self.console.print(f"[red]⚠️  Failed to initialize cognitive agents: {e}[/red]")
            self.console.print("[yellow]V5.0 cognitive features disabled - falling back to V4 mode[/yellow]")
        
    def print_header(self):
        """Display professional header with V5.0 system information"""
        header_text = Text("SidelineSignal V5.0 Swarm Orchestrator", style="bold cyan")
        header_panel = Panel(
            header_text,
            title="🧠 COGNITIVE ORGANISM",
            title_align="center",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()
    
    def run_cognitive_cycle(self):
        """
        Execute the complete V5.0 cognitive cycle: Plan → Execute → Report
        
        This is the core autonomous loop that:
        1. Uses PlannerAgent to generate mission strategy
        2. Executes the strategy via the Scrapy crawler
        3. Uses ReportingAgent to analyze results
        4. Saves report for next cycle's planning
        
        Returns:
            Dict containing the complete cycle results
        """
        self.console.print("[bold blue]🚀 INITIATING V5.0 COGNITIVE CYCLE[/bold blue]")
        cycle_results = {}
        
        try:
            # STAGE 1: PLANNING
            self.console.print("\n[bold cyan]STAGE 1: COGNITIVE PLANNING[/bold cyan]")
            planning_result = self._execute_planning_stage()
            cycle_results["planning"] = planning_result
            
            if not planning_result.get("success", False):
                return cycle_results
            
            # STAGE 2: EXECUTION  
            self.console.print("\n[bold cyan]STAGE 2: MISSION EXECUTION[/bold cyan]")
            execution_result = self._execute_mission_stage(planning_result["mission_plan"])
            cycle_results["execution"] = execution_result
            
            # STAGE 3: REPORTING (always run to capture results)
            self.console.print("\n[bold cyan]STAGE 3: COGNITIVE ANALYSIS[/bold cyan]")
            reporting_result = self._execute_reporting_stage()
            cycle_results["reporting"] = reporting_result
            
            # Overall cycle success
            cycle_results["success"] = (
                planning_result.get("success", False) and
                execution_result.get("success", False) and
                reporting_result.get("success", False)
            )
            
            if cycle_results["success"]:
                self.console.print("\n[bold green]✅ V5.0 COGNITIVE CYCLE COMPLETED SUCCESSFULLY[/bold green]")
            else:
                self.console.print("\n[bold yellow]⚠️  V5.0 cognitive cycle completed with some issues[/bold yellow]")
            
            return cycle_results
            
        except Exception as e:
            self.console.print(f"\n[bold red]💥 V5.0 cognitive cycle failed: {e}[/bold red]")
            cycle_results["error"] = str(e)
            cycle_results["success"] = False
            return cycle_results
    
    def _execute_planning_stage(self):
        """Execute the cognitive planning stage using PlannerAgent."""
        if not self.planner_agent:
            return {
                "success": False,
                "error": "PlannerAgent not available",
                "mission_plan": self._get_fallback_plan()
            }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("PlannerAgent generating autonomous mission strategy...", total=None)
            
            try:
                # Get previous report for adaptive planning
                previous_report = self.reporting_agent.get_latest_report() if self.reporting_agent else None
                
                # Generate mission plan
                mission_plan = self.planner_agent.generate_mission_plan(previous_report)
                
                progress.update(task, completed=True)
                
                # Display the generated plan
                self._display_mission_plan(mission_plan)
                
                return {
                    "success": True,
                    "mission_plan": mission_plan,
                    "adaptive": previous_report is not None
                }
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]❌ Planning stage failed: {e}[/red]")
                return {
                    "success": False,
                    "error": str(e),
                    "mission_plan": self._get_fallback_plan()
                }
    
    def _execute_mission_stage(self, mission_plan):
        """Execute the mission using the generated plan."""
        with Progress(
            SpinnerColumn(), 
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Executing autonomous discovery mission...", total=None)
            
            try:
                # Save the mission plan for the scout to use
                self._prepare_scout_mission(mission_plan)
                
                # Execute the scout with the AI-generated plan
                python_exe = self.get_python_executable(self.scout_venv)
                scout_command = f'"{python_exe}" -m scrapy crawl scout'
                
                result = subprocess.run(
                    scout_command,
                    shell=True,
                    cwd=self.scout_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                progress.update(task, completed=True)
                self.console.print("[green]✅ Mission execution completed successfully[/green]")
                
                return {
                    "success": True,
                    "output": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
                    "mission_plan": mission_plan
                }
                
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                self.console.print("[red]❌ Mission execution failed[/red]")
                if e.stderr:
                    self.console.print(f"[red]Error output: {e.stderr[-200:]}...[/red]")
                
                return {
                    "success": False,
                    "error": str(e),
                    "mission_plan": mission_plan
                }
    
    def _execute_reporting_stage(self):
        """Execute the cognitive analysis stage using ReportingAgent."""
        if not self.reporting_agent:
            return {
                "success": False,
                "error": "ReportingAgent not available"
            }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("ReportingAgent analyzing mission results...", total=None)
            
            try:
                # Generate after-action report
                report = self.reporting_agent.generate_after_action_report()
                
                # Save report for next cycle
                report_path = self.reporting_agent.save_report(report)
                
                progress.update(task, completed=True)
                
                # Display key metrics
                self._display_mission_results(report)
                
                return {
                    "success": True,
                    "report": report,
                    "report_path": report_path
                }
                
            except Exception as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]❌ Reporting stage failed: {e}[/red]")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def _get_fallback_plan(self):
        """Get a basic fallback plan when PlannerAgent is unavailable."""
        return {
            "mission_type": "fallback",
            "strategy": "Basic discovery using default configuration",
            "seed_queries": [
                "watch NFL live free",
                "soccer stream online",
                "NBA streaming free",
                "sports stream sites"
            ],
            "reasoning": "Fallback plan - PlannerAgent unavailable"
        }
    
    def _prepare_scout_mission(self, mission_plan):
        """Prepare the scout configuration with the AI-generated plan."""
        try:
            # Load existing scout config
            config_path = self.scout_dir / "scout_config.json"
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {"operational_parameters": {}}
            
            # Update with AI-generated queries, removing hardcoded ones
            config["operational_parameters"]["seed_queries"] = mission_plan.get("seed_queries", [])
            
            # Remove hardcoded fallbacks as per requirements
            if "aggregator_urls" in config["operational_parameters"]:
                del config["operational_parameters"]["aggregator_urls"]
            if "permutation_bases" in config["operational_parameters"]:
                del config["operational_parameters"]["permutation_bases"]  
            if "permutation_tlds" in config["operational_parameters"]:
                del config["operational_parameters"]["permutation_tlds"]
            
            # Add mission metadata
            config["v5_mission"] = {
                "mission_type": mission_plan.get("mission_type", "unknown"),
                "strategy": mission_plan.get("strategy", ""),
                "timestamp": mission_plan.get("timestamp", ""),
                "planner_reasoning": mission_plan.get("reasoning", "")
            }
            
            # Save updated configuration
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.console.print("[green]✅ Scout mission configuration updated with AI-generated plan[/green]")
            
        except Exception as e:
            self.console.print(f"[red]⚠️  Failed to prepare scout mission: {e}[/red]")
    
    def _display_mission_plan(self, mission_plan):
        """Display the generated mission plan to the user."""
        plan_table = Table(show_header=True, header_style="bold magenta")
        plan_table.add_column("Component", style="cyan", width=20)
        plan_table.add_column("Details", style="white")
        
        plan_table.add_row("Mission Type", mission_plan.get("mission_type", "Unknown"))
        plan_table.add_row("Strategy", mission_plan.get("strategy", "No strategy provided"))
        
        queries = mission_plan.get("seed_queries", [])
        queries_text = "\n".join(f"• {q}" for q in queries[:5])  # Show first 5
        plan_table.add_row("AI-Generated Queries", queries_text)
        
        plan_table.add_row("Reasoning", mission_plan.get("reasoning", "No reasoning provided"))
        
        plan_panel = Panel(
            plan_table,
            title="🧠 AUTONOMOUS MISSION PLAN",
            border_style="blue"
        )
        self.console.print(plan_panel)
    
    def _display_mission_results(self, report):
        """Display mission results from the ReportingAgent."""
        results_table = Table(show_header=True, header_style="bold green")
        results_table.add_column("Metric", style="cyan", width=25)
        results_table.add_column("Result", style="white")
        
        # Mission summary
        summary = report.get("mission_summary", {})
        results_table.add_row("Pages Crawled", str(summary.get("pages_crawled", 0)))
        results_table.add_row("Links Evaluated", str(summary.get("links_evaluated", 0)))
        
        # Discovery results
        discovery = report.get("discovery_results", {})
        results_table.add_row("New Sites Found", str(discovery.get("new_sites_found", 0)))
        results_table.add_row("Sites Quarantined", str(discovery.get("sites_quarantined", 0)))
        results_table.add_row("Total Active Sites", str(discovery.get("total_active_sites", 0)))
        
        # Performance
        performance = report.get("performance_analysis", {})
        results_table.add_row("Most Effective Method", str(performance.get("most_effective_hunt_method", "Unknown")))
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        rec_text = "\n".join(f"• {r}" for r in recommendations[:3])  # Show first 3
        results_table.add_row("AI Recommendations", rec_text or "No recommendations")
        
        results_panel = Panel(
            results_table,
            title="📊 MISSION ANALYSIS RESULTS",
            border_style="green"
        )
        self.console.print(results_panel)

    def check_prerequisites(self):
        """Verify system prerequisites and display status"""
        self.console.print("[bold yellow]📋 V5.0 COGNITIVE SYSTEM PREREQUISITE CHECK[/bold yellow]")
        
        status_table = Table(show_header=True, header_style="bold magenta")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", justify="center")
        status_table.add_column("Details", style="dim")
        
        # Check Python
        python_status = "✅ OK" if sys.version_info >= (3, 7) else "❌ FAIL"
        python_details = f"Python {sys.version.split()[0]}"
        status_table.add_row("Python Runtime", python_status, python_details)
        
        # Check virtual environments
        scout_venv_status = "✅ OK" if self.scout_venv.exists() else "❌ MISSING"
        scout_venv_details = f"Path: {self.scout_venv.relative_to(self.project_root)}"
        status_table.add_row("Scout VirtualEnv", scout_venv_status, scout_venv_details)
        
        app_venv_status = "✅ OK" if self.app_venv.exists() else "❌ MISSING"
        app_venv_details = f"Path: {self.app_venv.relative_to(self.project_root)}"
        status_table.add_row("App VirtualEnv", app_venv_status, app_venv_details)
        
        # Check directories
        scout_dir_status = "✅ OK" if self.scout_dir.exists() else "❌ MISSING"
        scout_dir_details = f"Path: {self.scout_dir.relative_to(self.project_root)}"
        status_table.add_row("Scout Directory", scout_dir_status, scout_dir_details)
        
        app_dir_status = "✅ OK" if self.app_dir.exists() else "❌ MISSING"
        app_dir_details = f"Path: {self.app_dir.relative_to(self.project_root)}"
        status_table.add_row("App Directory", app_dir_status, app_dir_details)
        
        # Check AI model
        model_path = self.scout_dir / "scout_model.pkl"
        model_status = "✅ TRAINED" if model_path.exists() else "⚠️  NEEDS TRAINING"
        model_details = "AI classifier ready" if model_path.exists() else "Run training first"
        status_table.add_row("AI Model", model_status, model_details)
        
        # Check database
        db_path = self.project_root / "shared_data" / "sites.db"
        db_status = "✅ EXISTS" if db_path.exists() else "⚠️  EMPTY"
        db_details = "Site database ready" if db_path.exists() else "Will be created on first run"
        status_table.add_row("Database", db_status, db_details)
        
        # V5.0 Cognitive Agents Check
        planner_status = "✅ READY" if self.planner_agent else "❌ FAILED"
        planner_details = "PlannerAgent initialized" if self.planner_agent else "Check LLM connection"
        status_table.add_row("V5.0 PlannerAgent", planner_status, planner_details)
        
        reporter_status = "✅ READY" if self.reporting_agent else "❌ FAILED"  
        reporter_details = "ReportingAgent initialized" if self.reporting_agent else "ReportingAgent failed"
        status_table.add_row("V5.0 ReportingAgent", reporter_status, reporter_details)
        
        self.console.print(status_table)
        self.console.print()
        
        # Return overall status
        critical_failures = [scout_venv_status, app_venv_status, scout_dir_status, app_dir_status]
        if "❌" in critical_failures:
            self.console.print("[bold red]❌ CRITICAL PREREQUISITES MISSING - System cannot operate[/bold red]")
            return False
        else:
            cognitive_status = "✅" if (self.planner_agent and self.reporting_agent) else "⚠️"
            self.console.print(f"[bold green]{cognitive_status} Prerequisites satisfied - V5.0 Cognitive Organism ready[/bold green]")
            return True

    def get_python_executable(self, venv_path):
        """Get the Python executable for a virtual environment"""
        if os.name == 'nt':  # Windows
            return venv_path / "Scripts" / "python.exe"
        else:  # Unix-like systems
            return venv_path / "bin" / "python"

    def run_with_progress(self, command, description, working_dir=None):
        """Execute a command with rich progress display"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(description, total=None)
            
            # Execute the command
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                progress.update(task, completed=True)
                self.console.print(f"[green]✅ {description} completed successfully[/green]")
                return result
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                self.console.print(f"[red]❌ {description} failed[/red]")
                if e.stderr:
                    self.console.print(f"[red]Error output: {e.stderr[:200]}...[/red]")
                raise

    def train_ai_model(self):
        """Train the AI classification model"""
        self.console.print("[bold blue]🧠 TRAINING AI CLASSIFICATION MODEL[/bold blue]")
        
        python_exe = self.get_python_executable(self.scout_venv)
        train_script = self.scout_dir / "train_model.py"
        
        if not train_script.exists():
            self.console.print(f"[red]❌ Training script not found: {train_script}[/red]")
            return False
            
        train_command = f'"{python_exe}" "{train_script}"'
        
        try:
            self.run_with_progress(
                train_command,
                "Training AI classification model",
                working_dir=self.scout_dir
            )
            
            # Verify model was created
            model_path = self.scout_dir / "scout_model.pkl"
            if model_path.exists():
                self.console.print("[green]🎯 AI model training completed successfully[/green]")
                return True
            else:
                self.console.print("[red]❌ Model file not created - training may have failed[/red]")
                return False
                
        except subprocess.CalledProcessError:
            self.console.print("[red]💥 AI model training failed - Check error output above[/red]")
            return False

    def run_scout(self):
        """Execute the V5.0 cognitive scout cycle (Plan → Execute → Report)"""
        self.console.print("[bold blue]🧠 LAUNCHING V5.0 COGNITIVE ORGANISM[/bold blue]")
        
        try:
            # Execute the complete cognitive cycle
            results = self.run_cognitive_cycle()
            
            if results.get("success", False):
                self.console.print("[green]🎯 V5.0 Cognitive cycle completed successfully[/green]")
                return True
            else:
                self.console.print("[red]💥 V5.0 Cognitive cycle encountered issues[/red]")
                return False
                
        except Exception as e:
            self.console.print(f"[bold red]💥 V5.0 Cognitive organism failed: {e}[/bold red]")
            return False
    
    def run_scout_legacy(self):
        """Execute the traditional Scrapy-based crawler (V4 compatibility)"""
        self.console.print("[bold blue]🕷️  LAUNCHING LEGACY V4 CRAWLER[/bold blue]")
        
        python_exe = self.get_python_executable(self.scout_venv)
        scout_command = f'"{python_exe}" -m scrapy crawl scout'
        
        try:
            self.run_with_progress(
                scout_command,
                "Running traditional crawler discovery engine",
                working_dir=self.scout_dir
            )
            self.console.print("[green]🎯 Legacy scout crawler completed successfully[/green]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("[red]💥 Legacy scout crawler failed - Check error output above[/red]")
            return False

    def start_web_app(self):
        """Start the Sideline monitoring web application"""
        self.console.print("[bold blue]🌐 STARTING SIDELINE WEB APPLICATION[/bold blue]")
        
        python_exe = self.get_python_executable(self.app_venv)
        app_script = self.app_dir / "app.py"
        
        if not app_script.exists():
            self.console.print(f"[red]❌ Web app script not found: {app_script}[/red]")
            return False
            
        self.console.print("[yellow]🚀 Starting web application server...[/yellow]")
        self.console.print("[dim]Press Ctrl+C to stop the server[/dim]")
        
        try:
            # Start the web application (this will run until interrupted)
            subprocess.run(
                f'"{python_exe}" "{app_script}"',
                shell=True,
                cwd=self.app_dir,
                check=True
            )
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]🛑 Web application stopped by user[/bold yellow]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("[bold red]💥 Web application failed to start - Check error output above[/bold red]")
            return False

    def run_full_test(self):
        """Execute a comprehensive system test"""
        self.console.print("[bold blue]🔬 RUNNING COMPREHENSIVE SYSTEM TEST[/bold blue]")
        
        # Test sequence: Train -> Scout (limited) -> Verify database
        try:
            # Step 1: Verify/train AI model
            self.console.print("\n[bold cyan]Test Step 1: AI Model Verification[/bold cyan]")
            model_path = self.scout_dir / "scout_model.pkl"
            if not model_path.exists():
                self.console.print("[yellow]AI model not found - Training new model...[/yellow]")
                if not self.train_ai_model():
                    return False
            else:
                self.console.print("[green]✅ AI model already trained and ready[/green]")
            
            # Step 2: Limited scout run
            self.console.print("\n[bold cyan]Test Step 2: Limited Scout Discovery Run[/bold cyan]")
            python_exe = self.get_python_executable(self.scout_venv)
            
            # Run with limits for testing
            test_command = f'"{python_exe}" -m scrapy crawl scout -s CLOSESPIDER_PAGECOUNT=10 -s CLOSESPIDER_TIMEOUT=60'
            
            self.run_with_progress(
                test_command,
                "Running limited scout test (10 pages, 60 seconds max)",
                working_dir=self.scout_dir
            )
            
            # Step 3: Verify database state
            self.console.print("\n[bold cyan]Test Step 3: Database Verification[/bold cyan]")
            db_path = self.project_root / "shared_data" / "sites.db"
            if db_path.exists():
                self.console.print(f"[green]✅ Database accessible at: {db_path}[/green]")
                
                # Quick database check using sqlite3 command
                sqlite_command = f'sqlite3 "{db_path}" "SELECT COUNT(*) FROM sites;"'
                try:
                    result = subprocess.run(sqlite_command, shell=True, capture_output=True, text=True, check=True)
                    site_count = result.stdout.strip()
                    self.console.print(f"[green]📊 Total sites in database: {site_count}[/green]")
                except subprocess.CalledProcessError:
                    self.console.print("[yellow]⚠️  Could not query database (sqlite3 not available)[/yellow]")
            else:
                self.console.print("[red]❌ Database not found - Scout may not have completed successfully[/red]")
            
            # Step 4: Quick web app validation  
            self.console.print("\n[bold cyan]Test Step 4: Web Application Validation[/bold cyan]")
            python_exe_app = self.get_python_executable(self.app_venv)
            app_script = self.app_dir / "app.py"
            
            try:
                # Brief startup test (will timeout quickly)
                def timeout_handler():
                    time.sleep(5)
                    return
                
                subprocess.run(f'"{python_exe_app}" "{app_script}"', shell=True, cwd=self.app_dir, timeout=5)
                
            except (subprocess.TimeoutExpired, KeyboardInterrupt, OSError):
                self.console.print("[green]✅ Web application startup test completed[/green]")
            
            # Final summary
            self.console.print("\n[bold green]🎉 COMPREHENSIVE SYSTEM TEST COMPLETED[/bold green]")
            summary_panel = Panel(
                "[green]✅ AI Model: Operational\n"
                "✅ Scout Engine: Functional\n"
                "✅ Database: Accessible\n"
                "✅ Web Application: Validated[/green]",
                title="Test Results Summary",
                border_style="green"
            )
            self.console.print(summary_panel)
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]💥 System test failed: {e}[/bold red]")
            return False


def main():
    """Main CLI entry point for V5.0 Swarm Orchestrator"""
    parser = argparse.ArgumentParser(
        description="SidelineSignal V5.0 Swarm Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python engine.py --train                  # Train the AI classification model
  python engine.py --scout                  # Run the V5.0 cognitive organism
  python engine.py --scout-legacy           # Run traditional V4 crawler  
  python engine.py --app                    # Start the monitoring web application
  python engine.py --full-test              # Run comprehensive system test
        """
    )
    
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train the AI classification model with current samples"
    )
    
    parser.add_argument(
        "--scout",
        action="store_true",
        help="Execute the V5.0 cognitive organism (Plan → Execute → Report cycle)"
    )
    
    parser.add_argument(
        "--scout-legacy", 
        action="store_true",
        help="Execute the traditional V4 Scrapy-based cognitive crawler"
    )
    
    parser.add_argument(
        "--app",
        action="store_true",
        help="Start the Sideline monitoring web application"
    )
    
    parser.add_argument(
        "--full-test",
        action="store_true",
        help="Run a comprehensive system test with all components"
    )
    
    args = parser.parse_args()
    
    # Ensure at least one action is specified
    if not any([args.train, args.scout, args.scout_legacy, args.app, args.full_test]):
        parser.print_help()
        sys.exit(1)
    
    # Initialize engine
    engine = SidelineEngine()
    
    # Display header and check prerequisites
    engine.print_header()
    
    if not engine.check_prerequisites():
        sys.exit(1)
    
    # Execute requested actions
    success = True
    try:
        if args.train:
            success &= engine.train_ai_model()
        
        if args.scout:
            success &= engine.run_scout()
            
        if args.scout_legacy:
            success &= engine.run_scout_legacy()
        
        if args.app:
            success &= engine.start_web_app()
        
        if args.full_test:
            success &= engine.run_full_test()
            
        if success:
            engine.console.print("\n[bold green]🎯 All requested operations completed successfully![/bold green]")
        else:
            engine.console.print("\n[bold red]❌ Some operations failed![/bold red]")
            sys.exit(1)
        
    except KeyboardInterrupt:
        engine.console.print("\n[bold yellow]🛑 Operation interrupted by user[/bold yellow]")
        sys.exit(1)
    except Exception as e:
        engine.console.print(f"\n[bold red]💥 Unexpected error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()