from django.shortcuts import render

from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.contrib.auth.models import User

from django.contrib.auth import login, authenticate, logout
from django.shortcuts import HttpResponseRedirect
#Para poder redireccionar importamos reverse_lazy:
from django.urls import reverse_lazy, reverse
#Para mostrar mensajes de django:
from django.contrib import messages
#Importamos formularios:
from .forms import RegistrationForm, LoginForm, FollowForm

from profiles.models import UserProfile
#Protegemos las vistas para usuarios que no están logueados:
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
#Hacemos consultas al modelo Post:
from post.models import Post
#Hacemos consultas al modelo Profiles:
from profiles.models import Follow
# Create your views here. Las vistas van a acceder a los archivos HTML correspondientes a cada vista.

class HomeView(TemplateView):
    #Cargamos un template html:
    template_name = "general/home.html"

    #Mostramos las 5 últimas publicaciones:
    def get_context_data(self, **kwargs):
        #definimos el contexto:
        context = super().get_context_data(**kwargs)

        #Si el usuario está logueado
        if self.request.user.is_authenticated:
            # Obtenemos los posts de los usuarios que seguimos
            seguidos = Follow.objects.filter(follower=self.request.user.profile).values_list('following__user', flat=True)
            # Nos traemos los posts de los usuarios que seguimos
            last_posts = Post.objects.filter(user__profile__user__in=seguidos)
        else:
            last_posts = Post.objects.all().order_by('-created_at')[:10]
        context['last_posts'] = last_posts

        return context


class LoginView(FormView):
    #Cargamos un template html:
    template_name = "general/login.html"
    #Decimos qué formulario queremos que obedezca:
    form_class = LoginForm
    #Validamos el usuario:
    def form_valid(self, form):
        usuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        #Dado un usuario y una contraseña, devolverá un true o un false:
        user = authenticate(username = usuario, password = password)

        #Si el usuario tiene un valor, logueamos al usuario:
        if user is not None:
            login(self.request, user)
            #Mostramos mensaje:
            messages.add_message(self.request, messages.SUCCESS, f'Bienvenido de nuevo {user.username}')
            #Redirigimos al usuario a la Home:
            return HttpResponseRedirect(reverse ('home'))

        #Si el usuario no es válido lo redirigimos al formulario para que lo vuelva a intentar:
        else:
            messages.add_message (
                self.request, messages.ERROR, ('Usuario no válido o contraseña incorrecta')
            )
            return super(LoginView, self).form_invalid(form)


class RegisterView(CreateView):
    template_name = "general/register.html"
    model = User
    #Cuando el formulario esté completado nos redirigirá a la home:
    success_url = reverse_lazy('login')
    #Decimos qué formulario queremos que obedezca:
    form_class = RegistrationForm

    #Función que activará mensajes de texto, si el formulario es correcto:
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Usuario creado correctamente.")
        return super(RegisterView, self).form_valid(form)



class LegalView(TemplateView):
    template_name = "general/legal.html"


class ContactView(TemplateView):
    template_name = "general/contact.html"

#El DetailView con un modelo y una plantilla html me va a renderizar la vista
#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
class ProfileDetailView(DetailView, FormView):
    model = UserProfile
    template_name = "general/profile_detail.html"
    context_object_name = "profile"
    form_class = FollowForm

    def get_initial(self):
        self.initial['profile_pk'] =  self.get_object().pk
        return super().get_initial()

    #Validamos el usuario:
    def form_valid(self, form):
        profile_pk = form.cleaned_data.get('profile_pk')
        action = form.cleaned_data.get('action')
        following = UserProfile.objects.get(pk=profile_pk)

        if Follow.objects.filter(
              follower=self.request.user.profile,
              following=following
        ).count():
            Follow.objects.filter(
                  follower=self.request.user.profile,
                  following=following
              ).delete()
            messages.add_message(self.request, messages.SUCCESS, f"Se ha dejado de seguir a {following.user.username}")
        else:
            Follow.objects.get_or_create(
              follower=self.request.user.profile,
              following=following
            )
            messages.add_message(self.request, messages.SUCCESS, f"Se empieza a seguir a {following.user.username}")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('profile_detail', args=[self.get_object().pk])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #comprobamos si seguimos al usuario:
        following = Follow.objects.filter(follower=self.request.user.profile, following=self.get_object()).exists()
        #Lo añadimos al contexto:
        context['following'] = following
        return context


#El DetailView con un modelo y una plantilla html me va a renderizar la vista
#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
class ProfileListView(ListView):
    model = UserProfile
    template_name = "general/profile_list.html"
    context_object_name = "profiles"

    #Nos excluimos a nosotros mismos del listado de perfiles:
    def get_queryset(self):
        return UserProfile.objects.all().exclude(user=self.request.user)


#El UpdateView con un modelo y una plantilla html me va a renderizar la vista
#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = UserProfile
    template_name = "general/profile_update.html"
    context_object_name = "profile"
    #Creamos el formulario que queremos utilizar:
    fields = ['profile_picture','bio','birth_date']

    #Sobreescribimos la función dispatch para que no puedan editar nuestro perfil otro usuario que se sepa la url:
    def dispatch(self, request, *args, **kwargs):
        #Verificamos el usuario actual:
        user_profile = self.get_object()
        if user_profile.user != self.request.user:
            return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)
    
    #Cuando el formulario se actualize, qué queremos que haga:
    #Función que activará mensajes de texto, si el formulario es correcto:
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Perfil editado correctamente.")
        return super(ProfileUpdateView, self).form_valid(form)
    
    #a qué _url irá despues de completar el formulario:
    def get_success_url(self):
        return reverse('profile_detail', args=[self.object.pk])


#Protegemos la vista, como es una CreateView debemos usar el 'dispatch'
@method_decorator(login_required, name='dispatch')
def logout_view(request):
    logout(request)
    messages.add_message(request, messages.INFO, "Sesión cerrada correctamente.")
    return HttpResponseRedirect(reverse('home'))


