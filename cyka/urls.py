from django.conf.urls import url
from django.urls import include, path

from . import views

app_name = 'cyka'

urlpatterns = [
	# ex: /cyka/
	url(r'^$', views.project, name="project"),
	# ex: /cyka/project/new
	url(r'^project/new/$', views.project_new, name="project_new"),
	# ex: /cyka/project/list
	url(r'^project/list/$', views.project_list, name="project_list"),
	# ex: /cyka/project/5/delete/
	url(r'^(?P<project_id>[0-9]+)/delete/$', views.project_delete, name="project_delete"),
	# ex: /cyka/project/5/details/
	url(r'^(?P<project_id>[0-9]+)/details/$', views.project_details, name="project_details"),
	# ex: /cyka/project/5/topics/
	url(r'^(?P<project_id>[0-9]+)/topics/$', views.project_topics, name="project_topics"),
	# ex: /cyka/project/5/topics/edit/
	url(r'^(?P<topic_id>[0-9]+)/topic_edit/$', views.topic_edit, name="topic_edit"),
	# ex: /cyka/project/5/team/
	url(r'^(?P<project_id>[0-9]+)/team/$', views.project_team, name="project_team"),
	# ex: /cyka/project/5/member/new/
	url(r'^(?P<project_id>[0-9]+)/member/new/$', views.member_new, name="member_new"),
	# ex: /cyka/project/5/agenda/
	url(r'^(?P<project_id>[0-9]+)/agenda/$', views.agenda, name="project_agenda"),
	# ex: /cyka/project/5/member/delete
	url(r'^(?P<member_id>[0-9]+)/member/delete/$', views.member_delete, name="member_delete"),
	# ex: /cyka/project/5/member/edit
	url(r'^(?P<member_id>[0-9]+)/member/edit/$', views.member_edit, name="member_edit"),
	# ex: /cyka/project/5/member/member_shuffle_topics
	url(r'^(?P<member_id>[0-9]+)/member/member_shuffle_topics/$', views.member_shuffle_topics, name="member_shuffle_topics"),
	# ex: /cyka/project/5/member/edit
	url(r'^(?P<member_id>[0-9]+)/member/edit/up/(?P<priority>[0-9]+)$', views.member_edit_up, name="member_edit_up"),
	url(r'^(?P<member_id>[0-9]+)/member/edit/up/(?P<priority>-[0-9]+)$', views.member_edit_up, name="member_edit_up"),
	# ex: /cyka/personal/uuid
        url(r'^personal/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal, name="personal"),
]

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
