import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import threading
import os

def send_emails():
    btn_send.config(state=tk.DISABLED)
    log_output.delete(1.0, tk.END)
    progress_bar['value'] = 0

    sender_email = entry_email.get().strip()
    app_password = entry_password.get().strip()
    subject_template = entry_subject.get().strip()
    body_template = text_body.get("1.0", tk.END).strip()
    csv_file = entry_csv.get().strip()
    try:
        delay_sec = float(entry_delay.get().strip())
    except:
        messagebox.showerror("Error", "Interval must be a valid number (seconds).")
        btn_send.config(state=tk.NORMAL)
        return

    if not (sender_email and app_password and subject_template and body_template and csv_file):
        messagebox.showerror("Error", "Please fill all fields and select CSV file.")
        btn_send.config(state=tk.NORMAL)
        return
    if not os.path.exists(csv_file):
        messagebox.showerror("Error", "CSV file does not exist.")
        btn_send.config(state=tk.NORMAL)
        return

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV: {e}")
        btn_send.config(state=tk.NORMAL)
        return

    if not {'Email', 'Position'}.issubset(df.columns):
        messagebox.showerror("Error", "CSV must have 'Email' and 'Position' columns.")
        btn_send.config(state=tk.NORMAL)
        return

    total = len(df)
    progress_bar['maximum'] = total

    recipients = df.to_dict('records')  # List of dicts for easy removal

    def job():
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
            btn_send.config(state=tk.NORMAL)
            return

        count = 0
        while recipients:
            row = recipients.pop(0)
            recipient = row['Email']
            position = str(row['Position'])

            subject = subject_template.replace("{position}", position)
            body = body_template.replace("{position}", position)

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            try:
                server.sendmail(sender_email, recipient, msg.as_string())
                log_output.insert(tk.END, f"✅ Sent to {recipient} ({position})\n")
            except Exception as e:
                log_output.insert(tk.END, f"❌ Failed to send to {recipient}: {e}\n")

            count += 1
            progress_bar['value'] = count
            log_output.see(tk.END)
            time.sleep(delay_sec)

        server.quit()
        messagebox.showinfo("Done", "All emails have been sent!")
        btn_send.config(state=tk.NORMAL)

    threading.Thread(target=job).start()

def browse_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    if filename:
        entry_csv.delete(0, tk.END)
        entry_csv.insert(0, filename)

# GUI setup
root = tk.Tk()
root.title("Job Application Email Sender with Progress")
root.geometry("650x650")

tk.Label(root, text="Your Gmail:").pack(anchor='w', padx=10, pady=2)
entry_email = tk.Entry(root, width=60)
entry_email.pack(padx=10)

tk.Label(root, text="App Password (use Gmail App Password):").pack(anchor='w', padx=10, pady=2)
entry_password = tk.Entry(root, show='*', width=60)
entry_password.pack(padx=10)

tk.Label(root, text="Email Subject (use {position} as placeholder):").pack(anchor='w', padx=10, pady=2)
entry_subject = tk.Entry(root, width=60)
entry_subject.pack(padx=10)
entry_subject.insert(0, "Application for {position}")

tk.Label(root, text="Email Body (use {position} as placeholder):").pack(anchor='w', padx=10, pady=2)
text_body = tk.Text(root, height=10, width=60)
text_body.pack(padx=10)
text_body.insert(tk.END,
    "Dear Hiring Manager,\n\n"
    "I am writing to express my interest in the {position} position.\n"
    "Please find my resume attached.\n\n"
    "Thank you for your time and consideration.\n\n"
    "Best regards,\n"
    "[Your Name]"
)

tk.Label(root, text="Select CSV File (must have Email,Position columns):").pack(anchor='w', padx=10, pady=2)
frame_csv = tk.Frame(root)
frame_csv.pack(padx=10, fill='x')
entry_csv = tk.Entry(frame_csv, width=50)
entry_csv.pack(side='left', fill='x', expand=True)
btn_browse = tk.Button(frame_csv, text="Browse", command=browse_csv)
btn_browse.pack(side='left', padx=5)

tk.Label(root, text="Interval between emails (seconds):").pack(anchor='w', padx=10, pady=2)
entry_delay = tk.Entry(root, width=10)
entry_delay.pack(padx=10)
entry_delay.insert(0, "120")  # default 2 minutes

btn_send = tk.Button(root, text="Send Emails", command=send_emails, bg="green", fg="white", height=2)
btn_send.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=600, mode='determinate')
progress_bar.pack(padx=10, pady=10)

tk.Label(root, text="Log:").pack(anchor='w', padx=10)
log_output = scrolledtext.ScrolledText(root, width=75, height=12)
log_output.pack(padx=10, pady=5)

root.mainloop()