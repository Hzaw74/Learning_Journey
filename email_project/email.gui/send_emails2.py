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
import re # Import the regular expression module

# Set up basic logging for debugging purposes
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_FILE = "config.json"
DATA_FILENAME = "saved_data.json"

resume_path = None
cover_letter_path = None

save_folder = None # Global save folder path

send_thread = None
stop_flag = False

# How many emails to send before reconnecting SMTP to prevent timeouts
RECONNECT_EVERY = 20
MAX_RECONNECT_RETRIES = 3 # New constant for retries on a single email send failure
MAX_INITIAL_CONNECT_RETRIES = 3  # Number of times to retry initial SMTP connection

# Global variable for tracking sent emails
sent_email_count = 0
# New global variable for tracking remaining emails
emails_to_send_count = 0

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
        "sent_email_count": sent_email_count
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
    global sent_email_count, first_load_done
    path = get_data_filepath()
    if not path or not os.path.exists(path):
        update_status("No saved data found.", "orange")
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
        # Only update sent_email_count on first load (startup)
        if not first_load_done:
            sent_email_count = data.get("sent_email_count", 0)
            first_load_done = True
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

def update_remaining_count(recipients_text):
    """Counts the number of valid recipient lines and updates the remaining counter."""
    # We now count the valid recipients, which are not tagged as 'error'
    lines = recipients_text.splitlines()
    count = 0
    for i, line in enumerate(lines, 1):
        # We need to get the tags for the line to check if it's an error
        # This is a bit tricky with tkinter, so we will use the validation function directly.
        pass # The actual count is now handled after validation

def on_recipients_change(event=None):
    """Handles changes in the recipients list text widget."""
    on_user_input_change(event)
    recipients_text = text_recipients.get("1.0", tk.END).strip()
    valid_list, _ = validate_recipients(recipients_text)
    emails_to_send_var.set(f"Remaining: {len(valid_list)}")
    
    # --- NEW: Update the estimated time when recipients change ---
    try:
        delay_sec = float(entry_delay.get().strip())
    except ValueError:
        delay_sec = 0

    remaining_emails = len(valid_list)
    remaining_seconds = remaining_emails * delay_sec
    minutes, seconds = divmod(remaining_seconds, 60)
    estimated_time_var.set(f"Estimated Time: {int(minutes)}m {int(seconds)}s")
    # --- END NEW ---

# New function to reset the sent email counter
def reset_sent_count():
    """Resets the sent email counter to zero and updates the label."""
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
    estimated_time_var.set("Estimated Time: --") # Reset time estimate

def update_recipient_text_widget(recipients_list):
    """Updates the recipient text widget on the main thread."""
    text_recipients.delete("1.0", tk.END)
    for row in recipients_list:
        text_recipients.insert(tk.END, f"{row['Email']},{row['Position']}\n")

# --- MODIFIED: Recipient Validation and Check function ---
def validate_recipients(recipients_text):
    """
    Validates recipient data from the text widget.
    Returns a tuple of (valid_recipients, invalid_recipients).
    """
    valid_recipients = []
    invalid_recipients = []
    # A simple regex for basic email format validation
    email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')

    for line in recipients_text.splitlines():
        line = line.strip()
        if not line:
            continue

        parts = line.split(",", 1)
        
        # Check if the line has exactly two parts
        if len(parts) != 2:
            invalid_recipients.append({"line": line, "reason": "Incorrect format (missing comma or extra data)."})
            continue
        
        email = parts[0].strip()
        position = parts[1].strip()

        # Check for valid email format and non-empty position
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
    
    # First, clear any previous error tags
    text_recipients.tag_remove('error', '1.0', tk.END)
        
    valid_list, invalid_list = validate_recipients(recipients_text)
    
    log_output.delete(1.0, tk.END)
    
    if invalid_list:
        log_output.insert(tk.END, "⚠️ Found the following invalid entries. They are highlighted in red. Please fix or remove them.\n", 'error')
        
        # Highlight each invalid line
        lines = recipients_text.splitlines()
        for item in invalid_list:
            # Find the line number of the invalid item
            try:
                line_number = lines.index(item['line']) + 1
                start_index = f"{line_number}.0"
                end_index = f"{line_number}.0 + {len(item['line'])}c"
                text_recipients.tag_add('error', start_index, end_index)
                
                # Log the reason for the error
                log_output.insert(tk.END, f"  - '{item['line']}' -> Reason: {item['reason']}\n", 'error')
            except ValueError:
                # In case the line can't be found (e.g., due to whitespace issues)
                log_output.insert(tk.END, f"  - Could not find and highlight: '{item['line']}' -> Reason: {item['reason']}\n", 'error')

        messagebox.showwarning("Validation Issues", f"Found {len(invalid_list)} invalid entries. They have been highlighted. Check the log for details.")
        update_status("Recipient list contains errors. Check log and fix/remove them.", "red")
    else:
        messagebox.showinfo("Success", "All recipient entries are valid!")
        update_status("Recipient list is clean.", "green")

    on_recipients_change() # Re-calculate remaining count

