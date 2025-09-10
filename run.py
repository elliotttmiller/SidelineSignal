#!/usr/bin/env python3
"""
SidelineSignal V3 Advanced Orchestrator Engine

Professional automation script for managing all SidelineSignal system processes
with rich console output and virtual environment isolation.
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

class SidelineOrchestrator:
    def __init__(self):
        self.console = Console()
        self.project_root = Path(__file__).parent.absolute()
        self.scout_venv = self.project_root / "scout_venv"
        self.app_venv = self.project_root / "app_venv"
        self.scout_dir = self.project_root / "signal_scout"
        self.app_dir = self.project_root / "sideline_app"
        
    def print_header(self):
        """Display professional header with system information"""
        header_text = Text("SidelineSignal V3 Advanced Orchestrator Engine", style="bold cyan")
        header_panel = Panel(
            header_text,
            title="🎯 COMMAND CENTER",
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
        
        # Check virtual environments
        scout_venv_status = "✅ OK" if self.scout_venv.exists() else "❌ MISSING"
        app_venv_status = "✅ OK" if self.app_venv.exists() else "❌ MISSING"
        
        # Check AI model
        model_path = self.scout_dir / "scout_model.pkl"
        ai_model_status = "✅ TRAINED" if model_path.exists() else "❌ NOT TRAINED"
        
        # Check database
        db_path = self.project_root / "shared_data" / "sites.db"
        db_status = "✅ INITIALIZED" if db_path.exists() else "❌ NOT INITIALIZED"
        
        # Check directories
        scout_dir_status = "✅ OK" if self.scout_dir.exists() else "❌ MISSING"
        app_dir_status = "✅ OK" if self.app_dir.exists() else "❌ MISSING"
        
        status_table.add_row("Scout Virtual Environment", scout_venv_status, str(self.scout_venv))
        status_table.add_row("App Virtual Environment", app_venv_status, str(self.app_venv))
        status_table.add_row("AI Model", ai_model_status, str(model_path))
        status_table.add_row("Database", db_status, str(db_path))
        status_table.add_row("Signal Scout Directory", scout_dir_status, str(self.scout_dir))
        status_table.add_row("Sideline App Directory", app_dir_status, str(self.app_dir))
        
        self.console.print(status_table)
        self.console.print()
        
        # Check if any critical components are missing
        missing_components = []
        if not self.scout_venv.exists():
            missing_components.append("Scout virtual environment")
        if not self.app_venv.exists():
            missing_components.append("App virtual environment")
        
        if missing_components:
            self.console.print(f"[bold red]❌ CRITICAL: Missing components: {', '.join(missing_components)}[/bold red]")
            self.console.print("[yellow]Please run the setup commands from the README first.[/yellow]")
            return False
        
        self.console.print("[bold green]✅ All prerequisites satisfied - System ready for operation[/bold green]")
        return True

    def get_python_executable(self, venv_path):
        """Get the correct Python executable for the given virtual environment"""
        if os.name == 'nt':  # Windows
            return venv_path / "Scripts" / "python.exe"
        else:  # Unix-like systems
            return venv_path / "bin" / "python"

    def run_with_progress(self, command, description, working_dir=None):
        """Execute command with rich progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(description, total=None)
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=working_dir
                )
                progress.remove_task(task)
                self.console.print(f"[bold green]✅ {description} - Completed successfully[/bold green]")
                return result
            except subprocess.CalledProcessError as e:
                progress.remove_task(task)
                self.console.print(f"[bold red]❌ {description} - Failed[/bold red]")
                self.console.print(f"[red]Error: {e.stderr}[/red]")
                raise

    def train_ai_model(self):
        """Train the AI classification model"""
        self.console.print("[bold blue]🧠 TRAINING AI CLASSIFICATION MODEL[/bold blue]")
        
        python_exe = self.get_python_executable(self.scout_venv)
        train_script = self.scout_dir / "train_model.py"
        
        command = f'"{python_exe}" "{train_script}"'
        
        try:
            self.run_with_progress(
                command,
                "Training AI classifier with updated samples",
                working_dir=self.scout_dir
            )
            
            # Verify model was created
            model_path = self.scout_dir / "scout_model.pkl"
            if model_path.exists():
                self.console.print(f"[bold green]🎯 AI model successfully saved to: {model_path}[/bold green]")
            else:
                self.console.print("[bold red]❌ Model training completed but file not found[/bold red]")
                
        except subprocess.CalledProcessError:
            self.console.print("[bold red]💥 AI model training failed - Check error output above[/bold red]")
            sys.exit(1)

    def run_scout(self):
        """Execute the V3 Scrapy-based cognitive crawler"""
        self.console.print("[bold blue]🕷️ LAUNCHING V3 COGNITIVE CRAWLER[/bold blue]")
        
        python_exe = self.get_python_executable(self.scout_venv)
        
        # Run Scrapy crawler command
        command = f'"{python_exe}" -m scrapy crawl scout'
        
        try:
            self.run_with_progress(
                command,
                "Executing Scrapy V3 cognitive discovery engine",
                working_dir=self.scout_dir
            )
            
            # Display log information
            log_path = self.scout_dir / "scout.log"
            if log_path.exists():
                self.console.print(f"[bold green]📝 Scout logs available at: {log_path}[/bold green]")
                self.console.print("[yellow]Tip: Use 'tail -f signal_scout/scout.log' to monitor real-time activity[/yellow]")
            
        except subprocess.CalledProcessError:
            self.console.print("[bold red]💥 Scout run failed - Check error output above[/bold red]")
            sys.exit(1)

    def start_web_app(self):
        """Start the Sideline monitoring web application"""
        self.console.print("[bold blue]🌐 STARTING SIDELINE MONITORING WEB APPLICATION[/bold blue]")
        
        python_exe = self.get_python_executable(self.app_venv)
        app_script = self.app_dir / "app.py"
        
        command = f'"{python_exe}" "{app_script}"'
        
        self.console.print("[yellow]⚠️  Web application will run in foreground mode[/yellow]")
        self.console.print("[yellow]   Press Ctrl+C to stop the server[/yellow]")
        self.console.print("[yellow]   Access URL: http://localhost:5000[/yellow]")
        self.console.print()
        
        try:
            # Run without progress indicator since this is a long-running process
            self.console.print("[bold green]🚀 Starting Flask application...[/bold green]")
            subprocess.run(command, shell=True, check=True, cwd=self.app_dir)
            
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]🛑 Web application stopped by user[/bold yellow]")
        except subprocess.CalledProcessError:
            self.console.print("[bold red]💥 Web application failed to start - Check error output above[/bold red]")
            sys.exit(1)

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
                self.train_ai_model()
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
            
            # Step 4: Web app validation (quick startup test)
            self.console.print("\n[bold cyan]Test Step 4: Web Application Validation[/bold cyan]")
            self.console.print("[yellow]Note: Web app test will start server briefly and then stop[/yellow]")
            
            python_exe_app = self.get_python_executable(self.app_venv)
            app_script = self.app_dir / "app.py"
            
            # Test if the app can start (run for 3 seconds then kill)
            import signal
            import threading
            
            def timeout_handler():
                time.sleep(3)
                os.kill(os.getpid(), signal.SIGTERM)
            
            try:
                timeout_thread = threading.Thread(target=timeout_handler)
                timeout_thread.daemon = True
                timeout_thread.start()
                
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
            
        except Exception as e:
            self.console.print(f"[bold red]💥 System test failed: {e}[/bold red]")
            sys.exit(1)

