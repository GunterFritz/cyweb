from django.conf.urls import url
from django.urls import include, path

from . import views

app_name = 'cyka'

urlpatterns = [
	# ex: /cyka/
	url(r'^$', views.project, name="project"),
	# ex: /cyka/project/new
	url(r'^project/new/$', views.project_new, name="project_new"),
	# ex: /cyka/project/5/test/
	url(r'^(?P<uuid>[0-9A-Za-z\-]+)/test/$', views.test, name="test"),
	# ex: /cyka/project/list
	url(r'^project/list/$', views.project_list, name="project_list"),
	# ex: /cyka/project/5/moderator/problemjostle/
	url(r'^(?P<project_id>[0-9]+)/moderator/problemjostle/$', views.moderator_problemjostle, name="moderator_problemjostle"),
	#dev only
        url(r'^(?P<project_id>[0-9]+)/moderator/delete/asi/$', views.moderator_delete_asi, name="moderator_delete_asi"),
        #navbar
	# ex: /cyka/project/5/jostle/
	url(r'^(?P<project_id>[0-9]+)/startjostle/$', views.admin_startjostle, name="admin_startjostle"),
        #end navbar
        #start
	# ex: /cyka/project/5/jostle/welcome/
	url(r'^(?P<project_id>[0-9]+)/jostle/welcome/$', views.jostle_welcome, name="moderator_startjostle"),
        #endstart
	# ex: /cyka/member_start/uuid
        url(r'^member_start/(?P<uuid>[0-9A-Za-z\-]+)$', views.member_start, name="member_start"),
        #schedule problem jostle
        url(r'^member/schedule/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_schedule_jostle, name="personal_schedule_jostle"),
        url(r'^moderator/schedule/$', views.moderator_schedule_jostle, name="moderator_schedule"),
        #topicauction
	# ex: /cyka/project/5/moderator/topicauction/
	url(r'^(?P<project_id>[0-9]+)/moderator/topicauction/$', views.moderator_topicauction, name="moderator_topicauction"),
	# ex: /member/topicauction/<uuid>
        # url(r'^member/topicauction/(?P<uuid>[0-9A-Za-z\-]+)$', views.topicauction_asi_overview, name="topicauction_asi_overview"),
	# ex: /member/topicauction/<uuid>
        url(r'^member/topicauction/asi/(?P<uuid>[0-9A-Za-z\-]+)$', views.topicauction_join_asi, name="topicauction_join_asi"),
        #end topicauction
        #priorization
	url(r'^(?P<project_id>[0-9]+)/moderator/priorization/$', views.moderator_priorization, name="moderator_priorization"),
	# ex: /member/priorization/<uuid>
        url(r'^member/priorization/(?P<uuid>[0-9A-Za-z\-]+)$', views.member_priorization, name="member_priorization"),
        #end priorization
        #iterations
	url(r'^(?P<project_id>[0-9]+)/moderator/round/$', views.moderator_round, name="moderator_round"),
        url(r'^member/round/(?P<uuid>[0-9A-Za-z\-]+)$', views.member_round, name="member_round"),
        #end iterations
        #common views
	url(r'^(?P<project_id>[0-9]+)/getmemberdetails/$', views.get_member_details, name="get_member_details"),
        #end get data
        #get data
	url(r'^(?P<project_id>[0-9]+)/getmembers/$', views.get_json_members, name="get_json_members"),
        url(r'^data/step/$', views.get_json_step, name="get_json_step"),
        url(r'^data/asi/$', views.get_json_asi, name="get_json_asi"),
        url(r'^data/proj/$', views.get_json_proj, name="get_json_proj"),
        #end get data
	# ex: /cyka/project/5/jostle/
	url(r'^(?P<project_id>[0-9]+)/jostle/$', views.admin_jostle, name="admin_jostle"),
	# ex: /cyka/project/5/jostle/randsession/
	url(r'^(?P<project_id>[0-9]+)/jostle/randsession/$', views.rand_session, name="randsession"),
	# ex: /cyka/project/5/delete/
	url(r'^(?P<project_id>[0-9]+)/delete/$', views.project_delete, name="project_delete"),
	# ex: /cyka/project/5/votes/
	url(r'^(?P<project_id>[0-9]+)/brainwriting/$', views.moderator_brainwriting, name="moderator_brainwriting"),
	# ex: /cyka/project/5/votes/
	url(r'^(?P<project_id>[0-9]+)/votes/$', views.admin_votes, name="admin_votes"),
	# ex: /cyka/project/5/details/
	url(r'^(?P<project_id>[0-9]+)/details/$', views.project_details, name="project_details"),
	# ex: /cyka/project/5/plenum/
	url(r'^(?P<project_id>[0-9]+)/plenum/$', views.plenum, name="plenum"),
	# ex: /cyka/project/5/workflow/
	url(r'^(?P<project_id>[0-9]+)/workflow/$', views.workflow, name="workflow"),
	# ex: /cyka/project/5/topics/
	url(r'^(?P<project_id>[0-9]+)/topics/$', views.project_topics, name="project_topics"),
	# ex: /cyka/5/topic_toggle/edit/
	url(r'^(?P<topic_id>[0-9]+)/topic_toggle/$', views.topic_toggle, name="topic_toggle"),
	# ex: /cyka/5/topic_edit/edit/
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
	# ex: /cyka/votes/uuid
        url(r'^votes/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_votes, name="personal_votes"),
	# ex: /cyka/project/5/jointable
        url(r'^jointable/(?P<uuid>[0-9A-Za-z\-]+)$', views.join_table, name="personal_join_table"),
	# ex: /cyka/project/5/table
        url(r'^table/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_table, name="personal_table"),
	# ex: /cyka/cards/uuid
        url(r'^cards/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_card, name="personal_card"),
	# ex: /cyka/personal_plenum/uuid
        url(r'^get_more_agenda/(?P<uuid>[0-9A-Za-z\-]+)$', views.get_more_agenda, name="get_more_agenda"),
	# ex: /cyka/personal_agenda/uuid
        url(r'^personal_workflow/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_workflow, name="personal_workflow"),
	# ex: /cyka/join_meeting/uuid
        url(r'^join_meeting/(?P<uuid>[0-9A-Za-z\-]+)$', views.join_room_member, name="join_room_member"),
	# ex: /cyka/join_room/uuid
        url(r'^join_room/(?P<uuid>[0-9A-Za-z\-]+)$', views.join_room, name="join_room"),
	# ex: /cyka/personal_edit/uuid
        url(r'^personal_edit/(?P<uuid>[0-9A-Za-z\-]+)$', views.personal_edit, name="personal_edit"),
	# ex: /cyka/personal_edit_up/5/member/edit
	url(r'^(?P<uuid>[0-9A-Za-z\-]+)/personal/edit/up/(?P<priority>[0-9]+)$', views.personal_edit_up, name="personal_edit_up"),
        #debugging
        url(r'^debug/proj/save_all_priorities/$', views.save_all_priorities, name="save_all_priorities"),
]

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
