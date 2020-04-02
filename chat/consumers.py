import re
import json
import logging
from channels import Group
from channels.sessions import channel_session
from .models import Room

log = logging.getLogger(__name__)

@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'chat':
            log.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return

    log.debug('chat connect room=%s client=%s:%s',
        room.label, message['client'][0], message['client'][1])

    # Need to be explicit about the channel layer so that testability works
    # This may be a FIXME?
    Group('chat-'+label, channel_layer=message.channel_layer).add(message.reply_channel)

    message.channel_session['room'] = room.label

@channel_session
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        log.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        log.debug('recieved message, buy room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", text)
        return

    if data:
        log.debug('chat message room=%s handle=%s type=%s',
            room.label, data['handle'], data['type'])
        if data['type'] == 'start':
            log.debug('room players' + str(room.players.count()))
            if room.players.count() == 5 or room.players.count() == 7:
                room.locked = True
                room.save()
                log.debug(room.as_dict())
                Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(room.as_dict())})
            else:
                Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(room.as_dict())})
        if data['type'] == 'join':
            names = []
            for player in room.players.all():
                names.append(player.handle)
            if data['handle'] not in names:
                p = room.players.create(handle=data['handle'])
                Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(p.as_dict())})
            else:
                Channel(message.reply_channel).send({'text': json.dumps({'type': 'alert', 'message': 'handle already used in room, please choose another'}))
        if data['type'] == 'dm':
            m = room.messages.create(**data)
            # See above for the note about Group
            Group('chat-'+label, channel_layer=message.channel_layer).send({'text': json.dumps(m.as_dict())})

@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label, channel_layer=message.channel_layer).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass
