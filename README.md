## 语音转写（STT）集成

本项目新增了保存时自动将上传音频转写为文字并追加到记录的功能（可选）。默认实现使用百度语音识别 API。
- 配置项（在环境变量或 `settings.py` 中设置）:
    - `BAIDU_API_KEY`：百度开放平台 API Key（client_id）
    - `BAIDU_SECRET_KEY`：百度开放平台 Secret Key（client_secret）

- 运行依赖：`requests`、`pydub`，并需要在系统中安装 `ffmpeg`（Dockerfile 已添加安装）。

- 使用方式：在录音并保存后，后台会尝试将 `media/audio_records/...` 的音频转为 WAV(16k, mono)，调用百度 ASR 接口并把识别结果追加到 `DailyRecord.text` 字段末尾。

如果不希望启用该功能，请不要设置 `BAIDU_API_KEY` / `BAIDU_SECRET_KEY` 环境变量。

## Android APK 打包（客户端封装）
由于浏览器在非 HTTPS 页面上可能被限制调用麦克风（尤其是 Android），建议将前端封装为原生 APK（WebView / Cordova / Capacitor）。下面给出快速入门步骤：

1. 安装 Cordova：

```bash
npm install -g cordova
cordova create family_harvest_app
cd family_harvest_app
cordova platform add android
```

2. 将网站作为 `www` 内容或设置 WebView 加载远程 HTTP 地址（推荐打包为一个允许混合内容的 WebView 并授予麦克风权限）。

3. 编辑 `config.xml`，添加权限：

```xml
<platform name="android">
    <edit-config file="app/src/main/AndroidManifest.xml" mode="merge" target="/manifest">
        <uses-permission android:name="android.permission.RECORD_AUDIO" />
        <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    </edit-config>
```

4. 在 Android 10+ 需要在 WebView 中允许混合内容：修改原生代码或使用适配插件，构建时确保 targetSdk 与权限处理正确。

5. 构建 APK：

```bash
cordova build android --release
```

详细步骤会因 Cordova/Capacitor/Android Studio 版本而异，仓库中包含 `android_apk/README.md` 提示更详细的参考与示例配置。

# 家庭每日收获记录（Django 示例）

快速启动（开发）：

1. 创建并激活虚拟环境

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置数据库（local 或 docker-compose）并设置环境变量（可在 `.env` 中）

3. 运行迁移并创建预设用户

```bash
python manage.py migrate
python manage.py create_members
python manage.py runserver
```

4. 打开 http://127.0.0.1:8000/login/ 登录并开始使用。

语音文件存放在 `media/audio_records/`，已在 `settings.py` 配置 `MEDIA_ROOT` 与 `MEDIA_URL`。

Docker 使用（示例）:

- 构建并启动服务（本地开发/测试）:

```bash
docker-compose build
docker-compose up -d
# 首次运行或代码变更后，检查迁移和静态文件（entrypoint 已自动处理 ）
docker-compose logs -f web
```

- 说明:
	- 镜像启动时 `entrypoint.sh` 会运行 `manage.py migrate` 与 `collectstatic`，然后启动 `gunicorn`。
	- 上传的媒体文件将保存在 `docker-compose` 定义的 `media` 卷中（映射到容器 `/app/media`）。

请在生产环境中把数据库密码、`SECRET_KEY` 等敏感配置通过环境变量或 secret 管理，不要直接提交到代码库。

## 项目架构

```
家庭每日收获记录工具
├── 核心技术栈
│   ├── 后端: Django 4.x
│   ├── 数据库: SQLite
│   ├── 前端: Bootstrap 5 + 原生 JavaScript
│   └── 语音录制: MediaRecorder API
├── 目录结构
│   ├── family_harvest/       # Django 项目配置目录
│   │   ├── __init__.py
│   │   ├── settings.py       # 项目配置
│   │   ├── urls.py           # 根 URL 配置
│   │   └── wsgi.py           # WSGI 配置
│   ├── harvest/              # 主应用目录
│   │   ├── __init__.py
│   │   ├── admin.py          # 后台管理配置
│   │   ├── forms.py          # 表单定义
│   │   ├── models.py         # 数据模型
│   │   ├── views.py          # 视图逻辑
│   │   ├── urls.py           # 应用 URL 配置
│   │   ├── management/       # 自定义管理命令
│   │   │   └── commands/
│   │   │       └── create_members.py  # 创建预设家庭成员
│   │   ├── migrations/       # 数据库迁移文件
│   │   ├── static/           # 静态资源
│   │   │   ├── bootstrap/    # Bootstrap 框架
│   │   │   └── harvest/      # 应用静态资源
│   │   ├── templates/        # 模板文件
│   │   │   └── harvest/      # 应用模板
│   │   └── templatetags/     # 自定义模板标签
│   ├── media/                # 上传文件存储目录
│   ├── .env                  # 环境变量配置（示例）
│   ├── .gitignore
│   ├── README.md
│   ├── requirements.txt      # 依赖声明
│   └── manage.py             # Django 管理脚本
├── 核心功能
│   ├── 用户认证: 四位预设家庭成员，无需注册
│   ├── 每日记录: 文字输入 + 语音录制上传
│   ├── 家庭汇总: 每日四人收获卡片展示
│   ├── 历史记录: 按时间线展示所有记录
│   └── 个人统计: 个人记录统计（可选）
└── 页面结构
    ├── 登录页面 (login.html)
    ├── 主页 (index.html) - 今日家庭汇总
    ├── 记录编辑页 (record_form.html) - 文字+语音输入
    ├── 历史记录页 (history.html)
    └── 个人统计页 (stats.html) - 可选
```
