from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    #Quien crea el post:
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name= 'Usuario')
    #Que imagen sube:
    image = models.ImageField(upload_to='posts_images/',verbose_name= 'Imagen')
    #Breve descipción del post:
    caption = models.TextField(max_length=500, blank=True,verbose_name= 'Descripción')
    #Fecha de cración:
    created_at = models.DateTimeField(auto_now_add=True, verbose_name= 'Fecha de creación')
    #Numero de likes que tiene:
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True, verbose_name= 'Nº de Likes')

    #Como quiero que me aparezca en el admin:
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    #Qué quiero ver al imprimir un Post
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


#Este es un modelo para controlar los comentarios que otros usuarios hagan a un post:
class Comment(models.Model):
    #Post al que hace refecencia el comentario
    post = models.ForeignKey(Post,verbose_name='Post al que pertenece el comentario', on_delete=models.CASCADE, related_name='comments')
    #Usuario que hace el comentario
    user = models.ForeignKey(User,verbose_name='Autor', on_delete=models.CASCADE, related_name='comments')
    #Texto que contendrá el comentario
    text = models.TextField(verbose_name='Contenido del comentario', max_length=300)
    #Fecha de creacion del comentario
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    #Como quiero que me aparezca en el admin:
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-created_at']


    #Qué quiero ver al imprimir un comentario:
    def __str__(self):
        return f"Comentó {self.user.username} el post {self.post}"