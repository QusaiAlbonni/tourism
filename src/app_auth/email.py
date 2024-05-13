from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = 'activate\\email.html'
    def get_subject(self):
        return 'Activate your account'
    
class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'reset_password_email.html'
    def get_subject(self):
        return 'Reset your password'