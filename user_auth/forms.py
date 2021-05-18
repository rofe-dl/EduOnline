from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):

    #to define the details of the form(equivalent models, fields)
    class Meta:

        #for which model this form exists
        model=User
        fields=['username','email','password1','password2']

    #to remove the help text
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        self.fields['password2'].label = "Confirm Password"
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None