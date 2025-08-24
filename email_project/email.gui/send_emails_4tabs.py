# -----------------------------------------------------------------------------
# Job Application Email Sender - 4 Tab Version
# This script helps users send job application emails with attachments via Gmail.
# Features 4 separate tabs for different CV types with independent functionality.
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import threading
import random
import os
import json
import webbrowser
import logging
import re
from datetime import datetime

# --------------------------
# Configuration & Constants
# --------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = "config_4tabs.json"
CV_TYPES = ["Software Developer", "Data Analyst", "Project Manager", "Designer"]

# Global variables
global_email = ""
global_password = ""
global_sent_count = 0
save_folder = None
send_thread = None
stop_flag = False

# Human-like behavior settings
BASE_DELAY_MIN = 180
BASE_DELAY_MAX = 300
DELAY_VARIATION = 0.50
BATCH_MIN = 5
BATCH_MAX = 8
BATCH_BREAK_MIN = 4 * 60
BATCH_BREAK_MAX = 10 * 60
TYPING_MIN = 1
TYPING_MAX = 3
INITIAL_START_MIN = 10
INITIAL_START_MAX = 20
DAILY_LIMIT = 150
RECONNECT_EVERY = 20
MAX_RECONNECT_RETRIES = 3
MAX_INITIAL_CONNECT_RETRIES = 3

# Dark mode colors
DARK_MODE_BG = "#2e2e2e"
DARK_MODE_FG = "#ffffff"
DARK_MODE_INPUT_BG = "#3e3e3e"
DARK_MODE_INPUT_FG = "#e0e0e0"
DARK_MODE_BUTTON_BG = "#5a5a5a"
DARK_MODE_BUTTON_FG = "#ffffff"
DARK_MODE_FRAME_BG = "#2e2e2e"
DARK_MODE_ERROR_FG = "#ff6b6b"
DARK_MODE_SUCCESS_FG = "#6bff6b"
DARK_MODE_WARNING_FG = "#ffcc66"
DARK_MODE_WAIT_FG = "#ffd966"

# --------------------------
# Helper Functions
# --------------------------

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def open_app_password_help():
    webbrowser.open("https://support.google.com/accounts/answer/185833")

def choose_save_folder():
    global save_folder
    folder = filedialog.askdirectory(title="Select Folder to Save Your Data")
    if folder:
        save_folder = folder
        save_config({"save_folder": save_folder})
        label_save_folder.config(text=f"Data will be saved in:\n{save_folder}")
        load_all_tab_data()
        update_status("Save folder selected. Data loaded if available.", "green")
    else:
        messagebox.showinfo("Info", "Save folder not selected. Data won't be saved.")
        update_status("No save folder selected.", "red")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def get_data_filepath(cv_type):
    if not save_folder:
        return None
    safe_name = cv_type.replace(" ", "_").lower()
    return os.path.join(save_folder, f"data_{safe_name}.json")

