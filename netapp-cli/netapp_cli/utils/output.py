"""Output formatting utilities."""

import json
import yaml
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from tabulate import tabulate

console = Console()


class OutputFormatter:
    """Handle different output formats."""

    def __init__(self, format_type: str = "table", verbose: bool = False):
        self.format_type = format_type
        self.verbose = verbose

    def format_output(self, data: Any, title: Optional[str] = None, headers: Optional[List[str]] = None):
        """Format and display output based on the specified format."""

        if self.format_type == "json":
            self._output_json(data)
        elif self.format_type == "yaml":
            self._output_yaml(data)
        else:  # Default to table
            if isinstance(data, list) and data:
                self._output_table(data, title, headers)
            elif isinstance(data, dict):
                self._output_dict(data, title)
            else:
                console.print(str(data))

    def _output_json(self, data: Any):
        """Output data as JSON."""
        console.print_json(json.dumps(data, indent=2, default=str))

    def _output_yaml(self, data: Any):
        """Output data as YAML."""
        yaml_output = yaml.dump(data, default_flow_style=False, default=str)
        console.print(yaml_output)

    def _output_table(self, data: List[Dict], title: Optional[str] = None, headers: Optional[List[str]] = None):
        """Output data as a rich table."""
        if not data:
            console.print("No data to display")
            return

        # Auto-detect headers if not provided
        if not headers:
            headers = self._extract_headers(data)

        # Create Rich table
        table = Table(title=title)

        # Add columns
        for header in headers:
            table.add_column(header.replace("_", " ").title(), style="cyan", no_wrap=True)

        # Add rows
        for item in data:
            row = []
            for header in headers:
                value = self._get_nested_value(item, header)
                row.append(str(value) if value is not None else "")
            table.add_row(*row)

        console.print(table)

    def _output_dict(self, data: Dict, title: Optional[str] = None):
        """Output dictionary as key-value table."""
        table = Table(title=title or "Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, indent=1, default=str)
            table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)

    def _extract_headers(self, data: List[Dict]) -> List[str]:
        """Extract headers from list of dictionaries."""
        headers = set()
        for item in data:
            headers.update(self._flatten_keys(item))
        return sorted(list(headers))

    def _flatten_keys(self, obj: Dict, parent_key: str = "", sep: str = ".") -> List[str]:
        """Flatten nested dictionary keys."""
        keys = []
        for key, value in obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict) and value:
                keys.extend(self._flatten_keys(value, new_key, sep))
            else:
                keys.append(new_key)
        return keys

    def _get_nested_value(self, obj: Dict, key: str, sep: str = ".") -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split(sep)
        value = obj

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def success(self, message: str):
        """Display success message."""
        console.print(f"[green]✓ {message}[/green]")

    def error(self, message: str):
        """Display error message."""
        console.print(f"[red]✗ {message}[/red]")

    def warning(self, message: str):
        """Display warning message."""
        console.print(f"[yellow]⚠ {message}[/yellow]")

    def info(self, message: str):
        """Display info message."""
        console.print(f"[blue]ℹ {message}[/blue]")

    def panel(self, content: str, title: str = None, style: str = "blue"):
        """Display content in a panel."""
        console.print(Panel(content, title=title, border_style=style))

    def progress_update(self, message: str):
        """Display progress update."""
        if self.verbose:
            console.print(f"[dim]{message}[/dim]")


def format_size(size_bytes: int) -> str:
    """Format bytes into human readable size."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def format_duration(seconds: int) -> str:
    """Format seconds into human readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
