# Django Chat

## Plan

### I - Fundamentals
- Introduction
- Installation des outils nécessaires
- Activation de l'environnement virtuel
- Installation des dépendances
- Création du projet Django

### II - Authentification
- Création de l'app accounts
- Création d'un modèle utilisateur
- Mise en place des migrations
- Création d'une vue pour l'enregistrement
- Ajout d'une URL pour l'authentification et l'autorisation
- Création du dossier de template pour l'authentification

### III - Chat (et channels)
- Configurer les channels
- Création de l'app "chat"
- Définir les modèles
- Mettre en place des consommateurs et des routeurs pour les WebSockets
- Paramétrage de l'ASGI
- Création des vues pour les salles de chat
- Mise en place de la connexion entre les vues et les URLs
- Création du dossier de template pour l'authentification
- Envoi d'une réponse HTML depuis le backend pour htmx/html
- Fonctionnalité sympatoche

### IV - Chiffrement

---

# I - Fundamentals

### Environnement virtuel

Un virtualenv est un environnement virtuel Python qui permet d'isoler les dépendances et les packages spécifiques à un projet.
Il permet de créer un espace de travail indépendant où vous pouvez installer des bibliothèques et des modules sans interférer avec d'autres projets Python sur votre système.

| commande | fonctionnement |
|----------|-------|
| `pip install virtualenv` | Installe `virtualenv` |
| `virtualenv nom_de_votre_env` | Creer un environnement virtuel |
| `source nom_de_votre_env/bin/activate` | Activer l'environnement virtuel |
| `deactivate` | Désactiver l'environnement virtuel |

Pip env
```
Package           Version
----------------- -------
asgiref           3.6.0
channels          3.0.5
constantly        15.1.0
cryptography      39.0.0
Django            3.2.19
daphne            4.0.0
pip               23.1.2
pytz              2023.3
setuptools        67.7.2
sqlparse          0.4.4
typing_extensions 4.5.0
wheel             0.40.0
```

### Django

Django est un framework open-source écrit en Python qui facilite la création d'applications web robustes et évolutives.

| commande | fonctionnement |
|----------|-------|
| `pip install django` | Installe `django` |

### Django channels

Django Channels est une bibliothèque qui permet de développer des applications Web en temps réel et de gérer des connexions persistantes, telles que des websockets, dans le cadre du framework Django. Django Channels ajoute une couche de communication bidirectionnelle aux fonctionnalités standard de Django

| commande | fonctionnement |
|----------|-------|
| `pip install channels` | Installe channels |

### Creation projet

Projet nommé `backchat`, vous pouvez l'appeler comme vous voulez. 
Créer l'environnement virtuel et installer Django dans cet environnement virtuel.

```python
virtualenv venv

source venv/bin/activate

pip install django
pip install -U channels["daphne"]
pip install channels_redis

django-admin startproject backchat
cd backchat
```

---

# II - Authentification

## Création de l'app `accounts`
Nous pouvons séparer l'authentification de l'utilisateur du reste du projet, en créant une application distincte appelée `accounts`.

```python
python manage.py startapp accounts
```

## Création d'un modèle utilisateurs

Nous commencerons par hériter du modèle `AbstractUser` fourni dans le module `django.contrib.auth.models`.
Le modèle possède des champs de base comme le nom d'utilisateur et le mot de passe qui sont des champs obligatoires, et l'email, le prénom, le nom de famille, etc. qui ne sont pas obligatoires. 
Il est préférable de créer un modèle personnalisé en héritant de `AbstractUser` car si, à long terme, nous avons besoin de créer des champs personnalisés dans le modèle de l'utilisateur, cela devient simple.

`accounts/models.py`
```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
```

Nous devons nous assurer que Django sache que l'utilisateur par défaut est celui que nous avons défini dans l'application `accounts` et non l'utilisateur par défaut. Nous devons donc ajouter un champ appelé `AUTH_USER_MODEL` dans le fichier `settings.py`. 
La valeur de ce champ sera le nom de l'application ou le nom du module et le modèle dans ce module python pour lequel nous avons besoin que notre modèle d'utilisateur personnalisé soit défini comme modèle d'utilisateur par défaut.

`backchat/settings.py`
```python
INSALLED_APPS = [
    ...
    ...
    "accounts",
]

AUTH_USER_MODEL = 'accounts.User'
```

## Mise en place de la migration

Migration des changements pour le projet Django et le modèle d'utilisateur.