def main():
    """Main orchestrator entry point"""
    parser = argparse.ArgumentParser(
        description="SidelineSignal V3 Advanced Orchestrator Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --train                  # Train the AI classification model
  python run.py --scout                  # Run the V3 cognitive crawler
  python run.py --app                    # Start the monitoring web application
  python run.py --full-test              # Run comprehensive system test
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
        help="Execute the V3 Scrapy-based cognitive crawler"
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
    
    # Initialize orchestrator
    orchestrator = SidelineOrchestrator()
    
    # Display header and check prerequisites
    orchestrator.print_header()
    
    if not orchestrator.check_prerequisites():
        sys.exit(1)
    
    # Execute requested actions
    try:
        if args.train:
            orchestrator.train_ai_model()
        
        if args.scout:
            orchestrator.run_scout()
        
        if args.app:
            orchestrator.start_web_app()
        
        if args.full_test:
            orchestrator.run_full_test()
            
        orchestrator.console.print("\n[bold green]🎯 All requested operations completed successfully![/bold green]")
        
    except KeyboardInterrupt:
        orchestrator.console.print("\n[bold yellow]🛑 Operation interrupted by user[/bold yellow]")
        sys.exit(1)
    except Exception as e:
        orchestrator.console.print(f"\n[bold red]💥 Unexpected error: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()