def remove_invalid_recipients():
    """Removes all currently highlighted invalid recipients from the list."""
    recipients_text = text_recipients.get("1.0", tk.END).strip()
    if not recipients_text:
        messagebox.showinfo("Info", "Recipient list is empty.")
        return
    
    # Get the valid list from the validation function
    valid_list, invalid_list = validate_recipients(recipients_text)

    if not invalid_list:
        messagebox.showinfo("Info", "No invalid entries to remove.")
        return

    # Update the text widget with only the valid entries
    update_recipient_text_widget(valid_list)
    on_recipients_change() # Re-calculate remaining count
    log_output.insert(tk.END, f"✅ Removed {len(invalid_list)} invalid entries from the list.\n")
    update_status("Invalid entries have been removed.", "green")
# --- END MODIFIED FUNCTIONS ---


def send_emails():
    """
    Main function to initiate the email sending process in a separate thread.
    Handles input validation and thread management.
    """
    global send_thread, stop_flag, sent_email_count, emails_to_send_count

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

    try:
        delay_sec = float(entry_delay.get().strip())
    except ValueError:
        messagebox.showerror("Error", "Interval must be a valid number (seconds).")
        btn_send.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)
        return

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
        
    # --- Check for invalid recipients before starting ---
    recipients, invalid_recipients = validate_recipients(recipients_text)
    
    if invalid_recipients:
        log_output.insert(tk.END, "⚠️ Cannot start sending. Invalid entries found. Please fix or click 'Remove Invalid' to proceed.\n", 'error')
        messagebox.showerror("Validation Error", "Please correct the recipient list before sending. Check the log for details.")
        btn_send.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)
        return
    # --- END CHECK ---

    total = len(recipients)
    progress_bar['maximum'] = total
    interval_progress['maximum'] = delay_sec
    emails_to_send_count = total # Initialize the new counter

    def update_interval_progress(seconds):
        """Updates the interval progress bar on the GUI."""
        interval_progress['value'] = 0
        interval_step = 0.1  # update every 0.1 sec
        increments = int(seconds / interval_step)
        count = 0

        def step():
            nonlocal count
            if stop_flag:
                interval_progress['value'] = 0
                return
            if count > increments:
                interval_progress['value'] = interval_progress['maximum']
                return
            interval_progress['value'] = count * interval_step
            count += 1
            root.after(int(interval_step * 1000), step)
        step()

    def job(recipients_list):
        """
        The main email sending job running in a separate thread.
        It now modifies the recipients_list directly and updates the GUI.
        """
        nonlocal sender_email, app_password, subject_template, body_template, delay_sec, total
        global stop_flag, sent_email_count, emails_to_send_count

        update_status("Connecting to SMTP server...", "yellow")
        server = None
        try:
            # Use retry logic for initial connection
            server = connect_smtp_with_retries(sender_email, app_password)
            update_status("SMTP connection successful. Starting to send emails...", "green")
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Login failed after {MAX_INITIAL_CONNECT_RETRIES} attempts: {e}"))
            root.after(0, lambda: btn_send.config(state=tk.NORMAL))
            root.after(0, lambda: btn_stop.config(state=tk.DISABLED))
            logging.error(f"Initial SMTP login failed after retries: {e}")
            update_status("Error: Initial SMTP login failed.", "red")
            return

        sent_count_in_session = 0
        
        # Iterate over recipients and send emails
        while recipients_list and not stop_flag:
            row = recipients_list[0] # Peek at the first recipient
            recipient = row['Email']
            position = row['Position']

            update_status(f"Sending email to {recipient} for {position}...", "yellow")

            subject = subject_template.replace("{position}", position)
            body = body_template.replace("{position}", position)

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
                except Exception as e:
                    root.after(0, lambda r=recipient: log_output.insert(tk.END, f"⚠️ Could not attach cover letter for {r}: {e}\n"))
                    logging.error(f"Could not attach cover letter for {recipient}: {e}")

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
                        root.after(0, lambda r=recipient, ret=retries, max_ret=MAX_RECONNECT_RETRIES: log_output.insert(
                            tk.END, f"⚠️ SMTP error {e.smtp_code}. Attempting reconnect (retry {ret}/{max_ret}) for {r}...\n"))
                        logging.warning(f"SMTP error {e.smtp_code} for {recipient}. Attempting reconnect.")
                        try:
                            server.quit()
                        except:
                            pass
                        try:
                            # Use retry logic for reconnect
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
                    # Try reconnect if not max retries
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
                # Remove the recipient from the list and update the GUI
                recipients_list.pop(0)
                sent_count_in_session += 1
                sent_email_count += 1
                save_data()
                emails_to_send_count -= 1
                root.after(0, lambda c=sent_count_in_session: progress_bar.config(value=c))
                root.after(0, lambda: sent_email_count_var.set(f"Sent: {sent_email_count}"))
                root.after(0, lambda: emails_to_send_var.set(f"Remaining: {emails_to_send_count}"))
                root.after(0, lambda: update_recipient_text_widget(recipients_list))
                root.after(0, save_data)
                
                # --- NEW: Calculate and update estimated time after each send ---
                remaining_emails = len(recipients_list)
                remaining_seconds = remaining_emails * delay_sec
                minutes, seconds = divmod(remaining_seconds, 60)
                root.after(0, lambda m=minutes, s=seconds: estimated_time_var.set(f"Estimated Time: {int(m)}m {int(s)}s"))
                # --- END NEW ---

            else:
                # If all retries failed, add the recipient back to the list and break
                update_status(f"Failed to send to {recipient}. Check log for details.", "red")
                break

            root.after(0, lambda: log_output.see(tk.END))

            # Auto reconnect every RECONNECT_EVERY emails as a preventative measure
            if (sent_count_in_session > 0 and sent_count_in_session % RECONNECT_EVERY == 0) and not stop_flag:
                root.after(0, lambda: log_output.insert(tk.END, f"⚠️ Reconnecting SMTP server after {RECONNECT_EVERY} emails to prevent timeout...\n"))
                logging.info(f"Reconnecting SMTP after {RECONNECT_EVERY} emails.")
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

            if not stop_flag and recipients_list:
                root.after(0, update_interval_progress, delay_sec)
                slept = 0
                variation = random.uniform(-0.1, 0.1) * delay_sec
                actual_delay = max(0.1, delay_sec + variation)
                while slept < actual_delay and not stop_flag:
                    update_status(f"Waiting for {delay_sec - slept:.1f} seconds before next email...", "white")
                    time.sleep(0.1)
                    slept += 0.1

            if stop_flag:
                break

        # Cleanup after the loop
        if server:
            try:
                server.quit()
            except:
                pass

        root.after(0, lambda: btn_send.config(state=tk.NORMAL))
        root.after(0, lambda: btn_stop.config(state=tk.DISABLED))
        root.after(0, lambda: interval_progress.config(value=0))
        root.after(0, lambda: estimated_time_var.set("Estimated Time: Done")) # NEW: Update time at the end

        if not stop_flag and not recipients_list:
            root.after(0, lambda: messagebox.showinfo("Done", "All emails have been sent!"))
            update_status("All emails have been sent!", "green")
        elif stop_flag:
            root.after(0, lambda: messagebox.showinfo("Stopped", "Email sending was stopped by the user."))
            update_status("Sending stopped by user.", "orange")
        else: # This case is when an error broke the loop
            root.after(0, lambda: messagebox.showwarning("Incomplete", "Email sending stopped due to an error. Please check the log."))
            update_status("Sending stopped due to an error. Check log.", "red")

        stop_flag = False
        logging.info("Email sending job finished.")

    # CRITICAL FIX: The thread must be created and started for the job to run.
    stop_flag = False # Ensure stop flag is reset
    send_thread = threading.Thread(target=job, args=(recipients,), daemon=True) # daemon=True allows the main program to exit even if the thread is still running
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