```python
python manage.py makemigrations
python manage.py migrate
```

## Créer une `view` pour l'enregistrement

Ajouter des `views` comme register et profile pour l'application `accounts` qui peuvent être utilisées pour l'authentification. Les `views` `Login` et `Logout` sont fournies dans le module `django.contrib.auth.views`, nous n'avons qu'à écrire notre propre `view` d'enregistrement. 

Nous devons d'abord avoir un formulaire, un formulaire d'enregistrement d'utilisateur. 
Le formulaire héritera du formulaire `UserCreationForm` qui fera le gros du travail pour nous lors de l'enregistrement de l'utilisateur.
Nous pouvons simplement surcharger la classe `Meta` avec les champs que nous voulons afficher, donc nous ne gardons que les champs nom d'utilisateur et mot de passe. 
Le formulaire peut être personnalisé en ajoutant l'attribut `widget` et en spécifiant les classes utilisées.

`accounts/forms.py`
```python
from accounts.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):

    class Meta:
        model= User
        fields = ['username', 'password1', 'password2']
```

Nous obtiendrons ainsi le formulaire `UserRegisterForm`, qui pourra être affiché dans la `view` d'enregistrement.

Nous devrons créer la `view` `register` qui rendra le formulaire pour l'enregistrement de l'utilisateur et traitera également la soumission du formulaire.

`accounts/views.py`
```python
from django.contrib import messages
from django.shortcuts import redirect, render
from accounts.forms import UserRegisterForm

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Your account has been created! You are now able to log in"
            )
            return redirect("login")
    else:
        form = UserRegisterForm()
        return render(request, "accounts/register.html", {"form": form})
```

La `view` d'enregistrement ci-dessus comporte deux cas :
- l'utilisateur demande le formulaire d'enregistrement.
- l'utilisateur soumet le formulaire. 

Lorsque l'utilisateur fait une demande `get`, nous chargeons un formulaire vide `UserRegisterForm` et rendons le modèle d'enregistrement avec le formulaire.

Ainsi, le modèle est rendu lorsque l'utilisateur souhaite s'enregistrer et lorsque l'utilisateur soumet le formulaire (envoie une requête `post`), nous récupérons les détails de la requête `post` et en faisons une instance de `UserRegisterForm` et sauvegardons le formulaire s'il est valide. 
Nous redirigeons ensuite l'utilisateur vers la `view` de connexion (nous utiliserons la `view` par défaut dans la section suivante). Nous analysons le message comme l'indication que l'utilisateur a été créé.

## Ajouter une URL pour l'authentification et l'autorisation

Une fois que nous avons configuré la `view` register, nous pouvons également ajouter les `views` `login` et `logout` dans l'application. 
Mais nous n'avons pas besoin de les écrire nous-mêmes.
Nous utiliserons les `views` `LoginView` et `LogoutView` qui sont des `views` basées sur des classes fournies dans le module `django.contrib.auth.views`. Nous fournirons les modèles respectifs pour chacune de ces `views`.

`accounts/urls.py`
```python
from django.urls import path
from django.contrib.auth import views as auth_views
import user.views as user_views

urlpatterns = [
    path("register/", user_views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
]
```

Nous avons nommé les URLs `register` , `login` , et `logout` afin de pouvoir les utiliser lors du rendu des liens dans les templates. 
Nous devons maintenant inclure les URLs de l'application `accounts` dans les URLs du projet. 
Nous pouvons le faire en utilisant la méthode `include` et en spécifiant le nom de l'application avec le module où se trouvent les `urlpatterns`.

`backchat/urls.py`
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
]
```

Ainsi, nous avons routé le chemin `/auth` pour inclure toutes les URLs dans l'application des comptes. Ainsi, la `view` de connexion sera à l'URL `/auth/login/` , et ainsi de suite.

Nous devons également ajouter les URL `LOGIN_REDIRECT_URL` et `LOGIN_URL` pour spécifier le nom de l'url qui sera redirigée une fois que l'utilisateur est connecté et le nom de l'url de connexion par défaut, respectivement.

`backchat/settings.py`
```python
LOGIN_REDIRECT_URL = "index"
LOGIN_URL = "login"
```

## Création du dossier de template pour l'authentification

```python
import os

