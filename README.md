# ProcessManager TUI

A modern, high-performance terminal user interface for managing system processes, built with **Python**, **Textual**, and **psutil**. This project is inspired by the Charm ecosystem in Go, offering a responsive and visually appealing alternative to `top` or `htop`.

## Features

* **Live Polling:** Real-time process updates every 2 seconds.
* **Interactive Sorting:** Sort by PID, Name, CPU %, or RAM % using keyboard shortcuts `1-4`.
* **Visual Indicators:** Highlighted headers show the current active sort column and direction.
* **Process Control:** Start new processes or terminate existing ones by PID via modal dialogs.
* **Safety:** Handles access denied and non-existent process errors gracefully.

## Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `1` | Sort by PID |
| `2` | Sort by Name |
| `3` | Sort by CPU % |
| `4` | Sort by RAM % |
| `S` | Start a new process |
| `T` | Terminate a process (Kill) |
| `R` | Manual Refresh |
| `Q` | Quit Application |

## Getting Started

### Prerequisites

You must have [uv](https://github.com/astral-sh/uv) installed on your system. If you don't have it yet, you can install it via:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation & Running

You don't need to manually create a virtual environment or install dependencies. **uv** will handle everything automatically using the `main.py` script.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Patopm/ptop.git
   cd ptop
   ```

2. **Run the application:**
   The simplest way to run the script with all dependencies (Textual, psutil) is:

   ```bash
   uv run main.py
   ```

## Troubleshooting

* **Permissions:** Some system processes may require elevated permissions to show detailed CPU usage or to be terminated. If you encounter "Access Denied" notifications, consider running the script with `sudo` if necessary (though use caution).
* **Terminal Support:** For the best experience (including the 16.7 million colors and symbols), use a modern terminal like **Ghostty**, **Alacritty**, or **Kitty**.