def save_tab_data(cv_type):
    path = get_data_filepath(cv_type)
    if not path:
        return
    
    tab = tabs[cv_type]
    data = {
        "subject": tab['subject_entry'].get(),
        "body": tab['body_text'].get("1.0", tk.END),
        "recipients": tab['recipients_text'].get("1.0", tk.END),
        "resume_path": tab.get('resume_path', ''),
        "cover_letter_path": tab.get('cover_letter_path', ''),
        "global_email": global_email,
        "global_password": global_password,
        "global_sent_count": global_sent_count
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        update_status(f"Data saved for {cv_type}.", "green")
    except Exception as e:
        log_output.insert(tk.END, f"⚠️ Failed to save data for {cv_type}: {e}\n")
        update_status(f"Error saving data for {cv_type}.", "red")

def load_tab_data(cv_type):
    path = get_data_filepath(cv_type)
    if not path or not os.path.exists(path):
        return
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        tab = tabs[cv_type]
        tab['subject_entry'].delete(0, tk.END)
        tab['subject_entry'].insert(0, data.get("subject", f"Application for {{position}} - {cv_type}"))
        
        tab['body_text'].delete("1.0", tk.END)
        tab['body_text'].insert(tk.END, data.get("body", 
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my interest in the {{position}} position as a {cv_type}.\n"
            f"Please find my resume attached.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best regards,\n"
            f"[Your Name]"
        ))
        
        tab['recipients_text'].delete("1.0", tk.END)
        tab['recipients_text'].insert(tk.END, data.get("recipients", ""))
        
        # Load file paths
        resume_path = data.get("resume_path", "")
        if resume_path and os.path.exists(resume_path):
            tab['resume_path'] = resume_path
            tab['resume_btn'].config(text=f"Resume: {os.path.basename(resume_path)}")
        
        cover_letter_path = data.get("cover_letter_path", "")
        if cover_letter_path and os.path.exists(cover_letter_path):
            tab['cover_letter_path'] = cover_letter_path
            tab['cover_letter_btn'].config(text=f"Cover Letter: {os.path.basename(cover_letter_path)}")
        
        # Update global variables
        global global_email, global_password, global_sent_count
        global_email = data.get("global_email", "")
        global_password = data.get("global_password", "")
        global_sent_count = data.get("global_sent_count", 0)
        
        # Update global entry fields
        global_email_entry.delete(0, tk.END)
        global_email_entry.insert(0, global_email)
        global_password_entry.delete(0, tk.END)
        global_password_entry.insert(0, global_password)
        global_sent_count_var.set(f"Global Sent: {global_sent_count}")
        
        update_status(f"Data loaded for {cv_type}.", "green")
    except Exception as e:
        log_output.insert(tk.END, f"⚠️ Failed to load data for {cv_type}: {e}\n")
        update_status(f"Error loading data for {cv_type}.", "red")

def load_all_tab_data():
    for cv_type in CV_TYPES:
        load_tab_data(cv_type)

def save_all_tab_data():
    for cv_type in CV_TYPES:
        save_tab_data(cv_type)

def on_user_input_change(cv_type, event=None):
    save_tab_data(cv_type)

def update_status(message, color="white"):
    status_label.config(text=f"Status: {message}", fg=color)

def validate_recipients(recipients_text):
    valid_recipients = []
    invalid_recipients = []
    email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')

    for line in recipients_text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 1)
        if len(parts) != 2:
            invalid_recipients.append({"line": line, "reason": "Incorrect format (missing comma or extra data)."})
            continue
        email = parts[0].strip()
        position = parts[1].strip()
        if not email_regex.fullmatch(email):
            invalid_recipients.append({"line": line, "reason": "Invalid email format."})
            continue
        if not position:
            invalid_recipients.append({"line": line, "reason": "Position is missing."})
            continue
        valid_recipients.append({"Email": email, "Position": position})

    return valid_recipients, invalid_recipients

def check_recipients_and_update_gui(cv_type):
    tab = tabs[cv_type]
    recipients_text = tab['recipients_text'].get("1.0", tk.END).strip()
    if not recipients_text:
        messagebox.showinfo("Info", f"Recipient list is empty for {cv_type}.")
        return

    tab['recipients_text'].tag_remove('error', '1.0', tk.END)
    valid_list, invalid_list = validate_recipients(recipients_text)

    log_output.delete(1.0, tk.END)

    if invalid_list:
        log_output.insert(tk.END, f"⚠️ Found invalid entries in {cv_type} tab. They are highlighted in red.\n", 'error')
        lines = recipients_text.splitlines()
        for item in invalid_list:
            try:
                line_number = lines.index(item['line']) + 1
                start_index = f"{line_number}.0"
                end_index = f"{line_number}.0 + {len(item['line'])}c"
                tab['recipients_text'].tag_add('error', start_index, end_index)
                log_output.insert(tk.END, f"  - '{item['line']}' -> Reason: {item['reason']}\n", 'error')
            except ValueError:
                log_output.insert(tk.END, f"  - Could not find and highlight: '{item['line']}' -> Reason: {item['reason']}\n", 'error')
        messagebox.showwarning("Validation Issues", f"Found {len(invalid_list)} invalid entries in {cv_type} tab.")
        update_status(f"Recipient list for {cv_type} contains errors.", "red")
    else:
        messagebox.showinfo("Success", f"All recipient entries are valid for {cv_type}!")
        update_status(f"Recipient list for {cv_type} is clean.", "green")

