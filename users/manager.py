from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, name, email, password=None):

        if not email:
            raise ValueError('Users must have email')

        user = self.model(
            email = self.normalize_email(email),
            name = name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, name,email, password):
        user = self.create_user(
            name = name,
            email = self.normalize_email(email),
            password = password,
            
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser =True
        user.save(using=self._db)
        return user


    