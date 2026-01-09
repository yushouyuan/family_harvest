## 对该项目进行以下改造
### 1 新增功能：TTS
调用国内稳定的免费TTS服务，当用户完成录音，单击保存后，调用tts服务，把DailyRecord.audio录音转换为文字，附加到DailyRecord.text最后面（如果之前有已填写的text内容，保留）

### 2 增加android apk
把客户端封装为apk，可以手动安装apk到android手机上，并且绕过因http链接导致的无法使用录音功能

### 注意事项
该网站是http链接，android会限制浏览器调用录音功能
完整阅读整个项目，同步修改dockfile、readme、requirements等文件


#### 关键步骤
关键步骤：

将Django静态文件构建到mobile/www/

使用Capacitor同步Android项目

在云端配置Android SDK

构建APK并自动分发