# === GUI Setup ===
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

# Apply dark mode to the root window
root.configure(bg=DARK_MODE_BG)

# Configure ttk style for dark mode
style = ttk.Style()
style.theme_use('clam')  # Use a theme that supports styling
style.configure("TLabel", background=DARK_MODE_BG, foreground=DARK_MODE_FG)
style.configure("TButton", background=DARK_MODE_BUTTON_BG, foreground=DARK_MODE_BUTTON_FG, borderwidth=1, relief="flat")
style.map("TButton", background=[('active', DARK_MODE_BUTTON_BG)])
style.configure("TProgressbar", background=DARK_MODE_SUCCESS_FG, troughcolor=DARK_MODE_INPUT_BG)


for i in range(16): # Now a total of 16 rows
    if i == 7:
        root.rowconfigure(i, weight=2)
    elif i == 9:
        root.rowconfigure(i, weight=5)
    elif i == 14: # Row for log frame
        root.rowconfigure(i, weight=3)
    elif i == 13: # Row for counter frame
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

# Frame for Send and Stop buttons to place them aligned right with a gap
frame_send_stop = tk.Frame(root, bg=DARK_MODE_BG)
frame_send_stop.grid(row=4, column=1, sticky="e", padx=(50, 10), pady=5)

# MODIFIED BUTTONS: Check Recipients and NEW Remove Invalid button
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

