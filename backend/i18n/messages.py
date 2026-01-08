from enum import Enum
from typing import Any


class Locale(str, Enum):
    EN_US = "en-US"
    ZH_CN = "zh-CN"


MESSAGES: dict[str, dict[Locale, str]] = {
    "EMPTY_INPUT": {
        Locale.EN_US: "Please enter a math problem",
        Locale.ZH_CN: "请输入一道数学题",
    },
    "TOO_LONG": {
        Locale.EN_US: "Problem is too long, please shorten it",
        Locale.ZH_CN: "题目太长了，请精简后重试",
    },
    "NOT_MATH": {
        Locale.EN_US: "This doesn't look like a math problem. Please try entering a math problem",
        Locale.ZH_CN: "这看起来不是数学题，请输入一道数学题试试",
    },
    "SESSION_NOT_FOUND": {
        Locale.EN_US: "Session not found",
        Locale.ZH_CN: "会话不存在",
    },
    "SESSION_COMPLETED": {
        Locale.EN_US: "Session has ended",
        Locale.ZH_CN: "会话已结束",
    },
    "RESPONSE_TOO_SHORT": {
        Locale.EN_US: "Can you write a bit more about your thinking?",
        Locale.ZH_CN: "能再多写一点你的想法吗？",
    },
    "PROBLEM_NOT_FOUND": {
        Locale.EN_US: "Problem not found",
        Locale.ZH_CN: "题目不存在",
    },
    "REVEAL_NOT_ALLOWED": {
        Locale.EN_US: "Please complete all hint layers first",
        Locale.ZH_CN: "请先完成所有提示层级",
    },
    "COMPLETE_NOT_ALLOWED": {
        Locale.EN_US: "Please complete more hints first",
        Locale.ZH_CN: "请先完成更多提示",
    },
    "COMPLETE_SUCCESS": {
        Locale.EN_US: "Congratulations! You solved this problem independently!",
        Locale.ZH_CN: "恭喜你独立完成了这道题！",
    },
    "CONFUSION_ENCOURAGEMENT": {
        Locale.EN_US: "That's okay, let's think about it some more!",
        Locale.ZH_CN: "没关系，再想想看！",
    },
    "DOWNGRADE_MESSAGE": {
        Locale.EN_US: "Let me help you understand this concept from a different angle!",
        Locale.ZH_CN: "让我换个角度来帮你理解这个概念！",
    },
    "LIMIT_REACHED": {
        Locale.EN_US: "You've reached your daily limit. Upgrade to Pro for unlimited problems!",
        Locale.ZH_CN: "已达到每日限制，升级到Pro版获取无限题目！",
    },
}

DEFAULT_LOCALE = Locale.EN_US


def get_message(key: str, locale: Locale | str | None = None, **kwargs: Any) -> str:
    if locale is None:
        locale = DEFAULT_LOCALE
    elif isinstance(locale, str):
        try:
            locale = Locale(locale)
        except ValueError:
            locale = DEFAULT_LOCALE

    messages = MESSAGES.get(key, {})
    message = messages.get(locale, messages.get(DEFAULT_LOCALE, key))

    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            pass

    return message
