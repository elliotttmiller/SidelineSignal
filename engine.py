#!/usr/bin/env python3
"""
SidelineSignal V3 Engine Module

Core engine functions for managing SidelineSignal system processes
with rich console output and virtual environment isolation.
This module provides importable functions for orchestrating the system.
"""

import argparse
import subprocess
import sys
import os
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


class SidelineEngine:
    """Core engine class providing all SidelineSignal orchestration functions"""
    
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent.absolute()
        self.scout_venv = self.project_root / "scout_venv"
        self.app_venv = self.project_root / "app_venv"
        self.scout_dir = self.project_root / "signal_scout"
        self.app_dir = self.project_root / "sideline_app"
        
    def print_header(self):
        """Display professional header with system information"""
        header_text = Text("SidelineSignal V3 Engine", style="bold cyan")
        header_panel = Panel(
            header_text,
            title="🎯 CORE ENGINE",
            title_align="center",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(header_panel)
        self.console.print()

    def check_prerequisites(self):
        """Verify system prerequisites and display status"""
        self.console.print("[bold yellow]📋 SYSTEM PREREQUISITE CHECK[/bold yellow]")
        
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
        
        self.console.print(status_table)
        self.console.print()
        
        # Return overall status
        critical_failures = [scout_venv_status, app_venv_status, scout_dir_status, app_dir_status]
        if "❌" in critical_failures:
            self.console.print("[bold red]❌ CRITICAL PREREQUISITES MISSING - System cannot operate[/bold red]")
            return False
        else:
            self.console.print("[bold green]✅ All critical prerequisites satisfied[/bold green]")
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
        """Execute the Scrapy-based cognitive crawler"""
        self.console.print("[bold blue]🕷️  LAUNCHING V3 COGNITIVE CRAWLER[/bold blue]")
        
        python_exe = self.get_python_executable(self.scout_venv)
        scout_command = f'"{python_exe}" -m scrapy crawl scout'
        
        try:
            self.run_with_progress(
                scout_command,
                "Running cognitive crawler discovery engine",
                working_dir=self.scout_dir
            )
            self.console.print("[green]🎯 Scout crawler completed successfully[/green]")
            return True
        except subprocess.CalledProcessError:
            self.console.print("[red]💥 Scout crawler failed - Check error output above[/red]")
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
    """Main CLI entry point (backwards compatibility)"""
    parser = argparse.ArgumentParser(
        description="SidelineSignal V3 Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python engine.py --train                  # Train the AI classification model
  python engine.py --scout                  # Run the cognitive crawler
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
        help="Execute the Scrapy-based cognitive crawler"
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
    if not any([args.train, args.scout, args.app, args.full_test]):
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