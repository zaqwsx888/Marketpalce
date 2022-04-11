from django.template.defaulttags import register


@register.filter
def get_phone_message(value):
    if value != '':
        if value.get("phone") is not None:
            return value.get("phone")[0]['message']
        else:
            return ''
    else:
        return value


@register.filter
def get_password_message(value):
    if value != '':
        if value.get("__all__") is not None:
            return value.get("__all__")[0]['message']
        else:
            return ''
    else:
        return value


@register.filter
def get_email_message(value):
    if value != '':
        if value.get("email") is not None:
            return value.get("email")[0]['message']
        return ''
    else:
        return value


@register.filter
def get_avatar_message(value):
    if value != '':
        if value.get("avatar") is not None:
            return value.get("avatar")[0]['message']
        return ''
    else:
        return value
