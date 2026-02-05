import subprocess
import psutil
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Input, Static, Button
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen

class ProcessManager(App):
    """
    A TUI Process Manager
    """

    CSS = """
    DataTable { height: 1fr; margin: 1; border: round $primary; }
    #controls { height: auto; dock: bottom; padding: 1; background: $panel; }
    InputDialog { align: center middle; }
    #dialog_container { padding: 1 2; width: 50; height: auto; background: $surface; border: thick $primary; }
    Horizontal { height: auto; align: right middle; margin-top: 1; }
    Button { margin-left: 1; }
    """

    SORT_MAP = {"1": "pid", "2": "name", "3": "cpu", "4": "ram"}

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "sort_by('1')", "Sort PID"),
        ("2", "sort_by('2')", "Sort Name"),
        ("3", "sort_by('3')", "Sort CPU"),
        ("4", "sort_by('4')", "Sort RAM"),
        ("t", "terminate_dialog", "Terminate"),
        ("s", "start_dialog", "Start"),
    ]

    def __init__(self):
        super().__init__()
        self.sort_column_key = "pid"
        self.sort_reverse = False
        self.base_labels = {
            "pid": "PID",
            "name": "Name",
            "cpu": "CPU %",
            "ram": "RAM %",
            "status": "Status"
        }

    # =========================================================================
    # SYSTEM / PROCESS LOGIC
    # These methods interact directly with the Operating System.
    # =========================================================================

    def get_system_processes(self):
        """Fetches a list of current processes and their stats from the OS."""
        process_list = []
        # Get snapshots of process info
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                process_list.append((
                    info['pid'],
                    info['name'] or "Unknown",
                    round(info.get('cpu_percent') or 0.0, 1),
                    round(info.get('memory_percent') or 0.0, 2),
                    info['status']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return process_list

    def kill_process(self, pid: int):
        """Attempts to terminate a process by PID."""
        proceso = psutil.Process(pid)
        proceso.terminate()

    def spawn_process(self, command: str):
        """Starts a new system process."""
        subprocess.Popen(command.split())

    # =========================================================================
    # TEXTUAL / TUI METHODS
    # Methods below handle UI rendering, event handling, and data binding.
    # =========================================================================

    def compose(self) -> ComposeResult:
        """Defines the visual structure of the application."""
        yield Header(show_clock=True)
        yield DataTable(cursor_type="row")
        yield Vertical(
            Static(" Sort: [1] PID [2] Name [3] CPU [4] RAM | [T] Kill [S] Start"),
            id="controls",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initializes the TUI after the app starts."""
        table = self.query_one(DataTable)
        for key, label in self.base_labels.items():
            table.add_column(label, key=key)
        
        self.update_ui_headers()
        self.update_processes_in_table()
        # Tick/Polling: Refresh list every 2 seconds
        self.set_interval(2.0, self.update_processes_in_table)

    def update_ui_headers(self) -> None:
        """Syncs the column header labels with the current sort state."""
        table = self.query_one(DataTable)
        icon = "▲" if self.sort_reverse else "▼"
        
        for key, label in self.base_labels.items():
            column = table.columns[key]
            if key == self.sort_column_key:
                column.label = f"[b][reverse] {label} {icon} [/][/]"
            else:
                column.label = label
        table.refresh()

    def update_processes_in_table(self) -> None:
        """Bridge between System Logic and TUI: Refreshes the DataTable."""
        table = self.query_one(DataTable)
        
        # Save state to prevent UI jumping
        cursor_coordinate = table.cursor_coordinate
        scroll_x, scroll_y = table.scroll_x, table.scroll_y

        # Call System Logic
        rows = self.get_system_processes()

        # Update UI Component
        table.clear()
        table.add_rows(rows)
        table.sort(self.sort_column_key, reverse=self.sort_reverse)
        
        # Restore scroll and cursor position
        try:
            table.cursor_coordinate = cursor_coordinate
            table.scroll_to(scroll_x, scroll_y, animate=False)
        except Exception:
            pass

    def action_sort_by(self, key_index: str) -> None:
        """Binding action for keys 1-4."""
        new_key = self.SORT_MAP[key_index]
        if self.sort_column_key == new_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column_key = new_key
            self.sort_reverse = False
            
        self.update_ui_headers()
        self.update_processes_in_table()

    def action_terminate_dialog(self) -> None:
        """Shows the PID input modal."""
        self.push_screen(InputDialog("PID to kill", "Terminate"), self.handle_terminate)

    def action_start_dialog(self) -> None:
        """Shows the Command input modal."""
        self.push_screen(InputDialog("Command to start", "Start"), self.handle_start)

    def handle_terminate(self, pid_str: str | None) -> None:
        """Callback from Modal to perform the kill system logic."""
        if pid_str:
            try:
                self.kill_process(int(pid_str))
                self.notify(f"Killed {pid_str}")
                self.update_processes_in_table()
            except Exception as e:
                self.notify(f"Error: {e}", severity="error")

    def handle_start(self, command: str | None) -> None:
        """Callback from Modal to perform the spawn system logic."""
        if command:
            try:
                self.spawn_process(command)
                self.notify(f"Started: {command}")
                self.set_timer(0.5, self.update_processes_in_table)
            except Exception as e:
                self.notify(f"Error: {e}", severity="error")

# =============================================================================
# DIALOG COMPONENT
# =============================================================================

class InputDialog(ModalScreen[str]):
    """Generic modal screen for text input."""
    def __init__(self, placeholder: str, button_text: str):
        super().__init__()
        self.msg, self.btn = placeholder, button_text

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog_container"):
            yield Static(f" {self.msg}")
            yield Input(placeholder=self.msg, id="dialog_input")
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button(self.btn, variant="primary", id="submit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.dismiss(self.query_one(Input).value)
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.query_one("#submit", Button).press()
        elif event.key == "escape":
            self.dismiss(None)

if __name__ == "__main__":
    app = ProcessManager()
    app.run()