...
...

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [ os.path.join(BASE_DIR, "templates"), ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

Créez ensuite le dossier `templates` dans le même chemin que votre fichier `manage.py`.

Les templates créer sont des proposition, et pas des modèles a suivrent obligatoirement. 


###  Création de template d'enregistrement

`templates/accounts/register.html`
```html
# templates / accounts / register.html

{% extends 'base.html' %}
{% block base %}
    <div class="content-section">
        <form method="POST">
            {% csrf_token %}
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">Register Now</legend>
                {{ form.as_p }}
            </fieldset>
            <div class="form-group">
                <button class="btn btn-outline-info" type="submit">Sign Up</button>
            </div>
        </form>
        <div class="border-top pt-3">
            <small class="text-muted">
            Already Have An Account? <a class="ml-2" href="{% url 'login' %}">Log In</a>
            </small>
        </div>
    </div>
{% endblock %}
```

### Création de template Login

`templates/accounts/login.html`  
```html
{% extends 'base.html' %}
{% block base %}
    <div class="content-section" id="login">
        <form method="POST" >
            {% csrf_token %}
            <fieldset class="form-group">
                <legend class="border-bottom mb-4">LOG IN</legend>
                {{ form.as_p }}
            </fieldset>
            <div class="form-group">
                <button class="btn btn-outline-info" type="submit">Log In</button>
            </div>
        </form>
        <div class="border-top pt-3">
            <small class="text-muted">
                Register Here <a class="ml-2" href="{% url 'register' %}">Sign Up</a>
            </small>
        </div>
    </div>
{% endblock %}
```

### Création de template Logout

`templates/accounts/logout.html`
```html
{% extends 'base.html' %}
{% block base %}
    <h2>You have been logged out</h2>
    <div class="border-top pt-3">
        <small class="text-muted">
            <a href="{% url 'login' %}">Log In Again</a>
        </small>
    </div>
{% endblock %}
```

---

# III - Chat (et channels)

## Configurer les channels

Configurer la configuration `CHANNEL_LAYER` pour spécifier le backend utilisé qui peut être `Redis` , `In-Memory` , ou d'autres.
Nous devons ajouter `channels` , `daphne` à la configuration `INSALLED_APPS` du projet. Assurez-vous que l'application `daphne` est en haut de la liste des applications.

`backchat/settings.py`
```python
...
...

INSALLED_APPS = [
    "daphne",
    ...
    ...
    "channels",
]

ASGI_APPLICATION = "backchat.asgi.application"

...
...

# For InMemory channels
CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# For Redis
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis-host-url", 6379)],
        },
    },
}
```

## Création de l'app `chat`

Créer une autre application pour gérer les salles et la logique de l'application de chat. 

Cette application aura ses propres modèles, `views` et URL. 

```
python manage.py startapp chat
```

`backchat/settings.py`
```
INSALLED_APPS = [
    ...
    ...,
    "chat",
]
```

## Definir `models`

Nous avons déjà un système d'authentification configuré, ajouter des salles et autoriser les utilisateurs deviendra alors plus facile.

Modèles pour l'application de chat sera `Room`.

`chat/models.py`
```python
from django.db import models
from accounts.models import User

class Room(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            self.room.name + " - " +
            str(self.user.username) + " : " +
            str(self.message)
        )
```

Nous avons donc simplement le nom, qui sera tiré de l'utilisateur, et le mot-clé, qui servira d'URL à la salle. 

Les utilisateurs sont définis comme `ManyToManyField` puisqu'une salle peut avoir plusieurs utilisateurs et qu'un utilisateur peut être dans plusieurs salles. 

Nous créons également le modèle `Message` qui stockera la salle et l'utilisateur en tant que clé étrangère et le texte actuel en tant que message.

Nous avons défini le champ `created_at` qui indiquera l'heure à laquelle l'objet a été créé. 

Enfin, la méthode `dunder string` est utilisée pour représenter l'objet message comme un prix de la concaténation des chaînes de caractères du nom de la salle, du nom d'utilisateur et du message. 

Une fois les modèles conçus, nous pouvons les migrer dans la base de données.

```
python manage.py makemigrations
python manage.py migrate
```

## Mettre en place des consommateurs et des routeurs pour les WebSockets

Nous créons une classe (consommateur) appelée `ChatConsumer` qui hérite de l'`AsyncWebsocketConsumer` fourni par le module `channels.generic.websocket`. Cette classe possède quelques méthodes comme `connect`, `disconnect`, et `receive`. 

Nous définissons ces méthodes car elles seront utilisées pour la communication via le protocole `WebSocket` par l'intermédiaire de l'interface `channels`.

Dans le bloc de code suivant, nous faisons essentiellement ce qui suit :
- Accepter la connexion sur le nom de la salle demandée
- Envoi et réception de messages sur la salle/le groupe
- Fermeture de la connexion WebSocket et suppression du client de la salle/du groupe.

`chat/consumers.py`
```python
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = self.user.username

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "username": username
                }
            )
        )
```

### Accept la connexion websocket

La méthode `connect` est appelée lorsque le client établit une connexion websocket. À ce moment-là, la fonction obtient le nom de la salle à partir de l'URL du client et stocke le nom de la salle, qui est une chaîne de caractères. 

Elle crée une variable distincte appelée `room_group_name` en ajoutant la chaîne `chat_` au `room_name`, elle récupère également l'utilisateur actuellement connecté à partir de la demande. 

Il ajoute ensuite le nom du canal au groupe nommé `nom_du_groupe_de_salle`. Le nom du canal est un identifiant unique de la connexion/du consommateur dans le canal.

En ajoutant le nom du canal, le consommateur peut diffuser le message à tous les canaux du groupe. 

Enfin, la fonction accepte la connexion et une connexion webcoket est établie des deux côtés, la connexion est envoyée par le client et est maintenant acceptée par le backend.

### Deconnecter la connexion websocket

Lorsque le client envoie une demande de fermeture de connexion au serveur, la méthode de `disconnect` est déclenchée et supprime le nom du canal du groupe, c'est-à-dire le nom du groupe `room_group_name`, quelle que soit la chaîne de caractères qu'il contient. 

Ainsi, le client est retiré du groupe de diffusion et ne peut donc plus recevoir ou envoyer de messages par l'intermédiaire de la websocket puisqu'elle a été fermée des deux côtés.

### Recevoir un message de la connexion websocket

La méthode `recieve` est responsable de toute la logique et de l'analyse du message, ainsi que de la diffusion des messages des clients vers les canaux du groupe. 

La fonction prend un paramètre appelé `text_data` et il est envoyé par le client via websocket, il s'agit donc d'un contenu JSON. Nous devons obtenir le message réel de l'objet JSON ou tout autre élément de contenu du client. 

Nous désérialisons donc (en convertissant l'objet JSON en objets python) la charge utile reçue, et nous obtenons la valeur du message clé. 

La clé est le nom d'entrée ou l'identifiant du client qui envoie la requête via le socket web, elle peut donc être différente en fonction du modèle de l'interface (nous verrons l'interface bientôt).

La méthode `receive` est la méthode `channel_layer.group_send`. Cette méthode est utilisée pour envoyer ou diffuser le message reçu à l'ensemble du groupe.
La méthode a deux paramètres :
- le nom du groupe
- le corps JSON contenant le message et d'autres détails.

## Création de `Routers` pour la connexion websocket

Routes URL pour faire correspondre ces consommateurs à un chemin. 
Créer un fichier/module appelé `routing.py` qui ressemblera beaucoup au fichier `urls.py`. Il aura une liste appelée `websocket_urlpatterns` tout comme `urlpatterns` avec la liste des chemins. 

> Ces chemins ne sont cependant pas des routes http mais serviront de chemin WebSocket.

`chat/routing.py`
```python
from django.urls import path

from chat import consumers

websocket_urlpatterns = [
    path('chat/<str:room_slug>/', consumers.ChatConsumer.as_asgi()),
]
```

Le chemin `/chat/<room_slug>` où room_name sera le nom de la salle. 

Le chemin est lié au consommateur défini dans le module `consumers.py` comme `ChatConsumer`. La méthode `as_asgi` est utilisée pour convertir une `view` en une `view` compatible ASGI pour l'interface WebSocket.

## Parametrage de l'ASGI

Nous utilisons la configuration d'application ASGI.
Le chat est asynchrone parce que plusieurs clients peuvent envoyer et recevoir des messages en même temps, nous ne voulons pas faire attendre un client avant que le serveur ne traite un message d'un autre client.

Inclure les configurations de l'application de chat.

`backchat/asgi.py`
```python
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backchat.settings')

from chat import routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket":AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
})
```

Remplacer la configuration de l'application qui est un composant utilisé pour acheminer différents types de protocoles pour l'application ASGI. 

Nous avons défini les deux clés `http` et `websocket` dans notre application. 

Les demandes de type `http` seront servies par l'application `get_asgi_application` qui est utilisée pour exécuter l'application dans un environnement ASGI.

Pour les requêtes de type `websocket`, nous mettons en place l'`AuthMiddlewareStack` qui aide à authentifier les utilisateurs demandant une connexion `WebSocket` et permet uniquement aux utilisateurs autorisés d'établir une connexion avec l'application. 

L'`URLRouter` est utilisé pour mettre en correspondance la liste des modèles d'URL avec la demande entrante. Il sert donc l'URL de la demande au consommateur approprié dans l'application. Nous analysons les motifs `websocket_urlpatterns` comme la liste des URL qui seront utilisées pour les connexions WebSocket.

## Création de `views`pour les chat rooms

`chat/views.py`
```python
import string
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect
from django.utils.text import slugify
from chat.models import Room

@login_required
def index(request, slug):
    room = Room.objects.get(slug=slug)
    return render(request, 'chat/room.html', {'name': room.name, 'slug': room.slug})

@login_required
def room_create(request):
    if request.method == "POST":
        room_name = request.POST["room_name"]
        uid = str(''.join(random.choices(string.ascii_letters + string.digits, k=4)))
        room_slug = slugify(room_name + "_" + uid)
        room = Room.objects.create(name=room_name, slug=room_slug)
        return redirect(reverse('chat', kwargs={'slug': room.slug}))
    else:
        return render(request, 'chat/create.html')

@login_required
def room_join(request):
    if request.method == "POST":
        room_slug = request.POST["room_slug"]
        room = Room.objects.get(slug=room_slug)
        return redirect(reverse('chat', kwargs={'slug': room.slug}))
    else:
        return render(request, 'chat/join.html')
```

Dans le module de `views` ci-dessus, nous avons ajouté trois `views`, à savoir `index` pour la page de la salle, `room_create` pour la page de création de la salle et `room_join` pour la page de jonction de la salle. 

- La `view` `index` est une simple demande d'accès à l'identifiant fourni pour la salle, elle obtient l'identifiant à partir de l'URL de la demande et récupère un objet de la salle associé à cet identifiant. Ensuite, elle rend le modèle de salle avec les variables de contexte telles que le nom de la salle et le mot-clé associé à cette salle.

- La `view` `room_create` est une simple `view` à deux cas qui peut soit rendre la page de création de la salle, soit traiter le formulaire soumis et créer la salle. Tout comme nous l'avons fait pour la `view` register dans l'application accounts. Lorsque l'utilisateur envoie une requête `GET` à l'URL que nous allons mapper à /create/ peu de temps après, l'utilisateur reçoit un formulaire. Nous rendrons donc le modèle `create.html`. Si l'utilisateur a envoyé une requête POST à la `view` via l'URL /create, nous récupérerons le champ name dans la requête envoyée et créerons un identifiant unique avec le nom de la pièce. La concaténation du nom et de l'uid sera définie comme le nom de la salle. Nous créerons alors simplement la salle et redirigerons l'utilisateur vers la page de la salle.

- La `view` `room_join` est également une `view` à deux cas, où l'utilisateur peut soit demander le formulaire join room, soit envoyer un slug avec la soumission du formulaire. Si l'utilisateur demande un formulaire, nous rendrons le modèle join.html. Si l'utilisateur soumet le formulaire, nous allons chercher la salle en fonction de l'étiquette fournie et rediriger l'utilisateur vers la page de la salle.

## Mise en place de connexion entre les `views` et les URLs

`chat/urls.py`
```python
from django.urls import path
from django.views.generic import TemplateView
from chat import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html"), name='index'),
    path("room/<str:slug>/", views.index, name='chat'),
    path("create/", views.room_create, name='room-create'),
    path("join/", views.room_join, name='room-join'),
]
```

La première route ("`/`") est la page d'accueil ("`index`"). Elle utilise la vue TemplateView pour rendre le modèle "base.html".

La deuxième route ("`/room/str:slug/`") est pour la page d'index de la salle. Elle utilise la vue "`index`" qui récupère la salle en fonction du slug fourni.

La troisième route ("`/create/`") est pour la création d'une salle. Elle utilise la vue "`room_create`" pour afficher le formulaire de création et gérer la requête POST pour créer la salle.

La dernière route ("`/join/`") est pour rejoindre une salle. Elle utilise la vue "`room_join`" pour afficher le formulaire de connexion et rediriger vers la page de la salle.

`backchat/urls.py`
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include('accounts.urls')),
    path("", include('chat.urls')),
]
```

Le processus de traitement du message par le backend est achevé, il dépend alors du client pour traiter et restituer le message.

## Création du dossier de template pour l'authentification

On reutilise le meme dossier que pour la partie précédente, c'est plus simple.

### Création template de création de salle de chat (Room)

`templates/chat/create.html`
```html
{% extends 'base.html' %}

