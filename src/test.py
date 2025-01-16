

from asbot import AsBot
import json
bot = AsBot('人机')
content = {
    "zh_cn": {
    "title": "这是一个标题",
      "content": [[
        {
          "tag": "text",
          "text": "你懂我意思嘛😭😭😭😭，gump",
          "style":["bold", "italic"],
        },
          {
              "tag": "at",
              "user_id": "all",
          }
      ],]
    }
  }


# bot.send_post_to_group(content)
bot.send_text_to_group('wdwd')