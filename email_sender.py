import smtplib
import os

EMAIL_ADRESS = os.environ.get("cna.khadem.885@gmail.com")
EMAIL_PASS = os.environ.get("kfkj djwe lpoo odwl")

def send_email_to_user(user_mail):
    with smtplib.SMTP('smtp.gmail.com',587)as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_ADRESS, EMAIL_PASS)


        subject = "darim bishtar badkhat mishin XDDDDDDD"

        body = 'akharin meghdar taghrat arz ro ba ma dashte bashid va bishtar geryee konid :O'
        

        msg = f"{subject}\n\n{body}"


        smtp.sendmail(EMAIL_ADRESS, user_mail ,msg)