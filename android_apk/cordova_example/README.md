Cordova 示例项目（位于 `android_apk/cordova_example`）

快速开始：

1. 安装依赖并初始化 Cordova（需要全局 cordova）

```bash
# 在项目目录下
cd android_apk/cordova_example
npm install
npx cordova platform add android
```

2. 添加插件（示例）:

```bash
npx cordova plugin add cordova-plugin-whitelist
npx cordova plugin add cordova-plugin-android-permissions
```

3. 构建并运行（连接设备或模拟器）：

```bash
npm run build-android
npm run run-android
```

注意：
- 修改 `www/index.html` 中的 URL 为你的本地开发地址（例如 `http://192.168.0.10:8000`）。
- 确保 `android_apk/network_security_config.xml` 可用并在 `config.xml` 中通过 `edit-config` 引用。
- 生产环境请采用 HTTPS，或在 `network_security_config.xml` 中仅对白名单域允许明文。
