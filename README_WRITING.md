# SwZap 的 Markdown 写作说明

以后不需要直接编辑 `index.html` 或 `works/*/index.html`。

## 新建作品页

在 `content/works/` 新建一个 `.md` 文件，例如：

`content/works/my-new-piece.md`

最小示例：

```yaml
---
title: 新作品标题
slug: my-new-piece
category: 动画
composer:
  - 作曲家
artist: []
franchise:
  - 动画作品
instrument:
  - 钢琴
description: 一句话简介
youtube:
  id: YouTube视频ID
bilibili:
  - id: BVxxxxxxxxxx
    label: 在 Bilibili 打开
---
```

然后从第二个 `---` 下面开始正常写 Markdown 正文。

## 新建普通音乐随笔

在 `content/notes/` 新建 `.md` 文件。推荐写：

```yaml
---
title: 文章标题
slug: article-slug
date: 2026-11-05
category: 音乐随笔
composer: []
artist: []
franchise: []
instrument: []
description: 一句话简介
---
```

正文同样使用 Markdown。

## 首页顺序

现有 8 篇使用 `weight` 固定当前顺序。新文章通常不要写 `weight`；没有 `weight` 的文章会排在这些旧文章之前，并按 `date` 从新到旧排列。

## 图片

如果有 YouTube 视频，不需要填写缩略图，系统会自动使用 YouTube 缩略图。

若没有 YouTube，可以在 front matter 中指定：

```yaml
thumbnail: img/your-image.jpg
```

## 发布

1. 在 GitHub 网页中打开 Markdown 文件，点铅笔 Edit。
2. 修改正文，可用 GitHub 自带 Preview 检查 Markdown。
3. Commit changes。
4. GitHub Actions 自动生成首页和文章 HTML，并部署 GitHub Pages。

不要直接修改自动生成的 `index.html` 和 `works/*/index.html` 作为长期内容来源；下一次构建时它们会被 Markdown 重新生成。