def remove_invalid_recipients(cv_type):
    tab = tabs[cv_type]
    recipients_text = tab['recipients_text'].get("1.0", tk.END).strip()
    if not recipients_text:
        messagebox.showinfo("Info", f"Recipient list is empty for {cv_type}.")
        return
    valid_list, invalid_list = validate_recipients(recipients_text)
    if not invalid_list:
        messagebox.showinfo("Info", f"No invalid entries to remove for {cv_type}.")
        return
    
    tab['recipients_text'].delete("1.0", tk.END)
    for row in valid_list:
        tab['recipients_text'].insert(tk.END, f"{row['Email']},{row['Position']}\n")
    
    save_tab_data(cv_type)
    log_output.insert(tk.END, f"✅ Removed {len(invalid_list)} invalid entries from {cv_type}.\n")
    update_status(f"Invalid entries removed from {cv_type}.", "green")

def select_resume(cv_type):
    tab = tabs[cv_type]
    path = filedialog.askopenfilename(title=f"Select Resume PDF for {cv_type}", filetypes=[("PDF Files", "*.pdf")])
    if path:
        tab['resume_path'] = path
        tab['resume_btn'].config(text=f"Resume: {os.path.basename(path)}")
        save_tab_data(cv_type)
        update_status(f"Resume selected for {cv_type}: {os.path.basename(path)}", "green")

def select_cover_letter(cv_type):
    tab = tabs[cv_type]
    path = filedialog.askopenfilename(title=f"Select Cover Letter PDF for {cv_type} (Optional)", filetypes=[("PDF Files", "*.pdf")])
    if path:
        tab['cover_letter_path'] = path
        tab['cover_letter_btn'].config(text=f"Cover Letter: {os.path.basename(path)}")
        save_tab_data(cv_type)
        update_status(f"Cover letter selected for {cv_type}: {os.path.basename(path)}", "green")

def reset_global_sent_count():
    global global_sent_count
    global_sent_count = 0
    global_sent_count_var.set(f"Global Sent: {global_sent_count}")
    update_status("Global sent email counter has been reset.", "green")
    save_all_tab_data()

def connect_smtp(sender_email, app_password):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    logging.info("SMTP connection established and logged in.")
    return server

def connect_smtp_with_retries(sender_email, app_password, max_retries=MAX_INITIAL_CONNECT_RETRIES):
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            server = connect_smtp(sender_email, app_password)
            return server
        except Exception as e:
            last_exception = e
            logging.warning(f"SMTP connect attempt {attempt} failed: {e}")
            time.sleep(2)
    raise last_exception

def stop_sending():
    global stop_flag
    stop_flag = True
    for cv_type in CV_TYPES:
        tabs[cv_type]['send_btn'].config(state=tk.NORMAL)
        tabs[cv_type]['stop_btn'].config(state=tk.DISABLED)
    update_status("Stopping email sending...", "orange")

