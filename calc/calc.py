from typing import Optional
import sys

try:
    import tkinter as tk
    from tkinter import messagebox
    TK_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    tk = None
    messagebox = None
    TK_IMPORT_ERROR = exc


class CountdownTimerApp:
    def __init__(self, root: "tk.Tk") -> None:
        self.root = root
        self.root.title("Countdown Timer")
        self.root.resizable(False, False)

        self.remaining_seconds = 0
        self.initial_seconds = 0
        self.running = False
        self.after_id: Optional[str] = None

        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")
        self.display_var = tk.StringVar(value="00:00")

        self._build_ui()

    def _build_ui(self) -> None:
        main = tk.Frame(self.root, padx=16, pady=16)
        main.pack()

        input_row = tk.Frame(main)
        input_row.pack(pady=(0, 12))

        tk.Label(input_row, text="Minutes").grid(row=0, column=0, padx=(0, 6))
        tk.Entry(input_row, width=6, textvariable=self.minutes_var).grid(
            row=0, column=1, padx=(0, 10)
        )

        tk.Label(input_row, text="Seconds").grid(row=0, column=2, padx=(0, 6))
        tk.Entry(input_row, width=6, textvariable=self.seconds_var).grid(row=0, column=3)

        tk.Label(main, textvariable=self.display_var, font=("Helvetica", 38, "bold")).pack(
            pady=(0, 12)
        )

        button_row = tk.Frame(main)
        button_row.pack()

        self.start_btn = tk.Button(button_row, text="Start", width=12, command=self.start_timer)
        self.start_btn.grid(row=0, column=0, padx=4)

        self.pause_btn = tk.Button(
            button_row, text="Pause", width=12, command=self.toggle_pause, state=tk.DISABLED
        )
        self.pause_btn.grid(row=0, column=1, padx=4)

        self.reset_btn = tk.Button(button_row, text="Reset", width=12, command=self.reset_timer)
        self.reset_btn.grid(row=0, column=2, padx=4)

    def _parse_input_seconds(self) -> Optional[int]:
        minutes_text = self.minutes_var.get().strip()
        seconds_text = self.seconds_var.get().strip()

        if not minutes_text:
            minutes_text = "0"
        if not seconds_text:
            seconds_text = "0"

        try:
            minutes = int(minutes_text)
            seconds = int(seconds_text)
        except ValueError:
            messagebox.showerror("Invalid input", "Use whole numbers for minutes and seconds.")
            return None

        if minutes < 0 or seconds < 0:
            messagebox.showerror("Invalid input", "Minutes and seconds must be non-negative.")
            return None

        total_seconds = minutes * 60 + seconds
        normalized_minutes, normalized_seconds = divmod(total_seconds, 60)
        self.minutes_var.set(str(normalized_minutes))
        self.seconds_var.set(str(normalized_seconds))
        return total_seconds

    def _format_mm_ss(self, total_seconds: int) -> str:
        minutes, seconds = divmod(max(total_seconds, 0), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_display(self) -> None:
        self.display_var.set(self._format_mm_ss(self.remaining_seconds))

    def _set_inputs_from_seconds(self, total_seconds: int) -> None:
        minutes, seconds = divmod(max(total_seconds, 0), 60)
        self.minutes_var.set(str(minutes))
        self.seconds_var.set(str(seconds))

    def start_timer(self) -> None:
        if self.running:
            return

        # If user paused the timer, Start should resume from current remaining time.
        is_paused = self.pause_btn.cget("text") == "Resume" and self.remaining_seconds > 0
        if not is_paused:
            parsed = self._parse_input_seconds()
            if parsed is None:
                return
            if parsed == 0:
                messagebox.showerror("Invalid duration", "Please set a time greater than zero.")
                return
            self.remaining_seconds = parsed
            self.initial_seconds = parsed

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause")
        self._update_display()
        self._schedule_next_tick()

    def _schedule_next_tick(self) -> None:
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.after_id = self.root.after(1000, self._tick)

    def _tick(self) -> None:
        if not self.running:
            return

        self.remaining_seconds -= 1
        self._update_display()

        if self.remaining_seconds <= 0:
            self._finish_timer()
            return

        self._schedule_next_tick()

    def toggle_pause(self) -> None:
        if not self.running:
            self.running = True
            self.pause_btn.config(text="Pause")
            self.start_btn.config(state=tk.DISABLED)
            self._schedule_next_tick()
            return

        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.pause_btn.config(text="Resume")
        self.start_btn.config(state=tk.NORMAL)

    def reset_timer(self) -> None:
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.remaining_seconds = self.initial_seconds
        self._set_inputs_from_seconds(self.initial_seconds)
        self._update_display()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")

    def _finish_timer(self) -> None:
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.remaining_seconds = self.initial_seconds
        self._set_inputs_from_seconds(self.initial_seconds)
        self._update_display()
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="Pause")
        messagebox.showinfo("Timer", "Time's up!")


def main() -> None:
    if TK_IMPORT_ERROR is not None:
        print(
            "Tkinter is not available in this Python runtime.\n"
            "Your timer app needs a Tk-enabled Python.\n\n"
            "Quick fixes:\n"
            "1) Use system Python (often includes Tk on macOS):\n"
            "   /usr/bin/python3 calc/calc.py\n"
            "2) Or make uv use a different interpreter:\n"
            "   uv run --python /usr/bin/python3 calc/calc.py\n\n"
            "Original error: "
            f"{TK_IMPORT_ERROR}",
            file=sys.stderr,
        )
        sys.exit(1)

    root = tk.Tk()
    CountdownTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
