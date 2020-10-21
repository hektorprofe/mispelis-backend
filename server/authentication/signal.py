# RETO: ENVIAR EMAILS Y CONFIGURAR EL CLIENTE DE CORREO EN DJANGO

# Vista de la señal enviando correos usando los templates adjuntos
# https://github.com/anexia-it/django-rest-passwordreset#example-for-sending-an-e-mail
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    # create de template context
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': f"https://dominio.com/new-password/?token={reset_password_token.key}"
    }

    # render email text
    email_html_message = render_to_string(
        'email/user_reset_password.html', context)
    email_plaintext_message = render_to_string(
        'email/user_reset_password.txt', context)

    print(email_plaintext_message)

    # send email using django email configured client
    # https://docs.djangoproject.com/en/3.1/topics/email/#module-django.core.mail
    # Tutorial: https://codigofacilito.com/articulos/envio-correos-django
    msg = EmailMultiAlternatives(
        "Recuperación de contraseña para {title}".format(title="TusPelis DB"),
        email_plaintext_message,
        "noreply@https://dominio.com",
        [reset_password_token.user.email]
    )

    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