def send_emails_for_tab(cv_type):
    global send_thread, stop_flag, global_sent_count
    
    if send_thread and send_thread.is_alive():
        messagebox.showwarning("Warning", "Email sending is already in progress.")
        return

    tab = tabs[cv_type]
    tab['send_btn'].config(state=tk.DISABLED)
    tab['stop_btn'].config(state=tk.NORMAL)

    log_output.delete(1.0, tk.END)
    tab['progress_bar']['value'] = 0

    sender_email = global_email_entry.get().strip()
    app_password = global_password_entry.get().strip()
    subject_template = tab['subject_entry'].get().strip()
    body_template = tab['body_text'].get("1.0", tk.END).strip()
    recipients_text = tab['recipients_text'].get("1.0", tk.END).strip()

    if not (sender_email and app_password and subject_template and body_template and recipients_text):
        messagebox.showerror("Error", f"Please fill all fields for {cv_type} tab.")
        tab['send_btn'].config(state=tk.NORMAL)
        tab['stop_btn'].config(state=tk.DISABLED)
        return

    if not tab.get('resume_path'):
        messagebox.showerror("Error", f"Please select your Resume PDF file for {cv_type}.")
        tab['send_btn'].config(state=tk.NORMAL)
        tab['stop_btn'].config(state=tk.DISABLED)
        return

    recipients, invalid_recipients = validate_recipients(recipients_text)
    if invalid_recipients:
        log_output.insert(tk.END, f"⚠️ Cannot start sending for {cv_type}. Invalid entries found.\n", 'error')
        messagebox.showerror("Validation Error", f"Please correct the recipient list for {cv_type} before sending.")
        tab['send_btn'].config(state=tk.NORMAL)
        tab['stop_btn'].config(state=tk.DISABLED)
        return

    total = len(recipients)
    tab['progress_bar']['maximum'] = total

    def job(recipients_list, cv_type):
        nonlocal sender_email, app_password, subject_template, body_template, total
        global stop_flag, global_sent_count

        update_status(f"Connecting to SMTP server for {cv_type}...", "yellow")
        server = None
        try:
            server = connect_smtp_with_retries(sender_email, app_password)
            update_status(f"SMTP connection successful for {cv_type}. Preparing to send...", "green")
        except smtplib.SMTPAuthenticationError:
            root.after(0, lambda: messagebox.showerror("Login Failed", "Authentication failed. Please check your Gmail email and App Password."))
            root.after(0, lambda: tabs[cv_type]['send_btn'].config(state=tk.NORMAL))
            root.after(0, lambda: tabs[cv_type]['stop_btn'].config(state=tk.DISABLED))
            update_status("Error: Authentication failed.", "red")
            return
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Login failed for {cv_type}: {e}"))
            root.after(0, lambda: tabs[cv_type]['send_btn'].config(state=tk.NORMAL))
            root.after(0, lambda: tabs[cv_type]['stop_btn'].config(state=tk.DISABLED))
            update_status(f"Error: Initial SMTP login failed for {cv_type}.", "red")
            return

        initial_wait = random.uniform(INITIAL_START_MIN, INITIAL_START_MAX)
        root.after(0, lambda: log_output.insert(tk.END, f"🕘 Preparing to send {cv_type} emails... (about {int(initial_wait)}s)\n"))
        slept = 0.0
        while slept < initial_wait and not stop_flag:
            time.sleep(0.5)
            slept += 0.5

        sent_count_in_session = 0

        while recipients_list and not stop_flag:
            row = recipients_list[0]
            recipient = row['Email']
            position = row['Position']

            subject = subject_template.replace("{position}", position)
            body = body_template.replace("{position}", position)

            root.after(0, lambda r=recipient, p=position: log_output.insert(
                tk.END, f"📝 Drafting {cv_type} email to {r} for '{p}'...\n"))

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach resume
            try:
                with open(tab['resume_path'], "rb") as f:
                    part = MIMEBase('application', 'pdf')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(tab["resume_path"])}')
                    msg.attach(part)
            except Exception as e:
                root.after(0, lambda r=recipient: log_output.insert(tk.END, f"⚠️ Could not attach resume for {r}: {e}\n"))
                logging.error(f"Could not attach resume for {recipient}: {e}")

            # Attach cover letter if selected
            if tab.get('cover_letter_path'):
                try:
                    with open(tab['cover_letter_path'], "rb") as f:
                        part = MIMEBase('application', 'pdf')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(tab["cover_letter_path"])}')
                        msg.attach(part)
                except Exception as e:
                    root.after(0, lambda r=recipient: log_output.insert(tk.END, f"⚠️ Could not attach cover letter for {r}: {e}\n"))
                    logging.error(f"Could not attach cover letter for {recipient}: {e}")

            # Send email
            email_sent = False
            retries = 0
            while not email_sent and retries < MAX_RECONNECT_RETRIES and not stop_flag:
                try:
                    server.sendmail(sender_email, recipient, msg.as_string())
                    root.after(0, lambda r=recipient, p=position: log_output.insert(tk.END, f"✅ Sent {cv_type} email to {r} ({p})\n"))
                    logging.info(f"Successfully sent {cv_type} email to {recipient}")
                    email_sent = True
                except Exception as e:
                    retries += 1
                    root.after(0, lambda r=recipient, error_msg=e: log_output.insert(
                        tk.END, f"❌ Failed to send {cv_type} email to {r}: {error_msg} (retry {retries}/{MAX_RECONNECT_RETRIES})\n"))
                    logging.error(f"Unexpected error sending {cv_type} email to {recipient}: {e}")
                    if retries < MAX_RECONNECT_RETRIES:
                        time.sleep(2)
                    else:
                        break

            if email_sent:
                recipients_list.pop(0)
                sent_count_in_session += 1
                global_sent_count += 1
                save_all_tab_data()

                root.after(0, lambda c=sent_count_in_session: tab['progress_bar'].config(value=c))
                root.after(0, lambda: global_sent_count_var.set(f"Global Sent: {global_sent_count}"))
                
                # Update recipients list
                tab['recipients_text'].delete("1.0", tk.END)
                for remaining_row in recipients_list:
                    tab['recipients_text'].insert(tk.END, f"{remaining_row['Email']},{remaining_row['Position']}\n")
                
                save_tab_data(cv_type)
            else:
                update_status(f"Failed to send {cv_type} email to {recipient}. Check log for details.", "red")
                break

            root.after(0, lambda: log_output.see(tk.END))

            if stop_flag or not recipients_list:
                break

            # Delay between sends
            base = random.uniform(BASE_DELAY_MIN, BASE_DELAY_MAX)
            variation = base * DELAY_VARIATION
            actual_delay = max(0.5, base + random.uniform(-variation, variation))

            root.after(0, lambda s=int(actual_delay): log_output.insert(
                tk.END, f"⏳ Waiting about {s//60}m {s%60}s before next {cv_type} email...\n"))

            slept_delay = 0.0
            while slept_delay < actual_delay and not stop_flag:
                time.sleep(0.5)
                slept_delay += 0.5

        if server:
            try:
                server.quit()
            except:
                pass

        root.after(0, lambda: tabs[cv_type]['send_btn'].config(state=tk.NORMAL))
        root.after(0, lambda: tabs[cv_type]['stop_btn'].config(state=tk.DISABLED))

        if not stop_flag and not recipients_list:
            root.after(0, lambda: messagebox.showinfo("Done", f"All {cv_type} emails have been sent!"))
            update_status(f"All {cv_type} emails have been sent!", "green")
        elif stop_flag:
            root.after(0, lambda: messagebox.showinfo("Stopped", f"{cv_type} email sending was stopped by the user."))
            update_status(f"{cv_type} sending stopped by user.", "orange")
        else:
            root.after(0, lambda: messagebox.showwarning("Incomplete", f"{cv_type} email sending stopped due to an error. Please check the log."))
            update_status(f"{cv_type} sending stopped due to an error. Check log.", "red")

        stop_flag = False
        logging.info(f"{cv_type} email sending job finished.")

    send_thread = threading.Thread(target=job, args=(recipients, cv_type))
    send_thread.daemon = True
    send_thread.start()

