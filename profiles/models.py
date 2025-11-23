from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    #Imagen de perfil que tendrá el usuario:
    profile_picture = models.ImageField('Imagen de perfil',upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField('Biografía',max_length=500, blank=True)
    birth_date = models.DateField(verbose_name='Fecha de nacimiento', null=True, blank=True)
    #Relación uno a muchos con la gente a la que sigue. Lo de simmetrical significa que puedes seguir a alguien y este no te sigue a ti.
    followers = models.ManyToManyField("self", symmetrical=False, related_name='following',through='Follow')

    #Como quiero que me aparezca en el admin:
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return self.user.username
    
    #función que dado un perfil añadirá ese usuario a la tabla Follow:
    def follow(self, profile):
        Follow.objects.get_or_create(follower=self, following=profile)
    

class Follow(models.Model):
    #Quién es el usuario que sigue:
    follower = models.ForeignKey(UserProfile, verbose_name='¿Quién sigue?', on_delete=models.CASCADE, related_name='follower_set')
    # A quién sigue:
    following = models.ForeignKey(UserProfile, verbose_name='¿A quién sigue?', on_delete=models.CASCADE, related_name='following_set')
    #En qué fecha empezó ese seguimiento
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='¿Desde cuándo lo sigue?')
    
    #Como quiero que me aparezca en el admin:
    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"
    
        #Como quiero que me aparezca en el admin:
    class Meta:
        verbose_name = 'Seguidor'
        verbose_name_plural = 'Seguidores'