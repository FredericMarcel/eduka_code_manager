import logging 
# perform other imports 
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from  jinja2 import Environment, FileSystemLoader

def add_attachments(message : MIMEMultipart, attachments : list()):
    """
    Args:
        message (MIMEMultipart): message object 
        attachments (list): list of relative file paths to all required attachments
    """
    for file in attachments:
        with open(file, "rb") as attachment:
            temp = MIMEBase("application", "octet-stream")
            temp.set_payload(attachment.read())
            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(temp)

            # Add header as key/value pair to attachment part
            temp.add_header(
                "Content-Disposition",
                f"attachment; filename= {file}",
            )
            message.attach(temp)
    return None 

def send_daily_report(sender_credentials : dict(), recipient_list : dict(), daily_report : dict(), errors : list(), attachments : list(), datetime_str : str()):
    """
        Args:
            sender_credentials (dict): dictionary containing enko email and password of sender
            recipient_list (dict): list of recipient e-mail addresses. These must be enko e-mail addresses.
            daily_report (dict): dictionary containing all information necessary for reporting 
    """
    try:

        #initialise message object 
        message = MIMEMultipart("mixed")
        message["Subject"] = f"[{datetime_str}] Enko Hub code updates"
        #message["Subject"] = "[RECAP 2023/01/10] Enko Hub code updates"
        message["From"] = sender_credentials["email"]
        
        #add rendered html to email message
        #exploit the html template with the Jinja2 library 
        environment = Environment(loader=FileSystemLoader("./reports/templates/"))
        html_template = environment.get_template("daily_report.html")
        html_render = html_template.render(daily_report = daily_report, errors = errors) 
        html_message = MIMEText(html_render, "html")
        message.attach(html_message)
        
        #add required attachments 
        add_attachments(message = message, attachments = attachments)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_credentials["email"], sender_credentials["password"])
            server.sendmail(
                sender_credentials["email"], recipient_list, message.as_string()
            )
        
    except Exception as e:
        logging.exception("An error occured. Daily report was not sent.")
           
    return None

def send_weekly_report(sender_credentials : dict(), recipient_list : list(), weekly_report : dict(), attachments : list()): 
    """
        Args:
            sender_credentials (dict): dictionary containing enko email and password of sender
            recipient_list (dict): list of recipient e-mail addresses. These must be enko e-mail addresses.
            weekly_report (dict): dictionary containing all information necessary for reporting 
    """     
    
    try:
        
        if not weekly_report["must_be_sent"]:
            logging.INFO("Weekly report not sent. Weekly reporting is not active.") 
            return None 

        #initialise message object 
        message = MIMEMultipart("mixed")
        message["Subject"] = ""
        message["From"] = sender_credentials["email"]
        
        #add rendered html to email message
        #exploit the html template with the Jinja2 library 
        environment = Environment(loader=FileSystemLoader("./reports/templates/"))
        html_template = environment.get_template("weekly_report.html")
        html_render = html_template.render(report = weekly_report) 
        html_message = MIMEText(html_render, "html")
        message.attach(html_message)
        
        #add required attachments 
        add_attachments(message = message, attachments = attachments)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_credentials["email"], sender_credentials["password"])
            server.sendmail(
                sender_credentials["email"], recipient_list, message.as_string()
            )
        
    except Exception as e:
        logging.exception("An error occured. Weekly report was not sent.")
            
    return None
