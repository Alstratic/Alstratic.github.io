# Alstratic.github.io

Bingxu An (安炳旭) 的个人主页：https://alstratic.github.io/

基于 [Luka Homepage Template](https://github.com/wzsyyh/luka-homepage-template)，纯静态 HTML，不需要 Jekyll 或任何构建步骤。

## 修改内容

- `index.html`：所有页面内容。文件底部的注释里有 Experience / Projects / Publications / Awards 的现成代码块，需要时复制到正文里修改即可。
- `assets/css/custom.css`：本站自己的样式调整（中文字体、News 列表、图标等）。
- `assets/css/theme-luka.css`：模板原始样式，尽量不改，方便以后同步上游。
- `assets/img/`：头像、favicon、学校图标（`ucas.svg` / `hqu.svg` 是简单的字母徽标，可以换成官方校徽）。

## 本地预览

```bash
python3 -m http.server 8000
```

然后打开 http://localhost:8000

## 部署

推送到 GitHub 后，GitHub Pages 会直接发布仓库根目录（`.nojekyll` 用来跳过 Jekyll 处理）。

## 第三方资源

- 模板：Luka Homepage Template，MIT License（见 `LICENSE.md`）
- 字体：Inter，SIL Open Font License 1.1（见 `assets/fonts/Inter-OFL.txt`）
- 图标：GitHub Octicons，MIT License