{% block base %}
    <form method='post' action='{% url 'room-create' %}'>
        {% csrf_token %}
        <input name='room_name' id='room_name' placeholder='Room Name'>
        <input type='submit' id="submit">
    </form>
{% endblock %}
```

### Création template pour rejoindre une salle de chat (Room)

`templates/chat/join.html`
```html
{% extends 'base.html' %}

{% block base %}
    <form method='post' action='{% url 'room-join' %}'>
        {% csrf_token %}
        <input name='room_slug' id='room_slug' required='true' placeholder='Room Code'>
        <input type='submit' id="submit">
    </form>
{% endblock %}
```

### Création template de salle de chat (Room)

`templates/chat/room.html`
```html
{% extends 'base.html' %}

{% block base %}
    <h2>{{ name }}</h2>
    <div hx-ws="connect:/chat/{{ slug }}/">
        <form hx-ws="send:submit">
            <input name="message">
            <input type="submit">
        </form>
     </div>
     <div id='messages'></div>
{% endblock %}
```

## Envoi d'une réponse HTML depuis le backend pour htmx/html

`chat/consumers.py`
```python
    ...
    ...

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.user
        username = user.username

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        # This is the crucial part of the application
        message_html = f"<div hx-swap-oob='beforeend:#messages'><p><b>{username}</b>: {message}</p></div>"
        await self.send(
            text_data=json.dumps(
                {
                    "message": message_html,
                    "username": username
                }
            )
        )
