import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from pathlib import Path

SCRIPTS = [
    "1. Ideation & Script Gen.py",
    "2. Audio Creation.py",
    "3. Timestamp Transcription.py",
    "4. Storyboard Creation.py",
    "5. Title, Description & Cover.py",
    "6. Video Creation.py",
]

class Orchestrator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TL;DR Studios Orchestrator")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Select Step:").grid(row=0, column=0, sticky="w")
        self.step_var = tk.StringVar(value="1")
        options = [str(i) for i in range(1, len(SCRIPTS) + 1)]
        self.step_menu = ttk.Combobox(frame, textvariable=self.step_var, values=options, width=5)
        self.step_menu.grid(row=0, column=1, sticky="w")

        self.run_btn = ttk.Button(frame, text="Run Step", command=self.run_selected)
        self.run_btn.grid(row=0, column=2, padx=5)

        self.all_btn = ttk.Button(frame, text="Run All", command=self.run_all)
        self.all_btn.grid(row=0, column=3, padx=5)

        # inputs for script 1
        sep = ttk.Separator(self)
        sep.pack(fill="x", pady=5)

        input_frame = ttk.LabelFrame(self, text="Step 1 Options")
        input_frame.pack(fill="x", padx=10)

        ttk.Label(input_frame, text="Category number:").grid(row=0, column=0, sticky="w")
        self.cat_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.cat_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(input_frame, text="Idea number:").grid(row=1, column=0, sticky="w")
        self.idea_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.idea_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(input_frame, text="Edit instructions (one per line):").grid(row=2, column=0, sticky="nw")
        self.edits = tk.Text(input_frame, height=4, width=40)
        self.edits.grid(row=2, column=1, sticky="w")

        # output area
        sep2 = ttk.Separator(self)
        sep2.pack(fill="x", pady=5)
        self.output = scrolledtext.ScrolledText(self, height=20)
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

    def run_selected(self):
        idx = int(self.step_var.get()) - 1
        self.output.delete("1.0", tk.END)
        self.run_script(SCRIPTS[idx])

    def run_all(self):
        self.output.delete("1.0", tk.END)
        threading.Thread(target=self._run_all_steps, daemon=True).start()

    def _run_all_steps(self):
        for script in SCRIPTS:
            self.append_output(f"\n=== Running: {script} ===\n")
            self._execute_script(script)

    def run_script(self, script):
        threading.Thread(target=self._execute_script, args=(script,), daemon=True).start()

    def _execute_script(self, script):
        inputs = None
        if script == SCRIPTS[0]:
            edits = [line for line in self.edits.get("1.0", tk.END).splitlines() if line.strip()]
            inputs = [self.cat_var.get(), self.idea_var.get()] + edits + [""]
        if not Path(script).exists():
            self.append_output(f"Script not found: {script}\n")
            return
        try:
            proc = subprocess.Popen([
                "python",
                script,
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if inputs:
                proc.stdin.write("\n".join(inputs) + "\n")
                proc.stdin.flush()
            for line in proc.stdout:
                self.append_output(line)
            proc.wait()
        except Exception as e:
            self.append_output(f"Error running {script}: {e}\n")

    def append_output(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

if __name__ == "__main__":
    app = Orchestrator()
    app.mainloop()
