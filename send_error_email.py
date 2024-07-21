from SMTPEmail import SMTP
import sys

email_sender = 'shon.dev29@gmail.com'
email_password = 'slrmbmtlnuzlihul'
email_receiver = 'hshanazar29@mail.ru'

client = SMTP(
    SMTP_server='smtp.gmail.com',
    SMTP_account=email_sender,
    SMTP_password=email_password
)


def send_email(error, ip_address):
    subject = f'Сервер "{ip_address}"'

    client.create_mime(
        recipient_email_addr=email_receiver,
        sender_email_addr=email_sender,
        subject=subject,
        sender_display_name='HeadBot',
        recipient_display_name='Hudayberdiyew Sanazar',
        content_html=error,
    )
    client.send_msg()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    error_message = sys.argv[1]
    ip_address = sys.argv[2]
    send_email(error_message, ip_address)
