# -----------------------------------------------------------------------------
# Job Application Email Sender
# This script helps users send job application emails with attachments via Gmail.
# It does NOT download or execute code from the internet.
# It only sends emails you compose, to recipients you provide.
# If Windows Defender flags this script, add it to your exclusions if you trust it.
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

CONFIG_FILE = "config.json"
DATA_FILENAME = "saved_data.json"

resume_path = None
cover_letter_path = None
save_folder = None  # Global save folder path

send_thread = None
stop_flag = False

# How many emails to send before reconnecting SMTP to prevent timeouts
RECONNECT_EVERY = 20
MAX_RECONNECT_RETRIES = 3
MAX_INITIAL_CONNECT_RETRIES = 3

# Global counters
sent_email_count = 0  # lifetime counter (kept for backward-compat)
emails_to_send_count = 0  # for the current session / UI "Remaining"

# --- NEW: Daily limit tracking ---
DAILY_LIMIT = 150
daily_sent_count = 0
daily_sent_date = None  # YYYY-MM-DD string

# --- NEW: Human-like behavior tuning ---
BASE_DELAY_MIN = 180      # 3 minutes
BASE_DELAY_MAX = 300      # 5 minutes
DELAY_VARIATION = 0.50    # ±50%

BATCH_MIN = 5
BATCH_MAX = 8
BATCH_BREAK_MIN = 4 * 60   # 4 minutes (seconds)
BATCH_BREAK_MAX = 10 * 60  # 10 minutes (seconds)

TYPING_MIN = 1   # seconds
TYPING_MAX = 3   # seconds

INITIAL_START_MIN = 10  # seconds
INITIAL_START_MAX = 20  # seconds

# --------------------------
# Helper / Persistence
# --------------------------

def today_str():
    return datetime.now().strftime("%Y-%m-%d")

def open_app_password_help():
    """Opens a web browser to the Google App Password help page."""
    webbrowser.open("https://support.google.com/accounts/answer/185833")

def choose_save_folder():
    """Prompts the user to select a folder for saving data and updates the config."""
    global save_folder
    folder = filedialog.askdirectory(title="Select Folder to Save Your Data")
    if folder:
        save_folder = folder
        save_config({"save_folder": save_folder})
        label_save_folder.config(text=f"Data will be saved in:\n{save_folder}")
        load_data()
        update_status("Save folder selected. Data loaded if available.", "green")
    else:
        messagebox.showinfo("Info", "Save folder not selected. Data won't be saved.")
        update_status("No save folder selected.", "red")

def load_config():
    """Loads application configuration from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
    return {}

def save_config(config):
    """Saves application configuration to a JSON file."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def get_data_filepath():
    """Returns the full path to the data file, or None if no save folder is selected."""
    global save_folder
    if not save_folder:
        return None
    return os.path.join(save_folder, DATA_FILENAME)

