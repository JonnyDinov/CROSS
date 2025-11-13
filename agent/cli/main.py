from __future__ import annotations

import logging
import sys
from typing import Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agent.config import config, template_manager
from agent.core.agent import agent
from agent.core.logging import configure_logging

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def app():
    pass


@app.command()
@click.argument("prompt", nargs=-1)
@click.option("--context", "-c", help="Additional context for the prompt")
@click.option("--stream/--no-stream", default=False, help="Stream the response")
def run(prompt: tuple, context: Optional[str], stream: bool):
    configure_logging(config.get("agent.log_level", "INFO"))
    
    if not prompt:
        console.print("[red]Error: Please provide a prompt[/red]")
        return

    prompt_text = " ".join(prompt)
    
    console.print(Panel(f"[bold cyan]Prompt:[/bold cyan] {prompt_text}", expand=False))
    
    if stream:
        console.print("[bold green]Response:[/bold green]")
        response_parts = []
        
        def stream_callback(chunk: str):
            console.print(chunk, end="")
            response_parts.append(chunk)
        
        agent.process_prompt(prompt_text, context, stream=True, callback=stream_callback)
        console.print("\n")
    else:
        with console.status("[bold green]Processing...", spinner="dots"):
            response = agent.process_prompt(prompt_text, context, stream=False)
        
        console.print(Panel(Markdown(response), title="[bold green]Response[/bold green]", expand=False))


@app.command()
def interactive():
    configure_logging(config.get("agent.log_level", "INFO"))
    console.print(Panel("[bold cyan]Windows AI Agent - Interactive Mode[/bold cyan]\nType 'exit' or 'quit' to leave.", expand=False))
    
    template_names = [t["name"] for t in template_manager.templates]
    commands = ["exit", "quit", "history", "clear", "help"]
    completer = WordCompleter(template_names + commands, ignore_case=True)
    history = InMemoryHistory()
    session = PromptSession(completer=completer, history=history)
    
    while True:
        try:
            prompt_text = session.prompt("Prompt> ")
            
            if prompt_text.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not prompt_text.strip():
                continue
            
            if prompt_text.lower() == "help":
                console.print("\n[bold]Available Commands:[/bold]")
                console.print("  exit, quit - Exit interactive mode")
                console.print("  history - Show command history")
                console.print("  clear - Clear screen")
                console.print("  help - Show this help\n")
                continue
            
            if prompt_text.lower() == "clear":
                console.clear()
                continue
            
            if prompt_text.lower() == "history":
                from agent.config import history_manager
                for entry in history_manager.history[-5:]:
                    console.print(f"[dim]{entry['timestamp']}[/dim] {entry['prompt'][:60]}...")
                continue
            
            with console.status("[bold green]Processing...", spinner="dots"):
                response = agent.process_prompt(prompt_text, stream=False)
            
            console.print(Panel(Markdown(response), title="[bold green]Response[/bold green]", expand=False))
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")



@app.command()
def gui():
    from agent.gui.main import run
    run()


@app.command()
@click.option("--model", "-m", help="Show info for a specific model")
def info(model: Optional[str]):
    configure_logging("ERROR")
    from agent.integrations.ollama_client import ollama_client
    from agent.config import CONFIG_FILE, LOGS_DIR
    
    console.print(Panel("[bold cyan]Windows AI Agent - System Info[/bold cyan]", expand=False))
    
    console.print(f"[bold]Config Location:[/bold] {CONFIG_FILE}")
    console.print(f"[bold]Logs Location:[/bold] {LOGS_DIR}")
    console.print(f"[bold]Ollama URL:[/bold] {config.get('ollama.base_url')}")
    
    if ollama_client.is_available():
        console.print("[bold green]Ollama Status:[/bold green] Available ✓")
        
        models = ollama_client.list_models()
        if models:
            console.print(f"\n[bold]Available Models ({len(models)}):[/bold]")
            for m in models:
                name = m.get("name", "Unknown")
                size = m.get("size", 0) / (1024**3)
                console.print(f"  • {name} ({size:.2f} GB)")

            if model:
                selected = next((m for m in models if m.get("name") == model), None)
                if not selected:
                    candidates = [m for m in models if m.get("name", "").startswith(model)]
                    selected = candidates[0] if candidates else None

                if selected:
                    console.print("\n[bold green]Model Details:[/bold green]")
                    console.print(selected)
                else:
                    console.print(f"[yellow]Model '{model}' not found[/yellow]")
        else:
            console.print("[yellow]No models found[/yellow]")
    else:
        console.print("[bold red]Ollama Status:[/bold red] Not Available ✗")


@app.command()
def history():
    configure_logging("ERROR")
    from agent.config import history_manager
    
    console.print(Panel("[bold cyan]Recent History[/bold cyan]", expand=False))
    
    if not history_manager.history:
        console.print("[yellow]No history available[/yellow]")
        return
    
    for entry in history_manager.history[-10:]:
        console.print(f"\n[bold cyan]{entry['timestamp']}[/bold cyan]")
        console.print(f"[bold]Prompt:[/bold] {entry['prompt'][:80]}...")
        console.print(f"[bold]Response:[/bold] {entry['response'][:80]}...")


@app.command()
@click.confirmation_option(prompt="Are you sure you want to clear all history?")
def clear_history():
    configure_logging("ERROR")
    from agent.config import history_manager
    history_manager.clear()
    console.print("[green]History cleared[/green]")


if __name__ == "__main__":
    app()