# Added a Frame for Text + Scrollbar for body
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

# NEW: Frame to hold all the counters
frame_counters = tk.Frame(root, bg=DARK_MODE_BG)
frame_counters.grid(row=10, column=0, sticky="w", padx=10, pady=2)

# Counter for remaining emails
emails_to_send_var = tk.StringVar(value=f"Remaining: 0")
emails_to_send_label = tk.Label(frame_counters, textvariable=emails_to_send_var, justify="left", fg="yellow", bg=DARK_MODE_BG)
emails_to_send_label.pack(side=tk.LEFT, padx=(0, 20))

# Estimated time label - NEW
estimated_time_var = tk.StringVar(value="Estimated Time: --")
estimated_time_label = tk.Label(frame_counters, textvariable=estimated_time_var, justify="left", fg="yellow", bg=DARK_MODE_BG)
estimated_time_label.pack(side=tk.LEFT)


# New frame to group the interval controls and progress bar
frame_interval = tk.Frame(root, bg=DARK_MODE_BG)
frame_interval.grid(row=10, column=1, sticky="e", padx=10, pady=2)

tk.Label(frame_interval, text="Interval (seconds):", bg=DARK_MODE_BG, fg=DARK_MODE_FG).pack(side=tk.LEFT, padx=(0,5))
entry_delay = tk.Entry(frame_interval, width=10, bg=DARK_MODE_INPUT_BG, fg=DARK_MODE_INPUT_FG, insertbackground=DARK_MODE_FG)
entry_delay.pack(side=tk.LEFT, padx=(0,5))
entry_delay.insert(0, "120")

# Interval progress bar, now a child of frame_interval
interval_progress = ttk.Progressbar(frame_interval, orient='horizontal', length=150, mode='determinate')
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
text_recipients.bind("<KeyRelease>", on_recipients_change) # Bind recipient changes to a new function
entry_delay.bind("<KeyRelease>", on_recipients_change) # NEW: Also update time estimate if delay changes

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

# working final