def save_data():
    """Saves user-entered data to the specified JSON file."""
    path = get_data_filepath()
    if not path:
        return
    data = {
        "subject": entry_subject.get(),
        "body": text_body.get("1.0", tk.END),
        "recipients": text_recipients.get("1.0", tk.END),
        "sender_email": entry_email.get(),
        "app_password": entry_password.get(),
        "sent_email_count": sent_email_count,
        # --- NEW: persist daily counters ---
        "daily_sent_count": daily_sent_count,
        "daily_sent_date": daily_sent_date or today_str()
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        update_status("Data saved automatically.", "green")
    except Exception as e:
        log_output.insert(tk.END, f"⚠️ Failed to save data: {e}\n")
        logging.error(f"Failed to save data: {e}")
        update_status("Error saving data.", "red")

# Add a flag to indicate first load
first_load_done = False

def load_data():
    """Loads user data from a JSON file and populates the GUI fields."""
    global sent_email_count, first_load_done, daily_sent_count, daily_sent_date
    path = get_data_filepath()
    if not path or not os.path.exists(path):
        update_status("No saved data found.", "orange")
        # initialize daily counters for today
        daily_sent_date = today_str()
        daily_sent_count = 0
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry_subject.delete(0, tk.END)
        entry_subject.insert(0, data.get("subject", "Application for {position}"))
        text_body.delete("1.0", tk.END)
        text_body.insert(tk.END, data.get("body",
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in the {position} position.\n"
            "Please find my resume attached.\n\n"
            "Thank you for your time and consideration.\n\n"
            "Best regards,\n"
            "[Your Name]"
        ))
        text_recipients.delete("1.0", tk.END)
        text_recipients.insert(tk.END, data.get("recipients", ""))
        entry_email.delete(0, tk.END)
        entry_email.insert(0, data.get("sender_email", ""))
        entry_password.delete(0, tk.END)
        entry_password.insert(0, data.get("app_password", ""))

        # Lifetime counter (only update on first load)
        if not first_load_done:
            sent_email_count = data.get("sent_email_count", 0)
            first_load_done = True

        # Daily counters
        daily_sent_date = data.get("daily_sent_date", today_str())
        daily_sent_count = int(data.get("daily_sent_count", 0))
        if daily_sent_date != today_str():
            daily_sent_date = today_str()
            daily_sent_count = 0  # reset for a new day

        sent_email_count_var.set(f"Sent: {sent_email_count}")
        update_status("Saved data loaded successfully.", "green")
    except Exception as e:
        log_output.insert(tk.END, f"⚠️ Failed to load saved data: {e}\n")
        logging.error(f"Failed to load saved data from {path}: {e}")
        update_status("Error loading saved data.", "red")

def load_data_from_previous():
    """Loads data from a user-selected JSON file from a previous version."""
    file_path = filedialog.askopenfilename(
        title="Select Saved Data JSON from Previous Software",
        filetypes=[("JSON Files", "*.json")]
    )
    if not file_path:
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        entry_subject.delete(0, tk.END)
        entry_subject.insert(0, data.get("subject", "Application for {position}"))
        text_body.delete("1.0", tk.END)
        text_body.insert(tk.END, data.get("body",
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in the {position} position.\n"
            "Please find my resume attached.\n\n"
            "Thank you for your time and consideration.\n\n"
            "Best regards,\n"
            "[Your Name]"
        ))
        text_recipients.delete("1.0", tk.END)
        text_recipients.insert(tk.END, data.get("recipients", ""))
        entry_email.delete(0, tk.END)
        entry_email.insert(0, data.get("sender_email", ""))
        entry_password.delete(0, tk.END)
        entry_password.insert(0, data.get("app_password", ""))
        messagebox.showinfo("Success", "Data loaded successfully from previous software.")
        update_status("Data from previous software loaded.", "green")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")
        logging.error(f"Failed to load data from previous software file {file_path}: {e}")
        update_status("Error loading data from previous software.", "red")

def select_resume():
    """Opens a file dialog to select the resume PDF."""
    global resume_path
    path = filedialog.askopenfilename(title="Select Resume PDF", filetypes=[("PDF Files", "*.pdf")])
    if path:
        resume_path = path
        btn_resume.config(text=f"Resume: {os.path.basename(path)}")
        logging.info(f"Resume path selected: {path}")
        update_status(f"Resume selected: {os.path.basename(path)}", "green")

def select_cover_letter():
    """Opens a file dialog to select the cover letter PDF."""
    global cover_letter_path
    path = filedialog.askopenfilename(title="Select Cover Letter PDF (Optional)", filetypes=[("PDF Files", "*.pdf")])
    if path:
        cover_letter_path = path
        btn_cover_letter.config(text=f"Cover Letter: {os.path.basename(path)}")
        logging.info(f"Cover letter path selected: {path}")
        update_status(f"Cover letter selected: {os.path.basename(path)}", "green")

def on_user_input_change(event=None):
    """Triggers an auto-save after a short delay to avoid saving on every keypress."""
    global save_after_id
    if save_after_id:
        root.after_cancel(save_after_id)
    save_after_id = root.after(1000, save_data)  # save after 1 sec idle

def update_status(message, color="white"):
    """Updates the status bar text on the GUI."""
    status_label.config(text=f"Status: {message}", fg=color)

def on_recipients_change(event=None):
    """Handles changes in the recipients list text widget."""
    on_user_input_change(event)
    recipients_text = text_recipients.get("1.0", tk.END).strip()
    valid_list, _ = validate_recipients(recipients_text)
    emails_to_send_var.set(f"Remaining: {len(valid_list)}")

# New function to reset the sent email counter (lifetime)
def reset_sent_count():
    """Resets the lifetime sent email counter to zero and updates the label."""
    global sent_email_count
    sent_email_count = 0
    sent_email_count_var.set(f"Sent: {sent_email_count}")
    update_status("Sent email counter has been reset.", "green")
    save_data()

def connect_smtp(sender_email, app_password):
    """Establishes an SMTP connection and logs in."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, app_password)
    logging.info("SMTP connection established and logged in.")
    return server

def stop_sending():
    """Sets a flag to stop the email sending thread gracefully."""
    global stop_flag
    stop_flag = True
    btn_send.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)
    update_status("Stopping email sending...", "orange")
    # Clear the interval bar
    interval_progress['value'] = 0

def update_recipient_text_widget(recipients_list):
    """Updates the recipient text widget on the main thread."""
    text_recipients.delete("1.0", tk.END)
    for row in recipients_list:
        text_recipients.insert(tk.END, f"{row['Email']},{row['Position']}\n")

# --- Recipient Validation ---
def validate_recipients(recipients_text):
    """
    Validates recipient data from the text widget.
    Returns a tuple of (valid_recipients, invalid_recipients).
    """
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

def check_recipients_and_update_gui():
    """
    Called by the 'Check Recipients' button. Validates the list and highlights invalid entries.
    """
    recipients_text = text_recipients.get("1.0", tk.END).strip()
    if not recipients_text:
        messagebox.showinfo("Info", "Recipient list is empty.")
        return

    text_recipients.tag_remove('error', '1.0', tk.END)
    valid_list, invalid_list = validate_recipients(recipients_text)

    log_output.delete(1.0, tk.END)

    if invalid_list:
        log_output.insert(tk.END, "⚠️ Found the following invalid entries. They are highlighted in red. Please fix or remove them.\n", 'error')
        lines = recipients_text.splitlines()
        for item in invalid_list:
            try:
                line_number = lines.index(item['line']) + 1
                start_index = f"{line_number}.0"
                end_index = f"{line_number}.0 + {len(item['line'])}c"
                text_recipients.tag_add('error', start_index, end_index)
                log_output.insert(tk.END, f"  - '{item['line']}' -> Reason: {item['reason']}\n", 'error')
            except ValueError:
                log_output.insert(tk.END, f"  - Could not find and highlight: '{item['line']}' -> Reason: {item['reason']}\n", 'error')
        messagebox.showwarning("Validation Issues", f"Found {len(invalid_list)} invalid entries. They have been highlighted. Check the log for details.")
        update_status("Recipient list contains errors. Check log and fix/remove them.", "red")
    else:
        messagebox.showinfo("Success", "All recipient entries are valid!")
        update_status("Recipient list is clean.", "green")

    on_recipients_change()

def remove_invalid_recipients():
    """Removes all currently highlighted invalid recipients from the list."""
    recipients_text = text_recipients.get("1.0", tk.END).strip()
    if not recipients_text:
        messagebox.showinfo("Info", "Recipient list is empty.")
        return
    valid_list, invalid_list = validate_recipients(recipients_text)
    if not invalid_list:
        messagebox.showinfo("Info", "No invalid entries to remove.")
        return
    update_recipient_text_widget(valid_list)
    on_recipients_change()
    log_output.insert(tk.END, f"✅ Removed {len(invalid_list)} invalid entries from the list.\n")
    update_status("Invalid entries have been removed.", "green")

# --------------------------
# Sending Logic
# --------------------------

def send_emails():
    """
    Main function to initiate the email sending process in a separate thread.
    Handles input validation and thread management.
    """
    global send_thread, stop_flag, sent_email_count, emails_to_send_count, daily_sent_count, daily_sent_date

    # Check if a thread is already running to prevent duplicates
    if send_thread and send_thread.is_alive():
        messagebox.showwarning("Warning", "Email sending is already in progress.")
        return

    btn_send.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)

    log_output.delete(1.0, tk.END)
    progress_bar['value'] = 0
    interval_progress['value'] = 0

    sender_email = entry_email.get().strip()
    app_password = entry_password.get().strip()
    subject_template = entry_subject.get().strip()
    body_template = text_body.get("1.0", tk.END).strip()
    recipients_text = text_recipients.get("1.0", tk.END).strip()

    if not (sender_email and app_password and subject_template and body_template and recipients_text):
        messagebox.showerror("Error", "Please fill all fields including recipient list.")
        btn_send.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)
        return

    if not resume_path:
        messagebox.showerror("Error", "Please select your Resume PDF file.")
        btn_send.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)
        return

    # Validate recipients first
    recipients, invalid_recipients = validate_recipients(recipients_text)
    if invalid_recipients:
        log_output.insert(tk.END, "⚠️ Cannot start sending. Invalid entries found. Please fix or click 'Remove Invalid' to proceed.\n", 'error')
        messagebox.showerror("Validation Error", "Please correct the recipient list before sending. Check the log for details.")
        btn_send.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)
        return

    total = len(recipients)
    progress_bar['maximum'] = total
    emails_to_send_count = total

    # Reset / roll daily counter if date changed
    if daily_sent_date != today_str():
        daily_sent_date = today_str()
        daily_sent_count = 0
        save_data()

    def set_interval_style_wait():
        interval_progress.configure(style="Wait.Horizontal.TProgressbar")

    def set_interval_style_send():
        interval_progress.configure(style="Send.Horizontal.TProgressbar")

    def animate_wait(seconds):
        """Animate the interval progress bar for 'seconds' while the background thread sleeps in chunks."""
        try:
            interval_progress['maximum'] = max(1, int(seconds))
        except Exception:
            interval_progress['maximum'] = 1
        interval_progress['value'] = 0
        set_interval_style_wait()

        # We will tick every 0.5s to keep UI smooth
        step = 0.5
        ticks = int(seconds / step)
        current = 0

        def tick():
            nonlocal current, ticks, step
            if stop_flag or current >= ticks:
                # Fill bar when done or stopped
                interval_progress['value'] = interval_progress['maximum']
                return
            interval_progress['value'] = min(interval_progress['maximum'], int(current * step))
            current += 1
            root.after(int(step * 1000), tick)

        root.after(0, tick)

    def job(recipients_list):
        nonlocal sender_email, app_password, subject_template, body_template, total
        global stop_flag, sent_email_count, emails_to_send_count, daily_sent_count, daily_sent_date

        update_status("Connecting to SMTP server...", "yellow")
        server = None
        try:
            server = connect_smtp_with_retries(sender_email, app_password)
            update_status("SMTP connection successful. Preparing to send...", "green")
        except smtplib.SMTPAuthenticationError:
            root.after(0, lambda: messagebox.showerror("Login Failed", "Authentication failed. Please check your Gmail email and App Password. Ensure you have 2-Step Verification enabled and are using an App Password, not your regular Gmail password."))
            root.after(0, lambda: btn_send.config(state=tk.NORMAL))
            root.after(0, lambda: btn_stop.config(state=tk.DISABLED))
            logging.error("SMTP login failed due to authentication error.")
            update_status("Error: Authentication failed.", "red")
            return
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Login failed after {MAX_INITIAL_CONNECT_RETRIES} attempts: {e}"))
            root.after(0, lambda: btn_send.config(state=tk.NORMAL))
            root.after(0, lambda: btn_stop.config(state=tk.DISABLED))
            logging.error(f"Initial SMTP login failed after retries: {e}")
            update_status("Error: Initial SMTP login failed.", "red")
            return

        # Gradual start
        initial_wait = random.uniform(INITIAL_START_MIN, INITIAL_START_MAX)
        root.after(0, lambda: log_output.insert(tk.END, f"🕘 Reading through recipient list and preparing files... (about {int(initial_wait)}s)\n"))
        root.after(0, set_interval_style_wait)
        root.after(0, lambda: animate_wait(initial_wait))
        slept = 0.0
        while slept < initial_wait and not stop_flag:
            time.sleep(0.5)
            slept += 0.5

        sent_count_in_session = 0
        since_last_break = 0
        next_break_after = random.randint(BATCH_MIN, BATCH_MAX)

        while recipients_list and not stop_flag:
            # Daily limit check
            if daily_sent_count >= DAILY_LIMIT:
                msg = f"🚫 Daily limit of {DAILY_LIMIT} emails reached — stopping for today.\n"
                root.after(0, lambda: log_output.insert(tk.END, msg, 'error'))
                update_status(f"Daily limit reached ({DAILY_LIMIT}).", "red")
                break

            row = recipients_list[0]
            recipient = row['Email']
            position = row['Position']

            # Compose subject/body with placeholders
            subject = subject_template.replace("{position}", position)
            body = body_template.replace("{position}", position)

            # Human-like preparation logs
            root.after(0, lambda r=recipient, p=position: log_output.insert(
                tk.END, f"📝 Drafting email to {r} for '{p}'. Reviewing content and attachments...\n"))
            set_interval_style_send()
            interval_progress['maximum'] = 1
            interval_progress['value'] = 1

            # Build message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Attach resume
            try:
                with open(resume_path, "rb") as f:
                    part = MIMEBase('application', 'pdf')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(resume_path)}')
                    msg.attach(part)
                root.after(0, lambda: log_output.insert(tk.END, "📎 Attaching resume... done.\n"))
            except Exception as e:
                root.after(0, lambda r=recipient: log_output.insert(tk.END, f"⚠️ Could not attach resume for {r}: {e}\n"))
                logging.error(f"Could not attach resume for {recipient}: {e}")

            # Attach cover letter if selected
            if cover_letter_path:
                try:
                    with open(cover_letter_path, "rb") as f:
                        part = MIMEBase('application', 'pdf')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(cover_letter_path)}')
                        msg.attach(part)
                    root.after(0, lambda: log_output.insert(tk.END, "📄 Attaching cover letter... done.\n"))
                except Exception as e:
                    root.after(0, lambda r=recipient: log_output.insert(tk.END, f"⚠️ Could not attach cover letter for {r}: {e}\n"))
                    logging.error(f"Could not attach cover letter for {recipient}: {e}")

            # Typing simulation before sending
            typing_wait = random.uniform(TYPING_MIN, TYPING_MAX)
            root.after(0, lambda: log_output.insert(tk.END, f"⌨️ Final check before sending... (about {typing_wait:.1f}s)\n"))
            # Show green briefly to indicate "sending soon"
            set_interval_style_send()
            interval_progress['maximum'] = 1
            interval_progress['value'] = 1
            slept_local = 0.0
            while slept_local < typing_wait and not stop_flag:
                time.sleep(0.2)
                slept_local += 0.2

            # Attempt to send with retries
            email_sent = False
            retries = 0
            while not email_sent and retries < MAX_RECONNECT_RETRIES and not stop_flag:
                try:
                    server.sendmail(sender_email, recipient, msg.as_string())
                    root.after(0, lambda r=recipient, p=position: log_output.insert(tk.END, f"✅ Sent to {r} ({p})\n"))
                    logging.info(f"Successfully sent email to {recipient}")
                    email_sent = True
                except smtplib.SMTPResponseException as e:
                    if e.smtp_code == 421 or 400 <= e.smtp_code < 500:
                        retries += 1
                        root.after(0, lambda r=recipient, ret=retries: log_output.insert(
                            tk.END, f"⚠️ SMTP {e.smtp_code}. Reconnecting (retry {ret}/{MAX_RECONNECT_RETRIES}) for {r}...\n"))
                        logging.warning(f"SMTP error {e.smtp_code} for {recipient}. Attempting reconnect.")
                        try:
                            server.quit()
                        except:
                            pass
                        try:
                            server = connect_smtp_with_retries(sender_email, app_password, max_retries=MAX_RECONNECT_RETRIES)
                        except Exception as e2:
                            root.after(0, lambda r=recipient, error_msg=e2: log_output.insert(
                                tk.END, f"❌ Failed to reconnect SMTP for {r} after {MAX_RECONNECT_RETRIES} attempts: {error_msg}\n"))
                            logging.error(f"Failed to reconnect SMTP for {recipient} after retries: {e2}")
                            break
                    else:
                        root.after(0, lambda r=recipient, error_msg=e: log_output.insert(
                            tk.END, f"❌ Permanent SMTP error for {r}: {error_msg}\n"))
                        logging.error(f"Permanent SMTP error for {recipient}: {e}")
                        break
                except Exception as e:
                    retries += 1
                    root.after(0, lambda r=recipient, error_msg=e: log_output.insert(
                        tk.END, f"❌ Failed to send to {r}: {error_msg} (retry {retries}/{MAX_RECONNECT_RETRIES})\n"))
                    logging.error(f"Unexpected error sending email to {recipient}: {e}")
                    try:
                        server.quit()
                    except:
                        pass
                    if retries < MAX_RECONNECT_RETRIES:
                        try:
                            server = connect_smtp_with_retries(sender_email, app_password, max_retries=MAX_RECONNECT_RETRIES)
                        except Exception as e2:
                            root.after(0, lambda r=recipient, error_msg=e2: log_output.insert(
                                tk.END, f"❌ Failed to reconnect SMTP for {r} after {MAX_RECONNECT_RETRIES} attempts: {error_msg}\n"))
                            logging.error(f"Failed to reconnect SMTP for {recipient} after retries: {e2}")
                            break
                    else:
                        break

            if email_sent:
                # Remove recipient from list and update counters
                recipients_list.pop(0)
                sent_count_in_session += 1
                since_last_break += 1
                sent_email_count += 1
                daily_sent_count += 1
                save_data()
                emails_to_send_count -= 1

                # Update UI counters
                root.after(0, lambda c=sent_count_in_session: progress_bar.config(value=c))
                root.after(0, lambda: sent_email_count_var.set(f"Sent: {sent_email_count}"))
                root.after(0, lambda: emails_to_send_var.set(f"Remaining: {emails_to_send_count}"))
                root.after(0, lambda: update_recipient_text_widget(recipients_list))

                # Scheduled reconnect to keep session healthy
                if (sent_count_in_session > 0 and sent_count_in_session % RECONNECT_EVERY == 0) and not stop_flag:
                    root.after(0, lambda: log_output.insert(tk.END, f"🔄 Reconnecting SMTP after {RECONNECT_EVERY} emails to keep the session fresh...\n"))
                    update_status("Reconnecting SMTP server...", "yellow")
                    try:
                        server.quit()
                    except:
                        pass
                    try:
                        server = connect_smtp(sender_email, app_password)
                        update_status("Reconnection successful.", "green")
                    except Exception as e:
                        root.after(0, lambda: log_output.insert(tk.END, f"❌ Failed to reconnect SMTP: {e}\n"))
                        logging.error(f"Failed to reconnect SMTP during scheduled reconnect: {e}")
                        update_status("Error: Failed to reconnect SMTP.", "red")
                        break
            else:
                update_status(f"Failed to send to {recipient}. Check log for details.", "red")
                break

            root.after(0, lambda: log_output.see(tk.END))

            # Batch break logic
            if since_last_break >= next_break_after and not stop_flag and recipients_list:
                break_seconds = random.uniform(BATCH_BREAK_MIN, BATCH_BREAK_MAX)
                root.after(0, lambda s=int(break_seconds): log_output.insert(
                    tk.END, f"☕ Taking a short review break for about {s//60}m {s%60}s before continuing...\n"))
                since_last_break = 0
                next_break_after = random.randint(BATCH_MIN, BATCH_MAX)

                # Animate and sleep for the break
                root.after(0, lambda: animate_wait(break_seconds))
                slept_break = 0.0
                while slept_break < break_seconds and not stop_flag:
                    time.sleep(0.5)
                    slept_break += 0.5

            if stop_flag or not recipients_list:
                break

            # Randomized delay between sends (human-like)
            base = random.uniform(BASE_DELAY_MIN, BASE_DELAY_MAX)
            variation = base * DELAY_VARIATION
            actual_delay = max(0.5, base + random.uniform(-variation, variation))

            root.after(0, lambda s=int(actual_delay): log_output.insert(
                tk.END, f"⏳ Waiting about {s//60}m {s%60}s before the next email...\n"))
            root.after(0, lambda: animate_wait(actual_delay))

            # Sleep in small chunks to remain responsive to "Stop"
            slept_delay = 0.0
            while slept_delay < actual_delay and not stop_flag:
                time.sleep(0.5)
                slept_delay += 0.5

        # Cleanup after the loop
        if server:
            try:
                server.quit()
            except:
                pass

        root.after(0, lambda: btn_send.config(state=tk.NORMAL))
        root.after(0, lambda: btn_stop.config(state=tk.DISABLED))
        root.after(0, lambda: interval_progress.config(value=0))

        if daily_sent_count >= DAILY_LIMIT:
            # Daily limit reached
            root.after(0, lambda: messagebox.showwarning("Daily Limit Reached",
                                                         f"Daily limit of {DAILY_LIMIT} emails reached — stopping for today."))
            update_status(f"Daily limit reached ({DAILY_LIMIT}).", "red")
        elif not stop_flag and not recipients_list:
            root.after(0, lambda: messagebox.showinfo("Done", "All emails have been sent!"))
            update_status("All emails have been sent!", "green")
        elif stop_flag:
            root.after(0, lambda: messagebox.showinfo("Stopped", "Email sending was stopped by the user."))
            update_status("Sending stopped by user.", "orange")
        else:
            root.after(0, lambda: messagebox.showwarning("Incomplete", "Email sending stopped due to an error. Please check the log."))
            update_status("Sending stopped due to an error. Check log.", "red")

        stop_flag = False
        logging.info("Email sending job finished.")

    # --- FIX: Actually start the sending thread ---
    send_thread = threading.Thread(target=job, args=(recipients,))
    send_thread.daemon = True
    send_thread.start()

def connect_smtp_with_retries(sender_email, app_password, max_retries=MAX_INITIAL_CONNECT_RETRIES):
    """Tries to connect to SMTP server with retries."""
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            server = connect_smtp(sender_email, app_password)
            return server
        except Exception as e:
            last_exception = e
            logging.warning(f"SMTP connect attempt {attempt} failed: {e}")
            time.sleep(2)  # Wait before retrying
    raise last_exception

# --------------------------
# GUI Setup
# --------------------------

root = tk.Tk()
root.title("Job Application Email Sender with Attachments")
root.geometry("950x900")
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# --- Dark Mode Colors ---
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
DARK_MODE_WAIT_FG = "#ffd966"  # softer yellow for waiting bar

root.configure(bg=DARK_MODE_BG)

# Configure ttk style for dark mode
style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background=DARK_MODE_BG, foreground=DARK_MODE_FG)
style.configure("TButton", background=DARK_MODE_BUTTON_BG, foreground=DARK_MODE_BUTTON_FG, borderwidth=1, relief="flat")
style.map("TButton", background=[('active', DARK_MODE_BUTTON_BG)])
style.configure("TProgressbar", background=DARK_MODE_SUCCESS_FG, troughcolor=DARK_MODE_INPUT_BG)

# NEW styles for interval bar
style.configure("Wait.Horizontal.TProgressbar", background=DARK_MODE_WAIT_FG, troughcolor=DARK_MODE_INPUT_BG)
style.configure("Send.Horizontal.TProgressbar", background=DARK_MODE_SUCCESS_FG, troughcolor=DARK_MODE_INPUT_BG)

for i in range(16):  # Now a total of 16 rows
    if i == 7:
        root.rowconfigure(i, weight=2)
    elif i == 9:
        root.rowconfigure(i, weight=5)
    elif i == 14:  # Row for log frame
        root.rowconfigure(i, weight=3)
    elif i == 13:  # Row for counter frame
        root.rowconfigure(i, weight=1)
    else:
        root.rowconfigure(i, weight=0)

tk.Label(root, text="Your Gmail:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=0, column=0, sticky="w", padx=10, pady=2)
entry_email = tk.Entry(root, width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
entry_email.grid(row=0, column=1, padx=10, pady=2, sticky="ew")

tk.Label(root, text="App Password:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=1, column=0, sticky="w", padx=10, pady=2)
entry_password = tk.Entry(root, show='*', width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
entry_password.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

app_pass_info = tk.Label(
    root,
    text="⚠ Gmail App Password is NOT your normal Gmail password.\nYou must enable 2-Step Verification and generate one.",
    fg=DARK_MODE_WARNING_FG,
    bg=DARK_MODE_BG,
    justify="left",
    wraplength=700
)
app_pass_info.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0,5))

link_label = tk.Label(root, text="Learn how to get an App Password", fg="cyan", bg=DARK_MODE_BG, cursor="hand2")
link_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(0,10))
link_label.bind("<Button-1>", lambda e: open_app_password_help())

frame_buttons = tk.Frame(root, bg=DARK_MODE_BG)
frame_buttons.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=5)

btn_choose_folder = tk.Button(frame_buttons, text="Choose Save Folder", command=choose_save_folder, width=20, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_choose_folder.pack(side=tk.LEFT, padx=(0, 5))

btn_load_prev = tk.Button(frame_buttons, text="Load Data from Previous Software", command=load_data_from_previous, width=30, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_load_prev.pack(side=tk.LEFT, padx=(0, 5))

btn_resume = tk.Button(frame_buttons, text="Select Resume PDF", command=select_resume, width=20, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_resume.pack(side=tk.LEFT, padx=(0, 5))

btn_cover_letter = tk.Button(frame_buttons, text="Select Cover Letter PDF (Optional)", command=select_cover_letter, width=30, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_cover_letter.pack(side=tk.LEFT)

# Frame for tools & send buttons (right-aligned)
frame_send_stop = tk.Frame(root, bg=DARK_MODE_BG)
frame_send_stop.grid(row=4, column=1, sticky="e", padx=(50, 10), pady=5)

btn_check_recipients = tk.Button(frame_send_stop, text="Check Recipients", command=check_recipients_and_update_gui, width=15, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_check_recipients.pack(side=tk.LEFT, padx=(0, 5))

btn_remove_invalid = tk.Button(frame_send_stop, text="Remove Invalid", command=remove_invalid_recipients, width=15, height=1, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_remove_invalid.pack(side=tk.LEFT, padx=(0, 5))

btn_send = tk.Button(frame_send_stop, text="Send Emails", command=send_emails, bg=DARK_MODE_SUCCESS_FG, fg=DARK_MODE_BG, width=15, height=1)
btn_send.pack(side=tk.LEFT, padx=(0, 5))

btn_stop = tk.Button(frame_send_stop, text="Stop Sending", command=stop_sending, state=tk.DISABLED, bg=DARK_MODE_ERROR_FG, fg=DARK_MODE_FG, width=15, height=1)
btn_stop.pack(side=tk.LEFT)

label_save_folder = tk.Label(root, text="", fg=DARK_MODE_FG, bg=DARK_MODE_BG, justify="left", wraplength=700)
label_save_folder.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(0,10))
if save_folder:
    label_save_folder.config(text=f"Data will be saved in:\n{save_folder}")
else:
    label_save_folder.config(text="No save folder selected. Data will NOT be saved until you choose a folder.")

tk.Label(root, text="Email Subject ({position} placeholder):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=6, column=0, sticky="w", padx=10, pady=2)
entry_subject = tk.Entry(root, width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
entry_subject.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

tk.Label(root, text="Email Body:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=7, column=0, sticky="nw", padx=10, pady=2)

# Text + Scrollbar for body
frame_body = tk.Frame(root, bg=DARK_MODE_BG)
frame_body.grid(row=7, column=1, padx=10, pady=2, sticky="nsew")

text_body = tk.Text(frame_body, height=8, width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
text_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_body = tk.Scrollbar(frame_body, command=text_body.yview)
scroll_body.pack(side=tk.RIGHT, fill=tk.Y)

text_body.config(yscrollcommand=scroll_body.set)

tk.Label(root, text="Recipients (email,position per line):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=9, column=0, sticky="nw", padx=10, pady=2)
frame_recipients = tk.Frame(root, bg=DARK_MODE_BG)
frame_recipients.grid(row=9, column=1, padx=10, pady=2, sticky="nsew")

text_recipients = tk.Text(frame_recipients, height=14, width=80, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
text_recipients.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_recipients = tk.Scrollbar(frame_recipients, command=text_recipients.yview)
scroll_recipients.pack(side=tk.RIGHT, fill=tk.Y)

text_recipients.config(yscrollcommand=scroll_recipients.set)

# NEW: Frame to hold counters
frame_counters = tk.Frame(root, bg=DARK_MODE_BG)
frame_counters.grid(row=10, column=0, sticky="w", padx=10, pady=2)

# Counter for remaining emails
emails_to_send_var = tk.StringVar(value=f"Remaining: 0")
emails_to_send_label = tk.Label(frame_counters, textvariable=emails_to_send_var, justify="left", fg="yellow", bg=DARK_MODE_BG)
emails_to_send_label.pack(side=tk.LEFT, padx=(0, 20))

# NEW: Interval progress bar (repurposed)
frame_interval = tk.Frame(root, bg=DARK_MODE_BG)
frame_interval.grid(row=10, column=1, sticky="e", padx=10, pady=2)
interval_progress = ttk.Progressbar(frame_interval, orient='horizontal', length=250, mode='determinate', style="Wait.Horizontal.TProgressbar")
interval_progress.pack(side=tk.LEFT, fill=tk.X)

# Total progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=800, mode='determinate')
progress_bar.grid(row=12, column=0, columnspan=2, sticky="ew", padx=10, pady=(0,10))

# Frame for sent counter and reset button
frame_counter = tk.Frame(root, bg=DARK_MODE_BG)
frame_counter.grid(row=13, column=0, columnspan=2, sticky="w", padx=10, pady=(5,0))

sent_email_count_var = tk.StringVar(value=f"Sent: {sent_email_count}")
sent_count_label = tk.Label(frame_counter, textvariable=sent_email_count_var, justify="left", bg=DARK_MODE_BG, fg=DARK_MODE_FG)
sent_count_label.pack(side=tk.LEFT, padx=(0, 10))

btn_reset_count = tk.Button(frame_counter, text="Reset Counter", command=reset_sent_count, bg=DARK_MODE_BUTTON_BG, fg=DARK_MODE_BUTTON_FG)
btn_reset_count.pack(side=tk.LEFT)

tk.Label(root, text="Log:", bg=DARK_MODE_BG, fg=DARK_MODE_FG).grid(row=14, column=0, sticky="nw", padx=10, pady=2)
frame_log = tk.Frame(root, bg=DARK_MODE_BG)
frame_log.grid(row=14, column=1, padx=10, pady=(2,5), sticky="nsew")

log_output = tk.Text(frame_log, width=100, height=12, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
log_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_log = tk.Scrollbar(frame_log, command=log_output.yview)
scroll_log.pack(side=tk.RIGHT, fill=tk.Y)

log_output.config(yscrollcommand=scroll_log.set)
log_output.tag_configure('error', foreground=DARK_MODE_ERROR_FG)

# Status label
status_label = tk.Label(root, text="Status: Ready to send.", fg=DARK_MODE_SUCCESS_FG, justify="left", wraplength=700, bg=DARK_MODE_BG)
status_label.grid(row=15, column=0, columnspan=2, sticky="w", padx=10, pady=(5,10))

save_after_id = None
entry_subject.bind("<KeyRelease>", on_user_input_change)
text_body.bind("<KeyRelease>", on_user_input_change)
entry_email.bind("<KeyRelease>", on_user_input_change)
entry_password.bind("<KeyRelease>", on_user_input_change)
text_recipients.bind("<KeyRelease>", on_recipients_change)

# Load config and data on startup
app_config = load_config()
save_folder = app_config.get("save_folder")
if save_folder:
    label_save_folder.config(text=f"Data will be saved in:\n{save_folder}")
    load_data()
    update_status("Ready to send.", DARK_MODE_SUCCESS_FG)
else:
    label_save_folder.config(text="No save folder selected. Data will NOT be saved until you choose a folder.")
    update_status("Please select a save folder to begin.", DARK_MODE_WARNING_FG)

# Initial update of the remaining counter
on_recipients_change()

root.mainloop()