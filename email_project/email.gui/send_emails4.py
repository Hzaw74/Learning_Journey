import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os, re, json, time, threading, random, webbrowser, logging
from datetime import datetime

# ==============================
# Logging
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==============================
# Files & Persistence
# ==============================
GLOBAL_FILE = "global_data.json"                 # email, app password, counters/limits/date
CV_FILES = {f"CV {i}": f"cv{i}.json" for i in range(1, 5)}  # per-tab (subject, body, recipients, resume, cover)

# ==============================
# Human-like Behavior Settings (kept as requested)
# ==============================
# IMPORTANT: You said "no shuffle", "daily limit 150", "randomized delay ±50%",
# "break after 5–8 emails for 5–15 mins", "typing simulation 1–3s",
# "gradual start 10–20s", and remove estimated time displays.
DAILY_LIMIT = 150
BASE_DELAY_MIN, BASE_DELAY_MAX = 180, 300        # 3–5 minutes base delay
DELAY_VARIATION = 0.5                            # ±50%
BATCH_MIN, BATCH_MAX = 5, 8                      # emails per batch before a long break
BATCH_BREAK_MIN, BATCH_BREAK_MAX = 300, 900      # 5–15 minutes (seconds)
TYPING_MIN, TYPING_MAX = 1, 3                    # "typing" simulation
INITIAL_START_MIN, INITIAL_START_MAX = 10, 20    # gradual start on first email in a run

# Reconnect policy (kept from older style patterns)
RECONNECT_EVERY = 20
MAX_RECONNECT_RETRIES = 3
MAX_INITIAL_CONNECT_RETRIES = 3

# ==============================
# Globals
# ==============================
sent_email_count = 0
daily_sent_count = 0
daily_sent_date = None
stop_flag = False
send_thread = None
current_sending_tab = None

# Debounced autosave timers (per CV tab)
debounce_after_ids = {}  # { "CV 1": id, ... }

# Tk references filled in GUI section
root = None
entry_email = None
entry_password = None
status_label = None
sent_email_count_var = None
daily_count_var = None
limit_var = None

# CV tab registry:
# cv_tabs = {
#   "CV 1": {
#       "frame": ..., "subject": Entry, "body": Text, "recipients": Text,
#       "resume_path": str|None, "cover_path": str|None,
#       "progress": ttk.Progressbar,
#       "log": Text,
#       "check_btn": Button, "remove_btn": Button
#   }, ...
# }
cv_tabs = {}

# ==============================
# Utility
# ==============================
def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def open_app_password_help():
    webbrowser.open("https://support.google.com/accounts/answer/185833")

def update_status(msg, color="white"):
    status_label.config(text=f"Status: {msg}", fg=color)
    logging.info(msg)

def info_log(tab_id, msg):
    log = cv_tabs[tab_id]["log"]
    log.insert(tk.END, msg + "\n")
    log.see(tk.END)

def warn_log(tab_id, msg):
    log = cv_tabs[tab_id]["log"]
    log.insert(tk.END, "⚠ " + msg + "\n")
    log.see(tk.END)

def err_log(tab_id, msg):
    log = cv_tabs[tab_id]["log"]
    log.insert(tk.END, "❌ " + msg + "\n")
    log.see(tk.END)

