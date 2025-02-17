from smtplib import SMTP_SSL
from init_user import init_smtp_server

def test_mail(smtp_server: SMTP_SSL, user: str):
    # Test send mail
    sent_from = user
    sent_to = sent_from  #  Send it to self (as test)
    email_text = 'This is a test'
    smtp_server.sendmail(sent_from, sent_to, email_text)

    # Close the connection
    smtp_server.close()

if __name__ == '__main__':
    smtp_server, user = init_smtp_server("0")
    try:
        smtp_server.ehlo()
    except:
        print(smtp_server)
        exit()

    test_mail(smtp_server, user)
    print('Mail sent successfully')