# --------------------------
# GUI Setup
# --------------------------

root = tk.Tk()
root.title("Job Application Email Sender - 4 Tab Version")
root.geometry("1200x1000")
root.configure(bg=DARK_MODE_BG)

# Configure ttk style for dark mode
style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background=DARK_MODE_BG, foreground=DARK_MODE_FG)
style.configure("TButton", background=DARK_MODE_BUTTON_BG, foreground=DARK_MODE_BUTTON_FG, borderwidth=1, relief="flat")
style.map("TButton", background=[('active', DARK_MODE_BUTTON_BG)])
style.configure("TProgressbar", background=DARK_MODE_SUCCESS_FG, troughcolor=DARK_MODE_INPUT_BG)
style.configure("TNotebook", background=DARK_MODE_BG)
style.configure("TNotebook.Tab", background=DARK_MODE_BUTTON_BG, foreground=DARK_MODE_BUTTON_FG, padding=[10, 5])
style.map("TNotebook.Tab", background=[('selected', DARK_MODE_SUCCESS_FG), ('active', DARK_MODE_BUTTON_BG)])

# Global settings frame
global_frame = tk.Frame(root, bg=DARK_MODE_BG)
global_frame.pack(fill=tk.X, padx=10, pady=5)

tk.Label(global_frame, text="Global Settings", font=("Arial", 12, "bold"), bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(anchor="w")

# Global email and password
email_frame = tk.Frame(global_frame, bg=DARK_MODE_BG)
email_frame.pack(fill=tk.X, pady=5)

tk.Label(email_frame, text="Gmail:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(side=tk.LEFT)
global_email_entry = tk.Entry(email_frame, width=40, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
global_email_entry.pack(side=tk.LEFT, padx=(5, 20))

tk.Label(email_frame, text="App Password:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(side=tk.LEFT)
global_password_entry = tk.Entry(email_frame, show='*', width=30, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
global_password_entry.pack(side=tk.LEFT, padx=(5, 20))

global_sent_count_var = tk.StringVar(value="Global Sent: 0")
global_sent_label = tk.Label(email_frame, textvariable=global_sent_count_var, bg=DARK_MODE_BG, fg="yellow")
global_sent_label.pack(side=tk.LEFT, padx=(20, 0))

btn_reset_global = tk.Button(email_frame, text="Reset Global Counter", command=reset_global_sent_count, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_reset_global.pack(side=tk.RIGHT)

# App password help
app_pass_info = tk.Label(global_frame, text="⚠ Gmail App Password is NOT your normal Gmail password. Enable 2-Step Verification and generate one.", 
                        fg=DARK_MODE_WARNING_FG, bg=DARK_MODE_BG, justify="left")
app_pass_info.pack(anchor="w", pady=(0, 5))

link_label = tk.Label(global_frame, text="Learn how to get an App Password", fg="cyan", bg=DARK_MODE_BG, cursor="hand2")
link_label.pack(anchor="w")
link_label.bind("<Button-1>", lambda e: open_app_password_help())

# Save folder selection
folder_frame = tk.Frame(global_frame, bg=DARK_MODE_BG)
folder_frame.pack(fill=tk.X, pady=5)

btn_choose_folder = tk.Button(folder_frame, text="Choose Save Folder", command=choose_save_folder, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_choose_folder.pack(side=tk.LEFT)

label_save_folder = tk.Label(folder_frame, text="No save folder selected. Data will NOT be saved until you choose a folder.", 
                            fg=DARK_MODE_FG, bg=DARK_MODE_BG, justify="left")
label_save_folder.pack(side=tk.LEFT, padx=(10, 0))

# Create notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Dictionary to store tab data
tabs = {}

# Create tabs for each CV type
for cv_type in CV_TYPES:
    # Create tab frame
    tab_frame = tk.Frame(notebook, bg=DARK_MODE_BG)
    notebook.add(tab_frame, text=cv_type)
    
    # Store tab data
    tabs[cv_type] = {
        'frame': tab_frame,
        'resume_path': None,
        'cover_letter_path': None
    }
    
    # Tab content
    # File selection buttons
    file_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    file_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tabs[cv_type]['resume_btn'] = tk.Button(file_frame, text=f"Select Resume PDF for {cv_type}", 
                                           command=lambda ct=cv_type: select_resume(ct), 
                                           bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
    tabs[cv_type]['resume_btn'].pack(side=tk.LEFT, padx=(0, 10))
    
    tabs[cv_type]['cover_letter_btn'] = tk.Button(file_frame, text=f"Select Cover Letter PDF for {cv_type} (Optional)", 
                                                 command=lambda ct=cv_type: select_cover_letter(ct), 
                                                 bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
    tabs[cv_type]['cover_letter_btn'].pack(side=tk.LEFT)
    
    # Subject line
    subject_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    subject_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(subject_frame, text=f"Email Subject ({cv_type}):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(anchor="w")
    tabs[cv_type]['subject_entry'] = tk.Entry(subject_frame, width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
    tabs[cv_type]['subject_entry'].pack(fill=tk.X, pady=(5, 0))
    tabs[cv_type]['subject_entry'].insert(0, f"Application for {{position}} - {cv_type}")
    
    # Email body
    body_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    tk.Label(body_frame, text=f"Email Body ({cv_type}):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(anchor="w")
    
    body_text_frame = tk.Frame(body_frame, bg=DARK_MODE_BG)
    body_text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    tabs[cv_type]['body_text'] = tk.Text(body_text_frame, height=8, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
    tabs[cv_type]['body_text'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    body_scroll = tk.Scrollbar(body_text_frame, command=tabs[cv_type]['body_text'].yview)
    body_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    tabs[cv_type]['body_text'].config(yscrollcommand=body_scroll.set)
    
    # Default body text
    default_body = (f"Dear Hiring Manager,\n\n"
                   f"I am writing to express my interest in the {{position}} position as a {cv_type}.\n"
                   f"Please find my resume attached.\n\n"
                   f"Thank you for your time and consideration.\n\n"
                   f"Best regards,\n"
                   f"[Your Name]")
    tabs[cv_type]['body_text'].insert(tk.END, default_body)
    
    # Recipients section
    recipients_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    recipients_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    recipients_header = tk.Frame(recipients_frame, bg=DARK_MODE_BG)
    recipients_header.pack(fill=tk.X)
    
    tk.Label(recipients_header, text=f"Recipients for {cv_type} (email,position per line):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(side=tk.LEFT)
    
    # Recipient validation buttons
    btn_check = tk.Button(recipients_header, text="Check Recipients", 
                         command=lambda ct=cv_type: check_recipients_and_update_gui(ct), 
                         bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
    btn_check.pack(side=tk.RIGHT, padx=(5, 0))
    
    btn_remove = tk.Button(recipients_header, text="Remove Invalid", 
                          command=lambda ct=cv_type: remove_invalid_recipients(ct), 
                          bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
    btn_remove.pack(side=tk.RIGHT, padx=(5, 0))
    
    # Recipients text area
    recipients_text_frame = tk.Frame(recipients_frame, bg=DARK_MODE_BG)
    recipients_text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    tabs[cv_type]['recipients_text'] = tk.Text(recipients_text_frame, height=10, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
    tabs[cv_type]['recipients_text'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    recipients_scroll = tk.Scrollbar(recipients_text_frame, command=tabs[cv_type]['recipients_text'].yview)
    recipients_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    tabs[cv_type]['recipients_text'].config(yscrollcommand=recipients_scroll.set)
    
    # Configure error highlighting
    tabs[cv_type]['recipients_text'].tag_configure('error', foreground=DARK_MODE_ERROR_FG)
    
    # Progress bar
    progress_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    progress_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tabs[cv_type]['progress_bar'] = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
    tabs[cv_type]['progress_bar'].pack(fill=tk.X)
    
    # Send/Stop buttons
    button_frame = tk.Frame(tab_frame, bg=DARK_MODE_BG)
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tabs[cv_type]['send_btn'] = tk.Button(button_frame, text=f"Send {cv_type} Emails", 
                                         command=lambda ct=cv_type: send_emails_for_tab(ct), 
                                         bg=DARK_MODE_SUCCESS_FG, fg=DARK_MODE_BG)
    tabs[cv_type]['send_btn'].pack(side=tk.LEFT, padx=(0, 10))
    
    tabs[cv_type]['stop_btn'] = tk.Button(button_frame, text=f"Stop {cv_type} Sending", 
                                         command=stop_sending, state=tk.DISABLED, 
                                         bg=DARK_MODE_ERROR_FG, fg=DARK_MODE_FG)
    tabs[cv_type]['stop_btn'].pack(side=tk.LEFT)
    
    # Bind auto-save events
    tabs[cv_type]['subject_entry'].bind("<KeyRelease>", lambda e, ct=cv_type: on_user_input_change(ct, e))
    tabs[cv_type]['body_text'].bind("<KeyRelease>", lambda e, ct=cv_type: on_user_input_change(ct, e))
    tabs[cv_type]['recipients_text'].bind("<KeyRelease>", lambda e, ct=cv_type: on_user_input_change(ct, e))

# Global input bindings
global_email_entry.bind("<KeyRelease>", lambda e: save_all_tab_data())
global_password_entry.bind("<KeyRelease>", lambda e: save_all_tab_data())

# Log output
log_frame = tk.Frame(root, bg=DARK_MODE_BG)
log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

tk.Label(log_frame, text="Log:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(anchor="w")

log_text_frame = tk.Frame(log_frame, bg=DARK_MODE_BG)
log_text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

log_output = tk.Text(log_text_frame, height=8, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
log_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

log_scroll = tk.Scrollbar(log_text_frame, command=log_output.yview)
log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
log_output.config(yscrollcommand=log_scroll.set)
log_output.tag_configure('error', foreground=DARK_MODE_ERROR_FG)

# Status label
status_label = tk.Label(root, text="Status: Ready to send.", fg=DARK_MODE_SUCCESS_FG, justify="left", wraplength=700, bg=DARK_MODE_BG)
status_label.pack(anchor="w", padx=10, pady=(5, 10))

# Load config and data on startup
app_config = load_config()
save_folder = app_config.get("save_folder")
if save_folder:
    label_save_folder.config(text=f"Data will be saved in:\n{save_folder}")
    load_all_tab_data()
    update_status("Ready to send.", DARK_MODE_SUCCESS_FG)
else:
    label_save_folder.config(text="No save folder selected. Data will NOT be saved until you choose a folder.")
    update_status("Please select a save folder to begin.", DARK_MODE_WARNING_FG)

root.mainloop()
