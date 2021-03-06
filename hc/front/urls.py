from django.conf.urls import include, url

from hc.front import views
from hc.help_videos import urls as help_videos_urls

post_urls = [
    url(r'^$', views.show_post, name="hc-show-post"),
    url(r'^edit/$', views.edit_post, name="hc-update-post"),
    url(r'^publish/$', views.publish_post, name="hc-publish-post"),
    url(r'^delete/$', views.delete_post, name="hc-delete-post")
]

check_urls = [
    url(r'^name/$', views.update_name, name="hc-update-name"),
    url(r'^timeout/$', views.update_timeout, name="hc-update-timeout"),
    url(r'^nag_time/$', views.set_nag_time, name="hc-set-nag-time"),
    url(r'^remove_nag_time/$', views.remove_nag_time, name="hc-remove-nag"),
    url(r'^pause/$', views.pause, name="hc-pause"),
    url(r'^remove/$', views.remove_check, name="hc-remove-check"),
    url(r'^log/$', views.log, name="hc-log"),
    url(r'^priority/$', views.priority, name="hc-priority")
]

channel_urls = [
    url(r'^$', views.channels, name="hc-channels"),
    url(r'^add/$', views.add_channel, name="hc-add-channel"),
    url(r'^add_email/$', views.add_email, name="hc-add-email"),
    url(r'^add_webhook/$', views.add_webhook, name="hc-add-webhook"),
    url(r'^add_pd/$', views.add_pd, name="hc-add-pd"),
    url(r'^add_slack/$', views.add_slack, name="hc-add-slack"),
    url(r'^add_slack_btn/$', views.add_slack_btn, name="hc-add-slack-btn"),
    url(r'^add_hipchat/$', views.add_hipchat, name="hc-add-hipchat"),
    url(r'^add_pushbullet/$', views.add_pushbullet, name="hc-add-pushbullet"),
    url(r'^add_pushover/$', views.add_pushover, name="hc-add-pushover"),
    url(r'^add_victorops/$', views.add_victorops, name="hc-add-victorops"),
    url(r'^telegram/subscribe/$', views.subscribe_to_telegram_bot, name="hc-subscribe-telegram"),
    url(r'^add_telegram/$', views.add_telegram, name="hc-add-telegram"),
    url(r'^([\w-]+)/checks/$', views.channel_checks, name="hc-channel-checks"),
    url(r'^([\w-]+)/remove/$', views.remove_channel, name="hc-remove-channel"),
    url(r'^([\w-]+)/verify/([\w-]+)/$', views.verify_email,
        name="hc-verify-email"),
]

urlpatterns = [
    url(r'^$', views.index, name="hc-index"),
    url(r'^checks/$', views.my_checks, name="hc-checks"),
    url(r'^failed_checks', views.failed_checks, name="hc-failed-checks"),
    url(r'^checks/add/$', views.add_check, name="hc-add-check"),
    url(r'^checks/([\w-]+)/', include(check_urls)),
    url(r'^integrations/', include(channel_urls)),

    url(r'^posts/$', views.posts, name="hc-all-posts"),
    url(r'^post/add/$', views.add_post, name="hc-add-post"),
    url(r'^latest_post/$', views.latest_post, name="hc-post"),
    url(r'^post/([\w-]+)/', include(post_urls)),

    url(r'^docs/$', views.docs, name="hc-docs"),
    url(r'^docs/api/$', views.docs_api, name="hc-docs-api"),
    url(r'^docs/help/$', views.docs_help, name="hc-docs-help"),
    url(r'^docs/faq/$', views.docs_faq, name="hc-docs-faq"),
    url(r'^docs/faq/save/$', views.save_faq, name="hc-save-faq"),
    url(r'^docs/faq/save/(?P<id>\d+)/$', views.save_faq, name="hc-save-faq-edit"),
    url(r'^docs/faq/(?P<id>\d+)/$', views.faq_edit, name="hc-faq-edit"),
    url(r'^docs/faq/del/(?P<id>\d+)/$', views.delete_faq, name="hc-faq-delete"),
    url(r'^docs/faq/cat/(?P<id>\d+)/$', views.faq_cat_edit, name="hc-cat-edit"),
    url(r'^docs/faq/cat/save/$', views.save_category, name="hc-save-cat"),
    url(r'^docs/faq/cat/save/(?P<id>\d+)/$', views.save_category, name="hc-save-cat-edit"),
    url(r'^docs/faq/cat/del/(?P<id>\d+)/$', views.delete_cat, name="hc-cat-delete"),
    url(r'^about/$', views.about, name="hc-about"),
    url(r'^privacy/$', views.privacy, name="hc-privacy"),
    url(r'^terms/$', views.terms, name="hc-terms"),
    url(r'^help/videos/', include(help_videos_urls))
]
