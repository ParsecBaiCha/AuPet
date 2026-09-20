# AI 通识课教师头像

使用内置 image_gen 工具生成。小学使用 xiaozhi.png（小知老师），初高中使用 zhixing.png（知行老师）。两张均为新生成的虚构人物。

## 小知老师最终提示词

A square avatar illustration for a Chinese primary school AI course assistant called 小知老师. Single human chibi little teacher, friendly round face, short dark hair, round glasses, warm smile, soft yellow cardigan over white shirt, carrying a small teal book and a teaching pencil, small backpack straps. Polished charming children educational app illustration, clean soft shapes, readable at 48px, centered head and upper torso with breathing room, light warm cream background, no text, no animals, no pet features. Save as project avatar.

## 知行老师最终提示词

A square avatar illustration for a Chinese middle and high school AI course assistant called 知行老师. Single human young adult teacher, short dark hair, subtle round glasses, friendly thoughtful confident expression, white shirt under muted teal casual jacket, holding a slim tablet. Polished clean contemporary educational editorial illustration, mature proportions rather than chibi, soft shading, centered head and upper torso with breathing room, pale blue background, readable at 48px, no text, no animals. Visually warm and approachable, not childish.

## 部署

先在业务数据库执行 database/20260918_chat_teachers.sql，再重启后端并更新前端。迁移可重复执行。旧聊天记录保留在知心畅聊，今后 AI 通识课的对话和清空操作单独处理。
