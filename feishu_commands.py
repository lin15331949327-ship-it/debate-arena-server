"""feishu_commands.py - Debate command definitions"""
import sys
sys.path.insert(0, "E:/debate-arena")

COMMANDS = {
    "debate": {
        "help": "/debate [topic] - Start a 3-agent debate",
        "handler": "feishu_handler.handle_debate_command",
        "examples": [
            "/debate 自由是什么",
            "/debate history",
            "/debate rounds 6 科技的发展是否让人类更幸福",
        ]
    }
}

def get_command_list():
    return list(COMMANDS.keys())

def get_command_help(cmd):
    return COMMANDS.get(cmd, {}).get("help", "Unknown command")
