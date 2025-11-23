from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.detail import DetailView
from post.models import Post
from .forms import PostCreateForm, CommentCreateForm
#Para mostrar mensajes de django:
from django.contrib import messages
#Para poder redireccionar importamos reverse_lazy:
from django.urls import reverse_lazy, reverse
#Protegemos las vistas para usuarios que no están logueados:
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.shortcuts import HttpResponseRedirect
#Para poder redireccionar importamos reverse_lazy:
from django.urls import reverse_lazy, reverse

#Importar JsonResponse:
from django.http import JsonResponse


# Create your views here.
# Creamos una vista para ver los datos de post:
#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
class PostCreateView (CreateView):
    #Necesitamos un template html:
    template_name = "posts/post_create.html"
    #Necesitamos un modelo:
    model = Post
    #Necesitamos un formulario:
    form_class = PostCreateForm
    #Necesitamos una URL para redirigir al usuario cuando complete el formulario:
    success_url = reverse_lazy('home')
    
    #Debemos asignar a qué usuario le pertenece la publicación que se crea:
    def form_valid(self, form):
        form.instance.user = self.request.user
        #Añadimos un mensaje de éxito:
        messages.add_message(self.request, messages.SUCCESS, "Publicación creada correctamente.")
        #llamamos al constructor: para ejecutar el comportamiento por defecto
        return super(PostCreateView, self).form_valid(form)


#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
class PostDetailView (DetailView, CreateView):
    template_name = "posts/post_detail.html"
    model = Post
    #Cómo vamos a llamar al modelo dentro del template:
    context_object_name = 'post'
    #Añadimos el formulario para poder añadir comentarios:
    form_class = CommentCreateForm

    #Debemos asignar a qué usuario le pertenece la publicación que se crea:
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post = self.get_object()
        #llamamos al constructor: para ejecutar el comportamiento por defecto
        return super(PostDetailView, self).form_valid(form)
    
    #a qué _url irá despues de completar el formulario:
    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Comentario añadido correctamente.")
        return reverse('post_detail', args=[self.get_object().pk])

@login_required
def like_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user in post.likes.all():
        messages.add_message(request, messages.SUCCESS, "Ya no te gusta esta publicación")
        post.likes.remove(request.user)
    else:
        messages.add_message(request, messages.SUCCESS, "Te gusta esta publicación")
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_detail', args=[pk]))


#Hacemos lo mismo pero vía JavaScript:
@login_required
def like_post_ajax(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        return JsonResponse(
            {
                'message': 'Ya no te gusta esta publicación',
                'liked':False,
                'nlikes': post.likes.all().count()
            }
        )
    else:
        post.likes.add(request.user)
        return JsonResponse(
            {
                'message': 'Te gusta esta publicación',
                'liked':True,
                'nlikes': post.likes.all().count()
            }
        )