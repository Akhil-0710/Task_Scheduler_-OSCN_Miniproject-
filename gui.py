import tkinter as tk
from tkinter import ttk
from state import system_state


def update_gui():
    for row in tree.get_children():
        tree.delete(row)

    for wid, data in system_state["workers"].items():
        tree.insert("", "end", values=(
            wid,
            data["algorithm"],
            data["status"],
            data["load"],
            str(data.get("queue", []))
        ))

        if wid in logs_widgets:
            logs = data.get("logs", [])
            text_widget = logs_widgets[wid]
            
            current_text = text_widget.get("1.0", tk.END).strip()
            new_text = "\n".join(logs).strip()
            
            if current_text != new_text:
                text_widget.config(state=tk.NORMAL)
                text_widget.delete("1.0", tk.END)
                text_widget.insert(tk.END, new_text + "\n")
                text_widget.see(tk.END)
                text_widget.config(state=tk.DISABLED)

        if wid in progress_bars:
            progress_bars[wid]["value"] = data.get("progress", 0)

    queue_label.config(text="Global Queue: " + str(system_state["task_queue"]))

    root.after(100, update_gui)


root = tk.Tk()
root.title("Distributed Scheduler Monitor")
root.geometry("1000x800")

columns = ("ID", "Algorithm", "Status", "Load", "Local Queue")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(pady=20, fill="x", padx=20)

queue_label = tk.Label(root, text="", font=("Arial", 14))
queue_label.pack()

logs_frame = tk.Frame(root)
logs_frame.pack(fill="both", expand=True, padx=20, pady=20)

logs_widgets = {}
progress_bars = {}

for wid in ["1", "2", "3"]:
    frame = tk.LabelFrame(logs_frame, text=f"Worker {wid} Console")
    frame.pack(side="left", fill="both", expand=True, padx=5)
    
    pb = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=100)
    pb.pack(fill="x", padx=5, pady=(5, 0))
    progress_bars[wid] = pb

    text = tk.Text(frame, height=15, width=30, bg="black", fg="lime green", font=("Courier", 10))
    text.pack(fill="both", expand=True, padx=5, pady=5)
    text.config(state=tk.DISABLED)
    logs_widgets[wid] = text

update_gui()
root.mainloop()