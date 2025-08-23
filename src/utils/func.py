import json

def custon_log(func):
    def wrapper(*args, **kwargs):
        parts = []
        for arg in args:
            if type(arg) == str:
                parts.append(arg)
                continue
            try:
                parts.append(json.dumps(arg, ensure_ascii=False))
            except Exception:
                parts.append(str(arg))
        message = "\n".join(parts)
        return func(message, **kwargs)
    return wrapper

def format_filter(message):
    if message["level"].name == "ERROR":
        return "\n[<red>{level}</red>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><red>{message}</red></b>\n"
    elif message["level"].name in ["WARNING", "UNHANDLED", "DEBUG"]:
        return "\n[<yellow>{level}</yellow>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><yellow>{message}</yellow></b>\n"
    else:
        return "\n[<green>{level}</green>]\n\n| Time: <b><green>{time:YYYY-MM-DD HH:mm:ss}</green></b>\n| File-func-line: <cyan>{name}:{function}:</cyan><red>{line}</red>\n<b><green>{message}</green></b>\n"

def filter_level(record, level):
    return record["level"].name == level