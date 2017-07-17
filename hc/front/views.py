import os
from collections import Counter
from datetime import timedelta as td
from itertools import tee
import json

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.core import signing
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.six.moves.urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden)

from hc.api.decorators import uuid_or_400
from hc.api.models import DEFAULT_GRACE, DEFAULT_TIMEOUT, PRIORITY_LEVELS, Channel, Check, Ping, Priority
from hc.front.models import Post
from hc.api.transports import Telegram
from hc.front.forms import (AddChannelForm, AddWebhookForm, NameTagsForm,
                            TimeoutForm, AddFaqForm, AddFaqCategoryForm, PostForm)
from hc.front.models import (FaqCategory, FaqItem)


# from itertools recipes:
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@login_required
def my_checks(request):
    q = Check.objects.filter(user=request.team.user).order_by("created")
    checks = list(q)
    checks = [check for check in checks if check.has_access(request.user)]

    counter = Counter()
    down_tags, grace_tags = set(), set()
    for check in checks:
        status = check.get_status()
        for tag in check.tags_list():
            if tag == "":
                continue

            counter[tag] += 1

            if status == "down":
                down_tags.add(tag)
            elif check.in_grace_period():
                grace_tags.add(tag)

    ctx = {
        "page": "checks",
        "checks": checks,
        "now": timezone.now(),
        "tags": counter.most_common(),
        "down_tags": down_tags,
        "grace_tags": grace_tags,
        "ping_endpoint": settings.PING_ENDPOINT,
        "current_user": request.user
    }

    return render(request, "front/my_checks.html", ctx)


@login_required
def failed_checks(request):
    query = Check.objects.filter(user=request.team.user).order_by("created")
    checks = list(filter(lambda check: check.get_status() == 'down', list(query)))
    ctx = {
        "page": "failed_checks",
        "checks": checks
    }
    return render(request, "front/my_checks.html", ctx)


def _welcome_check(request):
    check = None
    if "welcome_code" in request.session:
        code = request.session["welcome_code"]
        check = Check.objects.filter(code=code).first()

    if check is None:
        check = Check()
        check.save()
        request.session["welcome_code"] = str(check.code)

    return check


def index(request):
    if request.user.is_authenticated:
        return redirect("hc-checks")

    check = _welcome_check(request)

    ctx = {
        "page": "welcome",
        "check": check,
        "ping_url": check.url(),
        "enable_pushover": settings.PUSHOVER_API_TOKEN is not None
    }

    return render(request, "front/welcome.html", ctx)


def docs(request):
    check = _welcome_check(request)

    ctx = {
        "page": "docs",
        "section": "home",
        "ping_endpoint": settings.PING_ENDPOINT,
        "check": check,
        "ping_url": check.url()
    }

    return render(request, "front/docs.html", ctx)


def docs_api(request):
    ctx = {
        "page": "docs",
        "section": "api",
        "SITE_ROOT": settings.SITE_ROOT,
        "PING_ENDPOINT": settings.PING_ENDPOINT,
        "default_timeout": int(DEFAULT_TIMEOUT.total_seconds()),
        "default_grace": int(DEFAULT_GRACE.total_seconds())
    }

    return render(request, "front/docs_api.html", ctx)


def about(request):
    return render(request, "front/about.html", {"page": "about"})


@login_required
def add_check(request):
    assert request.method == "POST"

    check = Check(user=request.team.user)
    check.save()

    check.assign_all_channels()
    check.assign_access(request.user)

    return redirect("hc-checks")


