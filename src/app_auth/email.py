from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = 'activate\email.html'
    def get_subject(self):
        return 'Activate your account'