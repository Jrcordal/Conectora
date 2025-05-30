from django.apps import AppConfig


class FreelancersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.freelancers'


        
        # The ready() method is called by Django when the application is loading
        # It's the perfect place to import and connect signals because:
        # 1. It ensures signals are only connected once when the app is ready
        # 2. It avoids circular imports since models are loaded before this runs
        
        # When we import users.signals here, Django executes the code in signals.py
        # where the @receiver decorators automatically register the signal handlers
        # This creates the connection between User model signals (post_save) 
        # and our profile creation/update functions

