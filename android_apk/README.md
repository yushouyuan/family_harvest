APK 打包说明（Cordova / Capacitor 快速入门）

目标：把当前网站以 APK 形式封装到 Android 设备上，使其能在 HTTP（非 HTTPS）下使用麦克风录音。

推荐：使用 Capacitor（现代、与 Web 项目集成友好）或 Cordova（兼容旧插件生态）。下面给出 Capacitor 与 Cordova 的关键步骤与示例配置。

安全与权限要点：
- 需要授予 `RECORD_AUDIO` 权限。
- Android 9+ 对 HTTP（明文流量）有额外限制：需要在 `AndroidManifest.xml` 或 network security config 中允许明文流量（`usesCleartextTraffic` 或 `network_security_config.xml`）。
- WebView 默认可能阻止混合内容（HTTPS 页面加载 HTTP 资源），需要在原生 WebView 中允许混合内容（setMixedContentMode）。

一、Capacitor（推荐）

1. 安装并初始化：

```bash
npm install @capacitor/cli @capacitor/core --save
npx cap init family_harvest_app com.example.familyharvest
```

2. 把网页作为远程 URL 或者本地 `www` 内容：
- 若加载远程 HTTP 地址（例如 `http://192.168.0.10:8000`），请确保 Android 允许明文流量和混合内容（见下面 network config）。

3. 添加 Android 平台并打开工程：

```bash
npx cap add android
npx cap open android
```

4. 在 Android Studio 中：
- 在 `AndroidManifest.xml` 的 `<application>` 上添加 `android:usesCleartextTraffic="true"`（或使用 `networkSecurityConfig` 指定白名单）。
- 在 `app/src/main/res/xml/` 下添加 `network_security_config.xml`（示例见本目录），并在 `AndroidManifest.xml` 中引用：
  `<application android:networkSecurityConfig="@xml/network_security_config" ...>`
- 在 `MainActivity` 或 WebView 初始化处调用 `getBridge().getWebView().getSettings().setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);`（或在 `AndroidManifest` 中调整 WebView 设置，根据 Capacitor 版本选用合适方法）。

5. 授权权限：在 `AndroidManifest.xml` 添加：

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```

6. 构建 APK：

```bash
npm run build   # 如果你有前端构建步骤
npx cap copy android
npx cap sync android
# 在 Android Studio 中构建 release 或直接使用 gradlew
```

二、Cordova 示例（如果你选择 Cordova）

1. 安装与初始化：

```bash
npm install -g cordova
cordova create family_harvest_app
cd family_harvest_app
cordova platform add android
```

2. 使用 `config.xml`（本目录提供 `config.xml` 示例），示例包含 `edit-config` 修改 `AndroidManifest` 的方式以加入权限与 networkSecurityConfig。常用插件：
- `cordova-plugin-whitelist`（允许外部访问）
- `cordova-plugin-media` / 原生权限插件（视需要）

3. 构建：

```bash
cordova build android --release
```

三、允许明文 HTTP 与混合内容关键示例

- 在 `network_security_config.xml` 中可对特定域允许明文流量，也可以全局允许（仅开发/内网环境推荐）：见本目录 `network_security_config.xml` 示例。
- 在 WebView 中允许混合内容以确保录音脚本正常工作。

四、常见问题与调试
- 若录音无法启动：检查是否已授予麦克风权限（运行时请求）；在 Android 设置中确认 App 拥有麦克风权限。
- 若页面因为 HTTP 被阻止：确认 `usesCleartextTraffic` 或 `network_security_config` 已生效，并在 WebView 中允许混合内容。
- 若打包后想使用远程开发服务器：在 `AndroidManifest` 中配置好域名白名单，或将前端构建到本地 `www`。

示例文件位于本目录：
- `config.xml`：Cordova 示例配置
- `network_security_config.xml`：允许明文流量示例

如果你希望我为你：
- 生成一个完整的 Cordova 项目脚手架（含 `config.xml` 与插件），或
- 给出 Capacitor 项目具体的 Android Studio 修改步骤并生成示例 `network_security_config.xml`，
请告诉我你倾向 Cordova 还是 Capacitor，我会继续接着创建或演示。 