```

Ce code fait partie d'un consommateur `WebSocket` dans une application de chat en temps réel. 

La méthode `receive` est appelée lorsque le consommateur reçoit des données du client. Elle convertit les données au format JSON et extrait le message et le nom d'utilisateur associés.

Me consommateur envoie le message et le nom d'utilisateur au groupe de canaux correspondant à la salle de discussion. Cela permet d'envoyer le message à tous les clients connectés à cette salle.

La méthode `chat_message` est appelée lorsque le groupe de canaux reçoit un message. Elle extrait le message et le nom d'utilisateur de l'événement et crée une représentation HTML du message avec des balises `<div>` et `<p>`.

Enfin, le consommateur envoie le message HTML et le nom d'utilisateur aux clients connectés en utilisant la méthode `send`, en encodant les données au format JSON.

## Fonctionnalité sympatoche

Nous pouvons enregistrer des messages, ajouter et supprimer des utilisateurs de la salle en fonction de la connexion, et d'autres choses qui peuvent en faire une application à part entière. 

`chat/consumers.py`
```python
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        # Add the user when the client connects
        await self.add_user(self.room_name, self.user)

        await self.accept()

    async def disconnect(self, close_code):

        # Remove the user when the client disconnects
        await self.remove_user(self.room_name, self.user)

        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.user
        username = user.username
        room = self.room_name

        # Save the message on recieving
        await self.save_message(room, user, message)

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]


        message_html = f"<div hx-swap-oob='beforeend:#messages'><p><b>{username}</b>: {message}</p></div>"
        await self.send(
            text_data=json.dumps(
                {
                    "message": message_html,
                    "username": username
                }
            )
        )

    @sync_to_async
    def save_message(self, room, user, message):
        room = Room.objects.get(slug=room)
        Message.objects.create(room=room, user=user, message=message)

    @sync_to_async
    def add_user(self, room, user):
        room = Room.objects.get(slug=room)
        if user not in room.users.all():
            room.users.add(user)
            room.save()

    @sync_to_async
    def remove_user(self, room, user):
        room = Room.objects.get(slug=room)
        if user in room.users.all():
            room.users.remove(user)
            room.save()
```

Donc, nous avons créé quelques méthodes comme `save_message` , `add_user` et `remove_user` qui sont toutes des méthodes synchrones mais nous utilisons un serveur Web asynchrone, nous ajoutons donc le décorateur `sync_to_async` qui encapsule une méthode synchrone dans une méthode asynchrone.

Dans les méthodes, nous effectuons simplement les opérations de base de données telles que la création d'un objet de message et l'ajout ou la suppression de l'utilisateur de la salle.

# IV - Chiffrement