# ==============================
# Save/Load
# ==============================
def load_global():
    global sent_email_count, daily_sent_count, daily_sent_date
    if not os.path.exists(GLOBAL_FILE):
        daily_sent_date = today_str()
        return
    try:
        with open(GLOBAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry_email.insert(0, data.get("sender_email", ""))
        entry_password.insert(0, data.get("app_password", ""))
        sent_email_count = int(data.get("sent_email_count", 0))
        daily_sent_count = int(data.get("daily_sent_count", 0))
        daily_sent_date = data.get("daily_sent_date", today_str())
        sent_email_count_var.set(f"Total Sent: {sent_email_count}")
        daily_count_var.set(f"Sent Today: {daily_sent_count}")
        limit_var.set(f"Daily Limit: {DAILY_LIMIT}")
    except Exception as e:
        logging.exception(f"Failed to load global data: {e}")
        daily_sent_date = today_str()

def save_global():
    try:
        data = {
            "sender_email": entry_email.get(),
            "app_password": entry_password.get(),
            "sent_email_count": sent_email_count,
            "daily_sent_count": daily_sent_count,
            "daily_sent_date": daily_sent_date or today_str(),
        }
        with open(GLOBAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.exception(f"Failed to save global data: {e}")

def load_cv(tab_id):
    file = CV_FILES[tab_id]
    if not os.path.exists(file):
        return
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        tab = cv_tabs[tab_id]
        tab["subject"].delete(0, tk.END)
        tab["subject"].insert(0, data.get("subject", ""))

        tab["body"].delete("1.0", tk.END)
        tab["body"].insert("1.0", data.get("body", ""))

        tab["recipients"].delete("1.0", tk.END)
        tab["recipients"].insert("1.0", data.get("recipients", ""))

        tab["resume_path"] = data.get("resume", None)
        tab["cover_path"] = data.get("cover", None)
    except Exception as e:
        logging.exception(f"Failed to load {tab_id}: {e}")

def save_cv(tab_id):
    try:
        tab = cv_tabs[tab_id]
        data = {
            "subject": tab["subject"].get(),
            "body": tab["body"].get("1.0", tk.END),
            "recipients": tab["recipients"].get("1.0", tk.END),
            "resume": tab["resume_path"],
            "cover": tab["cover_path"]
        }
        with open(CV_FILES[tab_id], "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.exception(f"Failed to save {tab_id}: {e}")

def schedule_save(tab_id, delay_ms=800):
    # debounce per tab
    if tab_id in debounce_after_ids and debounce_after_ids[tab_id] is not None:
        root.after_cancel(debounce_after_ids[tab_id])
    debounce_after_ids[tab_id] = root.after(delay_ms, lambda: save_cv(tab_id))

# ==============================
# SMTP Helpers
# ==============================
def connect_smtp(sender_email, app_password):
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=60)
    server.starttls()
    server.login(sender_email, app_password)
    return server

def connect_smtp_with_retries(sender_email, app_password, max_retries=MAX_INITIAL_CONNECT_RETRIES):
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            return connect_smtp(sender_email, app_password)
        except Exception as e:
            last_exc = e
            time.sleep(2)
    raise last_exc

# ==============================
# Recipient Validation & UI Highlight
# ==============================
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

def parse_recipients(text):
    """Return (valid_list, invalid_lines_list).
       valid_list: [{Email, Position, raw}]
       invalid_lines_list: [raw_line, ...]"""
    valid, invalid = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        if len(parts) != 2:
            invalid.append(raw)
            continue
        email, position = parts[0].strip(), parts[1].strip()
        if not EMAIL_REGEX.fullmatch(email) or not position:
            invalid.append(raw)
            continue
        valid.append({"Email": email, "Position": position, "raw": raw})
    return valid, invalid

def highlight_invalid(tab_id):
    txt = cv_tabs[tab_id]["recipients"]
    content = txt.get("1.0", tk.END)
    _, invalid = parse_recipients(content)

    # clear old tags
    try:
        txt.tag_delete("invalid")
    except:
        pass
    txt.tag_configure("invalid", foreground="white", background="#7a0000")

    # apply to invalid lines
    start = "1.0"
    while True:
        line_start = start
        line_end = txt.index(f"{line_start} lineend")
        line_text = txt.get(line_start, line_end)
        if not line_text and txt.compare(line_start, "==", "end-1c"):
            break

        if line_text in invalid:
            txt.tag_add("invalid", line_start, line_end)

        # move to next line
        if txt.compare(line_end, "==", "end-1c"):
            break
        start = txt.index(f"{line_start} +1line")

def on_check_recipients(tab_id):
    highlight_invalid(tab_id)
    info_log(tab_id, "Checked recipients. Invalid entries are highlighted.")

def on_remove_invalid(tab_id):
    txt = cv_tabs[tab_id]["recipients"]
    content = txt.get("1.0", tk.END)
    valid, invalid = parse_recipients(content)
    if not invalid:
        info_log(tab_id, "No invalid recipients to remove.")
        return
    # Rewrite with only valid
    lines = [v["raw"] for v in valid]
    txt.delete("1.0", tk.END)
    txt.insert("1.0", "\n".join(lines) + ("\n" if lines else ""))
    # Clear tag
    try:
        txt.tag_delete("invalid")
    except:
        pass
    info_log(tab_id, f"Removed {len(invalid)} invalid recipient line(s).")
    schedule_save(tab_id)

# ==============================
# Animated waits & progress helpers
# ==============================
def animate_progress_start(tab_id, mode="indeterminate"):
    prog = cv_tabs[tab_id]["progress"]
    if mode == "indeterminate":
        prog.config(mode="indeterminate")
        prog.start(50)  # speed
    else:
        prog.stop()
        prog.config(mode="determinate")

def animate_progress_stop(tab_id):
    prog = cv_tabs[tab_id]["progress"]
    try:
        prog.stop()
    except:
        pass
    prog.config(mode="determinate")

# ==============================
# Email Sending
# ==============================
def build_message(sender_email, to_email, subject, body, resume_path, cover_path):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    def attach_file(path):
        with open(path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
            msg.attach(part)

    # resume is required
    if resume_path:
        attach_file(resume_path)

    # cover optional
    if cover_path:
        attach_file(cover_path)

    return msg

def _send_worker(tab_id, recipients):
    global sent_email_count, daily_sent_count, daily_sent_date, stop_flag

    sender_email = entry_email.get().strip()
    app_password = entry_password.get().strip()
    tab = cv_tabs[tab_id]

    subject_t = tab["subject"].get().strip()
    body_t = tab["body"].get("1.0", tk.END).strip()
    resume_path = tab["resume_path"]
    cover_path = tab["cover_path"]

    # initial gradual start per run
    initial_wait = random.uniform(INITIAL_START_MIN, INITIAL_START_MAX)
    info_log(tab_id, f"Starting in ~{int(initial_wait)}s (gradual start)...")
    animate_progress_start(tab_id, "indeterminate")
    start_t = time.time()
    while time.time() - start_t < initial_wait:
        if stop_flag: 
            animate_progress_stop(tab_id)
            update_status("Stopped before start.", "orange")
            return
        time.sleep(0.25)
    animate_progress_stop(tab_id)

    # login
    info_log(tab_id, "Connecting to SMTP...")
    try:
        server = connect_smtp_with_retries(sender_email, app_password)
    except Exception as e:
        err_log(tab_id, f"SMTP login failed: {e}")
        update_status("Login failed", "red")
        return
    info_log(tab_id, "SMTP connected.")

    # reset daily date if needed
    if daily_sent_date != today_str():
        daily_sent_date = today_str()
        daily_sent_count = 0
        save_global()

    # determinate progress
    prog = tab["progress"]
    prog.config(maximum=len(recipients), value=0, mode="determinate")

    batch_goal = random.randint(BATCH_MIN, BATCH_MAX)
    batch_count = 0

    # Main loop
    for idx, r in enumerate(recipients, start=1):
        if stop_flag:
            info_log(tab_id, "Stop requested. Ending...")
            break

        # daily limit
        if daily_sent_count >= DAILY_LIMIT:
            warn_log(tab_id, f"🚫 Daily limit ({DAILY_LIMIT}) reached. Stopping.")
            update_status("Daily limit reached", "red")
            break

        # reconnect policy
        if (idx - 1) > 0 and (idx - 1) % RECONNECT_EVERY == 0:
            info_log(tab_id, "Reconnecting to SMTP to keep session fresh...")
            try:
                server.quit()
            except:
                pass
            try:
                server = connect_smtp_with_retries(sender_email, app_password, MAX_RECONNECT_RETRIES)
                info_log(tab_id, "Reconnected.")
            except Exception as e:
                err_log(tab_id, f"Reconnect failed: {e}")
                break

        # personalize
        subject = subject_t.replace("{position}", r["Position"])
        body = body_t.replace("{position}", r["Position"])

        # typing simulation
        typing_wait = random.uniform(TYPING_MIN, TYPING_MAX)
        info_log(tab_id, f"Typing... (~{int(typing_wait)}s)")
        animate_progress_start(tab_id, "indeterminate")
        t0 = time.time()
        while time.time() - t0 < typing_wait:
            if stop_flag:
                animate_progress_stop(tab_id)
                break
            time.sleep(0.2)
        animate_progress_stop(tab_id)
        if stop_flag:
            break

        # send
        try:
            msg = build_message(sender_email, r["Email"], subject, body, resume_path, cover_path)
            server.sendmail(sender_email, r["Email"], msg.as_string())
            sent_email_count += 1
            daily_sent_count += 1
            sent_email_count_var.set(f"Total Sent: {sent_email_count}")
            daily_count_var.set(f"Sent Today: {daily_sent_count}")
            save_global()
            info_log(tab_id, f"✅ Sent to {r['Email']} ({r['Position']})")
        except Exception as e:
            err_log(tab_id, f"Failed to send to {r['Email']}: {e}")

        # progress step
        prog.step(1)
        root.update_idletasks()

        # batch logic
        batch_count += 1
        if batch_count >= batch_goal and idx < len(recipients):
            # take a longer break
            break_secs = random.uniform(BATCH_BREAK_MIN, BATCH_BREAK_MAX)
            info_log(tab_id, f"Taking a coffee break (~{int(break_secs)}s)...")
            animate_progress_start(tab_id, "indeterminate")
            t1 = time.time()
            while time.time() - t1 < break_secs:
                if stop_flag:
                    break
                time.sleep(0.5)
            animate_progress_stop(tab_id)
            if stop_flag:
                break
            batch_goal = random.randint(BATCH_MIN, BATCH_MAX)
            batch_count = 0

        # inter-email delay (human-like)
        if idx < len(recipients) and not stop_flag:
            base = random.uniform(BASE_DELAY_MIN, BASE_DELAY_MAX)
            # apply ±50%
            jitter = random.uniform(-DELAY_VARIATION * base, DELAY_VARIATION * base)
            wait_s = max(0, base + jitter)
            info_log(tab_id, f"Waiting ~{int(wait_s)}s before next email...")
            animate_progress_start(tab_id, "indeterminate")
            t2 = time.time()
            while time.time() - t2 < wait_s:
                if stop_flag:
                    break
                time.sleep(0.5)
            animate_progress_stop(tab_id)

        # autosave tab (counter updates and any edits)
        save_cv(tab_id)

    try:
        server.quit()
    except:
        pass

    if stop_flag:
        update_status("Stopped.", "orange")
    else:
        update_status(f"Finished sending on {tab_id}.", "green")

def send_emails(tab_id):
    global send_thread, stop_flag, current_sending_tab

    if send_thread and send_thread.is_alive():
        messagebox.showwarning("Busy", "Already sending emails. Please stop or wait until it finishes.")
        return

    sender_email = entry_email.get().strip()
    app_password = entry_password.get().strip()

    if not sender_email or not app_password:
        messagebox.showerror("Missing", "Enter your Gmail and App Password (global).")
        return

    tab = cv_tabs[tab_id]
    subject = tab["subject"].get().strip()
    body = tab["body"].get("1.0", tk.END).strip()
    recipients_text = tab["recipients"].get("1.0", tk.END).strip()
    resume_path = tab["resume_path"]
    # cover optional

    if not subject or not body or not recipients_text:
        messagebox.showerror("Missing", f"Fill in Subject, Body, and Recipients for {tab_id}.")
        return
    if not resume_path:
        messagebox.showerror("Missing", f"Select a Resume for {tab_id}.")
        return

    valid, invalid = parse_recipients(recipients_text)
    if invalid:
        messagebox.showerror("Invalid Recipients", f"Please fix invalid recipients in {tab_id} (use 'Check' or 'Remove Invalid').")
        highlight_invalid(tab_id)
        return

    # set progress maximum and clear log
    tab["progress"].config(maximum=len(valid), value=0, mode="determinate")
    tab["log"].delete("1.0", tk.END)

    stop_flag = False
    current_sending_tab = tab_id
    update_status(f"Preparing to send ({tab_id})...", "yellow")

    # launch thread
    send_thread = threading.Thread(target=_send_worker, args=(tab_id, valid), daemon=True)
    send_thread.start()

def stop_sending():
    global stop_flag
    stop_flag = True
    update_status("Stopping...", "orange")

def reset_counters():
    global sent_email_count, daily_sent_count, daily_sent_date
    if messagebox.askyesno("Confirm", "Reset total & daily counters?"):
        sent_email_count = 0
        daily_sent_count = 0
        daily_sent_date = today_str()
        sent_email_count_var.set(f"Total Sent: {sent_email_count}")
        daily_count_var.set(f"Sent Today: {daily_sent_count}")
        save_global()
        update_status("Counters reset.", "green")

# ==============================
# File pickers
# ==============================
def select_file(kind, tab_id):
    path = filedialog.askopenfilename(
        title=f"Select {kind.title()} (PDF or any file)",
        filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf")]
    )
    if not path:
        return
    key = f"{kind}_path"
    cv_tabs[tab_id][key] = path
    save_cv(tab_id)
    update_status(f"{kind.title()} selected for {tab_id}: {os.path.basename(path)}", "green")
    info_log(tab_id, f"{kind.title()} set: {path}")

# ==============================
# GUI Build
# ==============================
def build_gui():
    global root, entry_email, entry_password, status_label
    global sent_email_count_var, daily_count_var, limit_var

    root = tk.Tk()
    root.title("Job Application Email Sender — 4 CV Tabs (with Human-like Behavior)")
    root.geometry("1120x940")
    root.configure(bg="#1f1f1f")

    # ------------- Global Credentials -------------
    g_frame = tk.Frame(root, bg="#1f1f1f")
    g_frame.pack(fill="x", padx=12, pady=(10, 6))

    tk.Label(g_frame, text="Your Gmail:", bg="#1f1f1f", fg="white").grid(row=0, column=0, sticky="w", padx=4, pady=2)
    entry_email = tk.Entry(g_frame, width=50, bg="#303030", fg="white", insertbackground="white")
    entry_email.grid(row=0, column=1, sticky="w", padx=4, pady=2)

    tk.Label(g_frame, text="App Password:", bg="#1f1f1f", fg="white").grid(row=1, column=0, sticky="w", padx=4, pady=2)
    entry_password = tk.Entry(g_frame, width=50, show="*", bg="#303030", fg="white", insertbackground="white")
    entry_password.grid(row=1, column=1, sticky="w", padx=4, pady=2)

    link = tk.Label(g_frame, text="How to create an App Password", fg="cyan", bg="#1f1f1f", cursor="hand2")
    link.grid(row=0, column=2, rowspan=2, sticky="w", padx=10)
    link.bind("<Button-1>", lambda e: open_app_password_help())

    # ------------- Global Controls / Counters -------------
    c_frame = tk.Frame(root, bg="#1f1f1f")
    c_frame.pack(fill="x", padx=12, pady=(0, 10))

    sent_email_count_var = tk.StringVar(value=f"Total Sent: {sent_email_count}")
    daily_count_var = tk.StringVar(value=f"Sent Today: {daily_sent_count}")
    limit_var = tk.StringVar(value=f"Daily Limit: {DAILY_LIMIT}")

    tk.Label(c_frame, textvariable=sent_email_count_var, bg="#1f1f1f", fg="yellow").pack(side="left", padx=8)
    tk.Label(c_frame, textvariable=daily_count_var, bg="#1f1f1f", fg="orange").pack(side="left", padx=8)
    tk.Label(c_frame, textvariable=limit_var, bg="#1f1f1f", fg="white").pack(side="left", padx=8)

    tk.Button(c_frame, text="Reset Counters", command=reset_counters, bg="#7a0000", fg="white").pack(side="right", padx=8)
    tk.Button(c_frame, text="Stop Sending", command=stop_sending, bg="#c0392b", fg="white").pack(side="right", padx=8)

    # ------------- Notebook (4 CV Tabs) -------------
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=6)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass

    for i in range(1, 5):
        tab_id = f"CV {i}"
        frame = tk.Frame(notebook, bg="#1f1f1f")
        notebook.add(frame, text=tab_id)

        # Subject
        tk.Label(frame, text="Subject (use {position} placeholder):",
                 bg="#1f1f1f", fg="white").pack(anchor="w", padx=10, pady=(10, 2))
        subject = tk.Entry(frame, width=90, bg="#2b2b2b", fg="white", insertbackground="white")
        subject.pack(fill="x", padx=10, pady=2)
        subject.bind("<KeyRelease>", lambda e, t=tab_id: schedule_save(t))

        # Body
        tk.Label(frame, text="Body:", bg="#1f1f1f", fg="white").pack(anchor="w", padx=10, pady=(10, 2))
        body = tk.Text(frame, width=90, height=8, bg="#2b2b2b", fg="white", insertbackground="white")
        body.pack(fill="both", padx=10, pady=2)
        body.bind("<KeyRelease>", lambda e, t=tab_id: schedule_save(t))

        # Files
        f_frame = tk.Frame(frame, bg="#1f1f1f")
        f_frame.pack(fill="x", padx=10, pady=(8, 2))
        tk.Button(f_frame, text="Select Resume (required)", command=lambda t=tab_id: select_file("resume", t),
                  bg="#34495e", fg="white").pack(side="left", padx=6)
        tk.Button(f_frame, text="Select Cover Letter (optional)", command=lambda t=tab_id: select_file("cover", t),
                  bg="#34495e", fg="white").pack(side="left", padx=6)

        # Recipients
        tk.Label(frame, text="Recipients (one per line: email,position):",
                 bg="#1f1f1f", fg="white").pack(anchor="w", padx=10, pady=(10, 2))
        recipients = tk.Text(frame, width=90, height=8, bg="#2b2b2b", fg="white", insertbackground="white")
        recipients.pack(fill="both", padx=10, pady=2)
        recipients.bind("<KeyRelease>", lambda e, t=tab_id: schedule_save(t))

        # Recipient tools
        rtools = tk.Frame(frame, bg="#1f1f1f")
        rtools.pack(fill="x", padx=10, pady=(4, 10))
        btn_check = tk.Button(rtools, text="Check Recipients", command=lambda t=tab_id: on_check_recipients(t),
                              bg="#6c5ce7", fg="white")
        btn_check.pack(side="left", padx=4)
        btn_remove = tk.Button(rtools, text="Remove Invalid", command=lambda t=tab_id: on_remove_invalid(t),
                               bg="#e67e22", fg="white")
        btn_remove.pack(side="left", padx=4)

        # Actions
        act = tk.Frame(frame, bg="#1f1f1f")
        act.pack(fill="x", padx=10, pady=(0, 8))
        tk.Button(act, text=f"Send Emails for {tab_id}",
                  command=lambda t=tab_id: send_emails(t),
                  bg="#2ecc71", fg="#111").pack(side="left", padx=4)
        tk.Button(act, text="Stop", command=stop_sending,
                  bg="#c0392b", fg="white").pack(side="left", padx=4)

        # Progress + Log
        prog = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=980)
        prog.pack(fill="x", padx=10, pady=(2, 6))
        log = tk.Text(frame, width=120, height=12, bg="#1e1e1e", fg="white", insertbackground="white")
        log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        cv_tabs[tab_id] = {
            "frame": frame,
            "subject": subject,
            "body": body,
            "recipients": recipients,
            "resume_path": None,
            "cover_path": None,
            "progress": prog,
            "log": log,
            "check_btn": btn_check,
            "remove_btn": btn_remove,
        }

    # ------------- Status Bar -------------
    status_frame = tk.Frame(root, bg="#1f1f1f")
    status_frame.pack(fill="x", padx=10, pady=(0, 10))
    status_label_txt = tk.Label(status_frame, text="Status: Ready", bg="#1f1f1f", fg="green")
    status_label_txt.pack(anchor="w")
    globals()['status_label'] = status_label_txt

    # Load persisted data
    load_global()
    for t in CV_FILES:
        load_cv(t)

    return root

# ==============================
# Main
# ==============================
if __name__ == "__main__":
    root = build_gui()
    root.mainloop()
