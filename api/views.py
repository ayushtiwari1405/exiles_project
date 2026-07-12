import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from .models import User, Conversation, Message, Games

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=409)
        
        hashed_pw = make_password(password)
        user = User(username=username, password_hash=hashed_pw)
        user.save()
        
        return JsonResponse({
            'id': user.id,
            'username': user.username
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
        
        if not check_password(password, user.password_hash):
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
        
        request.session['user_id'] = user.id
        return JsonResponse({
            'id': user.id,
            'username': user.username
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def search_users(request):
    if not request.user or isinstance(request.user, AnonymousUser):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    query = request.GET.get('search', '')
    if not query:
        users = User.objects.all()
    else:
        users = User.objects.filter(username__icontains=query)
    
    users = users.exclude(pk=request.user.id)
    
    results = [{'id': u.id, 'username': u.username} for u in users]
    return JsonResponse(results, safe=False, status=200)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def conversations_view(request):
    if not request.user or isinstance(request.user, AnonymousUser):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if request.method == "GET":
        convs = Conversation.objects.filter(
            Q(part_1=request.user) | Q(part_2=request.user)
        ).order_by('-last_update')
        
        results = []
        for c in convs:
            other_user = c.part_2 if c.part_1_id == request.user.id else c.part_1
            results.append({
                'id': c.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username
                },
                'last_update': c.last_update.isoformat()
            })
        return JsonResponse(results, safe=False, status=200)
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            recipient_id = data.get('recipient_id')
            if not recipient_id:
                return JsonResponse({'error': 'recipient_id is required'}, status=400)
            
            if int(recipient_id) == request.user.id:
                return JsonResponse({'error': 'Cannot start a conversation with yourself'}, status=400)
            
            try:
                recipient = User.objects.get(pk=recipient_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Recipient does not exist'}, status=404)
            
            conv = Conversation.objects.filter(
                (Q(part_1=request.user) & Q(part_2=recipient)) |
                (Q(part_1=recipient) & Q(part_2=request.user))
            ).first()
            
            if not conv:
                conv = Conversation(part_1=request.user, part_2=recipient)
                conv.save()
            
            other_user = conv.part_2 if conv.part_1_id == request.user.id else conv.part_1
            return JsonResponse({
                'id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username
                },
                'last_update': conv.last_update.isoformat()
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def conversation_messages_view(request, id):
    if not request.user or isinstance(request.user, AnonymousUser):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        conv = Conversation.objects.get(pk=id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    
    if request.user.id != conv.part_1_id and request.user.id != conv.part_2_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    conv.save()
    
    cursor = request.GET.get('after')
    messages_query = Message.objects.filter(conv=conv)
    
    if cursor:
        try:
            cursor_id = int(cursor)
            messages_query = messages_query.filter(id__gt=cursor_id)
        except ValueError:
            return JsonResponse({'error': 'Invalid cursor format'}, status=400)
    
    messages_query = messages_query.order_by('id')
    
    if not cursor:
        messages_query = messages_query[max(0, messages_query.count() - 50):]
    
    results = []
    for msg in messages_query:
        results.append({
            'id': msg.id,
            'conv_id': msg.conv_id,
            'sender_id': msg.sender_id,
            'message_type': msg.message_type,
            'content': msg.content,
            'created_at': msg.created_at.isoformat()
        })
    
    return JsonResponse(results, safe=False, status=200)


import time
from django.core.cache import cache

@csrf_exempt
@require_http_methods(["POST"])
def send_message_view(request):
    if not request.user or isinstance(request.user, AnonymousUser):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # TC-11: Rate Limiting: 50 messages in 2 seconds
    rate_limit_key = f"rate_limit_{request.user.id}"
    now = time.time()
    timestamps = cache.get(rate_limit_key, [])
    timestamps = [t for t in timestamps if now - t <= 2.0]
    if len(timestamps) >= 50:
        return JsonResponse({'error': 'Rate limit exceeded. Too many messages.'}, status=429)
    timestamps.append(now)
    cache.set(rate_limit_key, timestamps, timeout=2)
    
    try:
        data = json.loads(request.body)
        conv_id = data.get('conv_id')
        message_type = data.get('message_type')
        content = data.get('content')
        client_tx_id = data.get('client_tx_id')
        
        if not conv_id or not message_type or not content:
            return JsonResponse({'error': 'conv_id, message_type, and content are required'}, status=400)
        
        if message_type not in ['text', 'games']:
            return JsonResponse({'error': "message_type must be 'text' or 'games'"}, status=400)
        
        try:
            conv = Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversation not found'}, status=404)
        
        if request.user.id != conv.part_1_id and request.user.id != conv.part_2_id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # TC-12: Duplicate message prevention using client_tx_id
        if client_tx_id:
            existing_msg = Message.objects.filter(sender=request.user, client_tx_id=client_tx_id).first()
            if existing_msg:
                return JsonResponse({
                    'id': existing_msg.id,
                    'conv_id': existing_msg.conv_id,
                    'sender_id': existing_msg.sender_id,
                    'message_type': existing_msg.message_type,
                    'content': existing_msg.content,
                    'client_tx_id': existing_msg.client_tx_id,
                    'created_at': existing_msg.created_at.isoformat()
                }, status=201)
        
        msg = Message(
            conv=conv,
            sender=request.user,
            message_type=message_type,
            content=content,
            client_tx_id=client_tx_id
        )
        msg.save()
        
        conv.save()
        
        return JsonResponse({
            'id': msg.id,
            'conv_id': msg.conv_id,
            'sender_id': msg.sender_id,
            'message_type': msg.message_type,
            'content': msg.content,
            'client_tx_id': msg.client_tx_id,
            'created_at': msg.created_at.isoformat()
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def games_view(request):
    if not request.user or isinstance(request.user, AnonymousUser):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    games_list = Games.objects.all()
    results = []
    for g in games_list:
        results.append({
            'id': g.id,
            'title': g.title,
            'desc': g.desc,
            'url': g.url
        })
    return JsonResponse(results, safe=False, status=200)