@login_required
@uuid_or_400
def update_name(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user_id != request.team.user.id:
        return HttpResponseForbidden()

    form = NameTagsForm(request.POST)
    if form.is_valid():
        check.name = form.cleaned_data["name"]
        check.tags = form.cleaned_data["tags"]
        check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def update_timeout(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    form = TimeoutForm(request.POST)
    if form.is_valid():
        check.timeout = td(seconds=form.cleaned_data["timeout"])
        check.grace = td(seconds=form.cleaned_data["grace"])
        check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def pause(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user_id != request.team.user.id:
        return HttpResponseForbidden()

    check.status = "paused"
    check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def remove_check(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    check.delete()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def log(request, code):
    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    limit = request.team.ping_log_limit
    pings = Ping.objects.filter(owner=check).order_by("-id")[:limit]

    pings = list(pings.iterator())
    # oldest-to-newest order will be more convenient for adding
    # "not received" placeholders:
    pings.reverse()

    # Add a dummy ping object at the end. We iterate over *pairs* of pings
    # and don't want to handle a special case of a check with a single ping.
    pings.append(Ping(created=timezone.now()))

    # Now go through pings, calculate time gaps, and decorate
    # the pings list for convenient use in template
    wrapped = []

    early = False
    for older, newer in pairwise(pings):
        wrapped.append({"ping": older, "early": early})

        # Fill in "missed ping" placeholders:
        expected_date = older.created + check.timeout
        n_blanks = 0
        while expected_date + check.grace < newer.created and n_blanks < 10:
            wrapped.append({"placeholder_date": expected_date})
            expected_date = expected_date + check.timeout
            n_blanks += 1

        # Prepare early flag for next ping to come
        early = older.created + check.timeout > newer.created + check.grace

    reached_limit = len(pings) > limit

    wrapped.reverse()
    ctx = {
        "check": check,
        "pings": wrapped,
        "num_pings": len(pings),
        "limit": limit,
        "show_limit_notice": reached_limit and settings.USE_PAYMENTS
    }

    return render(request, "front/log.html", ctx)


@login_required
@uuid_or_400
def priority(request, code):
    if request.method == "GET":
        try:
            check = Check.objects.get(code=code)
            members = set()
            members.add(check.user)
            for member in check.user.profile.member_set.all():
                if check.has_access(member.user):
                    members.add(member.user)

            data = {
                "check": check,
                "team_name": check.user.profile.team_name,
                "members": members,
                "priorities": PRIORITY_LEVELS,
                "levels": Priority.get_user_levels(check)
            }
            return render(request, "front/priority.html", data)
        except Check.DoesNotExist:
            return HttpResponseBadRequest()

    if request.method == "POST":
        check = Check.objects.filter(code=code).first()
        for key, value in request.POST.items():
            if key != "csrfmiddlewaretoken":
                user_id = int(key)
                level = int(value)
                user = User.objects.get(pk=user_id)

                priority = Priority.objects.filter(user=user, current_check=check).first()
                if priority:
                    priority.level = level
                else:
                    priority = Priority(level=level, current_check=check, user=user)
                priority.save()
        return redirect("hc-checks")


@login_required
def channels(request):
    if request.method == "POST":
        code = request.POST["channel"]
        try:
            channel = Channel.objects.get(code=code)
        except Channel.DoesNotExist:
            return HttpResponseBadRequest()
        if channel.user_id != request.team.user.id:
            return HttpResponseForbidden()

        new_checks = []
        for key in request.POST:
            if key.startswith("check-"):
                code = key[6:]
                try:
                    check = Check.objects.get(code=code)
                except Check.DoesNotExist:
                    return HttpResponseBadRequest()
                if check.user_id != request.team.user.id:
                    return HttpResponseForbidden()
                new_checks.append(check)

        channel.checks = new_checks
        return redirect("hc-channels")

    channels = Channel.objects.filter(user=request.team.user).order_by("created")
    channels = channels.annotate(n_checks=Count("checks"))

    num_checks = Check.objects.filter(user=request.team.user).count()

    ctx = {
        "page": "channels",
        "channels": channels,
        "num_checks": num_checks,
        "enable_pushbullet": settings.PUSHBULLET_CLIENT_ID is not None,
        "enable_pushover": settings.PUSHOVER_API_TOKEN is not None
    }
    return render(request, "front/channels.html", ctx)


def do_add_channel(request, data):
    form = AddChannelForm(data)
    if form.is_valid():
        channel = form.save(commit=False)
        channel.user = request.team.user
        channel.save()

        channel.assign_all_checks()

        if channel.kind == "email":
            channel.send_verify_link()

        return redirect("hc-channels")
    else:
        return HttpResponseBadRequest()


@login_required
def add_channel(request):
    assert request.method == "POST"
    return do_add_channel(request, request.POST)


@login_required
@uuid_or_400
def channel_checks(request, code):
    channel = get_object_or_404(Channel, code=code)
    if channel.user_id != request.team.user.id:
        return HttpResponseForbidden()

    assigned = set(channel.checks.values_list('code', flat=True).distinct())
    checks = Check.objects.filter(user=request.team.user).order_by("created")

    ctx = {
        "checks": checks,
        "assigned": assigned,
        "channel": channel
    }

    return render(request, "front/channel_checks.html", ctx)


@uuid_or_400
def verify_email(request, code, token):
    channel = get_object_or_404(Channel, code=code)
    if channel.make_token() == token:
        channel.email_verified = True
        channel.save()
        return render(request, "front/verify_email_success.html")

    return render(request, "bad_link.html")


@login_required
@uuid_or_400
def remove_channel(request, code):
    assert request.method == "POST"

    # user may refresh the page during POST and cause two deletion attempts
    channel = Channel.objects.filter(code=code).first()
    if channel:
        if channel.user != request.team.user:
            return HttpResponseForbidden()
        channel.delete()

    return redirect("hc-channels")


@login_required
def add_email(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_email.html", ctx)


@login_required
def add_webhook(request):
    if request.method == "POST":
        form = AddWebhookForm(request.POST)
        if form.is_valid():
            channel = Channel(user=request.team.user, kind="webhook")
            channel.value = form.get_value()
            channel.save()

            channel.assign_all_checks()
            return redirect("hc-channels")
    else:
        form = AddWebhookForm()

    ctx = {"page": "channels", "form": form}
    return render(request, "integrations/add_webhook.html", ctx)


@login_required
def add_pd(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_pd.html", ctx)


def add_slack(request):
    if not settings.SLACK_CLIENT_ID and not request.user.is_authenticated:
        return redirect("hc-login")

    ctx = {
        "page": "channels",
        "slack_client_id": settings.SLACK_CLIENT_ID
    }
    return render(request, "integrations/add_slack.html", ctx)


@login_required
def add_slack_btn(request):
    code = request.GET.get("code", "")
    if len(code) < 8:
        return HttpResponseBadRequest()

    result = requests.post("https://slack.com/api/oauth.access", {
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
        "code": code
    })

    doc = result.json()
    if doc.get("ok"):
        channel = Channel()
        channel.user = request.team.user
        channel.kind = "slack"
        channel.value = result.text
        channel.save()
        channel.assign_all_checks()
        messages.success(request, "The Slack integration has been added!")
    else:
        s = doc.get("error")
        messages.warning(request, "Error message from slack: %s" % s)

    return redirect("hc-channels")


@login_required
def add_hipchat(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_hipchat.html", ctx)


@login_required
def add_pushbullet(request):
    if settings.PUSHBULLET_CLIENT_ID is None:
        raise Http404("pushbullet integration is not available")

    if "code" in request.GET:
        code = request.GET.get("code", "")
        if len(code) < 8:
            return HttpResponseBadRequest()

        result = requests.post("https://api.pushbullet.com/oauth2/token", {
            "client_id": settings.PUSHBULLET_CLIENT_ID,
            "client_secret": settings.PUSHBULLET_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        })

        doc = result.json()
        if "access_token" in doc:
            channel = Channel(kind="pushbullet")
            channel.user = request.team.user
            channel.value = doc["access_token"]
            channel.save()
            channel.assign_all_checks()
            messages.success(request,
                             "The Pushbullet integration has been added!")
        else:
            messages.warning(request, "Something went wrong")

        return redirect("hc-channels")

    redirect_uri = settings.SITE_ROOT + reverse("hc-add-pushbullet")
    authorize_url = "https://www.pushbullet.com/authorize?" + urlencode({
        "client_id": settings.PUSHBULLET_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code"
    })

    ctx = {
        "page": "channels",
        "authorize_url": authorize_url
    }
    return render(request, "integrations/add_pushbullet.html", ctx)


@login_required
def add_pushover(request):
    if settings.PUSHOVER_API_TOKEN is None or settings.PUSHOVER_SUBSCRIPTION_URL is None:
        raise Http404("pushover integration is not available")

    if request.method == "POST":
        # Initiate the subscription
        nonce = get_random_string()
        request.session["po_nonce"] = nonce

        failure_url = settings.SITE_ROOT + reverse("hc-channels")
        success_url = settings.SITE_ROOT + reverse("hc-add-pushover") + "?" + urlencode({
            "nonce": nonce,
            "prio": request.POST.get("po_priority", "0"),
        })
        subscription_url = settings.PUSHOVER_SUBSCRIPTION_URL + "?" + urlencode({
            "success": success_url,
            "failure": failure_url,
        })

        return redirect(subscription_url)

    # Handle successful subscriptions
    if "pushover_user_key" in request.GET:
        if "nonce" not in request.GET or "prio" not in request.GET:
            return HttpResponseBadRequest()

        # Validate nonce
        if request.GET["nonce"] != request.session.get("po_nonce"):
            return HttpResponseForbidden()

        # Validate priority
        if request.GET["prio"] not in ("-2", "-1", "0", "1", "2"):
            return HttpResponseBadRequest()

        # All looks well--
        del request.session["po_nonce"]

        if request.GET.get("pushover_unsubscribed") == "1":
            # Unsubscription: delete all Pushover channels for this user
            Channel.objects.filter(user=request.user, kind="po").delete()
            return redirect("hc-channels")
        else:
            # Subscription
            user_key = request.GET["pushover_user_key"]
            priority = int(request.GET["prio"])

            return do_add_channel(request, {
                "kind": "po",
                "value": "%s|%d" % (user_key, priority),
            })

    # Show Integration Settings form
    ctx = {
        "page": "channels",
        "po_retry_delay": td(seconds=settings.PUSHOVER_EMERGENCY_RETRY_DELAY),
        "po_expiration": td(seconds=settings.PUSHOVER_EMERGENCY_EXPIRATION),
    }
    return render(request, "integrations/add_pushover.html", ctx)


@login_required
def add_victorops(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_victorops.html", ctx)


def privacy(request):
    return render(request, "front/privacy.html", {})


def terms(request):
    return render(request, "front/terms.html", {})


def posts(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        all_posts = Post.objects.all().order_by("-created")
    elif request.user.is_authenticated():
        all_posts = Post.objects.filter(Q(publish=True) | Q(user=request.user)).order_by("-created")
    else:
        all_posts = Post.objects.filter(publish=True).order_by("-created")

    paginator = Paginator(all_posts, os.environ.get("PER_PAGE", 6))
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    ctx = {
        "page": "view-all-posts",
        "section": "view-all-posts",
        "posts": all_posts[:5],
        "all_posts": posts
    }
    return render(request, "front/posts/index.html", ctx)


def latest_post(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        posts = Post.objects.all().order_by("-created")[:5]
    elif request.user.is_authenticated():
        posts = Post.objects.filter(Q(publish=True) | Q(user=request.user)).order_by("-created")[:5]
    else:
        posts = Post.objects.filter(publish=True).order_by("-created")[:5]

    ctx = {
        "page": "posts",
        "section": "posts",
        "posts": posts,
        "post": posts.first()
    }
    return render(request, "front/posts/show.html", ctx)


def show_post(request, slug):
    if request.user.is_authenticated() and request.user.is_superuser:
        posts = Post.objects.all().order_by("-created")[:5]
    elif request.user.is_authenticated():
        posts = Post.objects.filter(Q(publish=True) | Q(user=request.user)).order_by("-created")[:5]
    else:
        posts = Post.objects.filter(publish=True).order_by("-created")[:5]

    ctx = {
        "page": "show-post",
        "section": "show-post",
        "posts": posts,
        "post": Post.objects.filter(slug=slug).first()
    }
    return render(request, "front/posts/show.html", ctx)


@login_required
def add_post(request):
    if request.user.is_authenticated() and request.user.is_superuser:
        posts = Post.objects.all().order_by("-created")[:5]
    elif request.user.is_authenticated():
        posts = Post.objects.filter(Q(publish=True) | Q(user=request.user)).order_by("-created")[:5]
    else:
        posts = Post.objects.filter(publish=True).order_by("-created")[:5]

    if request.method == "GET":
        form = PostForm()
        ctx = {
            "page": "create-post",
            "section": "create-post",
            "form": form,
            "posts": posts
        }
        return render(request, "front/posts/create.html", ctx)

    if request.method == "POST":
        post = Post()
        form = PostForm(request.POST)
        if form.is_valid():
            post.title = form.cleaned_data["title"]
            post.body = form.cleaned_data["body"]
            post.user = request.user
            post.save()
            return redirect("hc-post")


@login_required
def edit_post(request, slug):
    if request.user.is_authenticated() and request.user.is_superuser:
        posts = Post.objects.all().order_by("-created")[:5]
    elif request.user.is_authenticated():
        posts = Post.objects.filter(Q(publish=True) | Q(user=request.user)).order_by("-created")[:5]
    else:
        posts = Post.objects.filter(publish=True).order_by("-created")[:5]

    post = Post.objects.filter(slug=slug).first()

    if request.method == "GET":
        form = PostForm({"title": post.title, "body": post.body})
        ctx = {
            "page": "edit-post",
            "section": "edit-post",
            "form": form,
            "posts": posts
        }
        return render(request, "front/posts/edit.html", ctx)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post.title = form.cleaned_data["title"]
            post.body = form.cleaned_data["body"]
            post.save()
        return redirect("hc-show-post", post.slug)


@login_required
def delete_post(request, slug):
    post = Post.objects.filter(slug=slug).first()

    if post:
        post.delete()
    return redirect("hc-all-posts")


@login_required
def publish_post(request, slug):
    if request.user.is_superuser:
        post = Post.objects.filter(slug=slug).first()
        state = request.GET.get("state")

        if post:
            post.publish = (state == "true")
            post.save()
    return redirect("hc-all-posts")

@csrf_exempt
@require_POST
def subscribe_to_telegram_bot(request):
    try:
        response = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest()

    if "/start" not in response["message"]["text"]:
        print("Start command: ", response["message"]["text"])
        return HttpResponse()

    chat = response["message"]["chat"]
    name = max(chat.get("title", ""), chat.get("username", ""))

    invite = render_to_string("integrations/telegram_invite.html", {
        "qs": signing.dumps((chat["id"], chat["type"], name)), "site_root": settings.SITE_ROOT
    })

    Telegram.confirm_subscription(chat["id"], invite)
    return HttpResponse()


@login_required
def add_telegram(request):
    chat_id, chat_type, chat_name = None, None, None
    qs = request.META["QUERY_STRING"]
    if qs:
        chat_id, chat_type, chat_name = signing.loads(qs, max_age=600)

    if request.method == "POST":
        channel = Channel(user=request.team.user, kind="telegram")
        channel.value = json.dumps({
            "id": chat_id,
            "type": chat_type,
            "name": chat_name
        })
        channel.save()

        channel.assign_all_checks()
        messages.success(request, "Your Telegram integration has been added!")
        return redirect("hc-channels")

    chat = {"chat_id": chat_id}

    return render(request, "integrations/add_telegram.html", chat)


def docs_faq(request):
    faq_category = FaqCategory.objects.all().order_by('category')
    result = {}
    form = AddFaqForm()
    form_cat = AddFaqCategoryForm()
    for category in faq_category:
        faq_list = list(FaqItem.objects.filter(category=category).order_by('title'))
        if faq_list:
            result[category] = faq_list
    ctx = {
        "page": "docs_faq",
        "faqs": result,
        "form": form,
        "form_cat": form_cat,
        "faq_cats": faq_category
    }

    return render(request, "front/docs_faq.html", ctx)


@login_required
def save_faq(request, id=None):
    if request.method == 'POST':
        if id:
            faq = FaqItem.objects.get(pk=id)
            form = AddFaqForm(data=request.POST, instance=faq)
        else:
            form = AddFaqForm(data=request.POST)
        if form.is_valid():
            form.save()
    return redirect("hc-docs-faq")


@login_required
def faq_edit(request, id):
    faq = FaqItem.objects.get(pk=id)
    form = AddFaqForm(instance=faq)
    ctx = {
        "page": "faq_edit",
        "edit": True,
        "faq_id": faq.id,
        "form": form
    }
    return render(request, "front/edit_faq.html", ctx)


@login_required
def delete_faq(request, id):
    if request.method == 'GET':
        if id:
            FaqItem.objects.filter(pk=id).delete()
            return redirect("hc-docs-faq")
        else:
            return HttpResponse("Operation not allowed")  # pragma: no cover


@login_required
def save_category(request, id=None):
    if request.method == 'POST':
        if id:
            faq_category = FaqCategory.objects.get(pk=id)
            form = AddFaqCategoryForm(data=request.POST, instance=faq_category)
        else:
            form = AddFaqCategoryForm(data=request.POST)
        if form.is_valid():
            form.save()
    return redirect("hc-docs-faq")


@login_required
def faq_cat_edit(request, id=None):
    faq_category = FaqCategory.objects.get(pk=id)
    form = AddFaqCategoryForm(instance=faq_category)
    ctx = {
        "page": "faq_cat_edit",
        "edit": True,
        "cat_id": faq_category.id,
        "form": form
    }
    return render(request, "front/edit_cat.html", ctx)


@login_required
def delete_cat(request, id=None):
    if request.method == 'GET':
        if id:
            FaqCategory.objects.filter(pk=id).delete()
            return redirect("hc-docs-faq")
        else:
            return HttpResponse(u'Operation not allowed')  # pragma: no cover


def docs_help(request):
    ctx = {
        "page": "docs",
        "section": "help",
        "SITE_ROOT": settings.SITE_ROOT,
        "PING_ENDPOINT": settings.PING_ENDPOINT,
        "default_timeout": int(DEFAULT_TIMEOUT.total_seconds()),
        "default_grace": int(DEFAULT_GRACE.total_seconds())
    }

    return render(request, "front/docs_help.html", ctx)
