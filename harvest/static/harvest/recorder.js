function initRecorder(opts) {
  const btn = document.getElementById(opts.buttonId);
  const status = document.getElementById(opts.statusId);
  let mediaRecorder = null;
  let chunks = [];
  let stream = null;

  // 处理浏览器前缀问题
  const navigator = window.navigator || {};
  navigator.mediaDevices = navigator.mediaDevices || {};

  // 初始化
  console.log("Recorder initialized with options:", opts);

  // 1. 浏览器支持检测
  const checkSupport = () => {
    console.log("Checking browser support...");

    // 检查getUserMedia支持
    if (!navigator.mediaDevices.getUserMedia) {
      // 旧版浏览器支持
      navigator.mediaDevices.getUserMedia = (constraints) => {
        const getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;

        if (!getUserMedia) {
          return Promise.reject(new Error('getUserMedia is not implemented in this browser'));
        }

        return new Promise((resolve, reject) => {
          getUserMedia.call(navigator, constraints, resolve, reject);
        });
      };
    }

    // 检查MediaRecorder支持
    const MediaRecorder = window.MediaRecorder || window.webkitMediaRecorder || window.mozMediaRecorder || window.msMediaRecorder;

    if (!MediaRecorder) {
      console.error("MediaRecorder is not supported");
      return false;
    }

    return true;
  };

  // 2. 检查浏览器支持
  if (!checkSupport()) {
    status.textContent = '抱歉，您的浏览器不支持录音功能，请使用最新版Chrome浏览器';
    btn.disabled = true;
    return;
  }

  // 3. 媒体录制器配置
  const MediaRecorder = window.MediaRecorder || window.webkitMediaRecorder || window.mozMediaRecorder || window.msMediaRecorder;

  // 4. 开始录音
  const startRecording = async () => {
    try {
      status.textContent = "正在请求麦克风权限...";
      chunks = [];

      // 请求麦克风权限
      // 移动端必须从用户交互（如点击按钮）中调用
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          // 简单配置以提高兼容性
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      console.log("麦克风权限已获取");

      // 创建媒体录制器
      // 移动端Chrome/Firefox支持基本配置
      mediaRecorder = new MediaRecorder(stream);

      // 监听数据可用事件
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      // 监听录制停止事件
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mediaRecorder.mimeType });

        // 清理资源
        cleanup();

        // 触发回调
        if (opts.onStop) {
          opts.onStop(blob);
        }

        status.textContent = "录音已完成";
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-secondary');
      };

      // 开始录制
      mediaRecorder.start();

      status.textContent = "录音中...点击按钮停止";
      btn.classList.remove('btn-secondary');
      btn.classList.add('btn-danger');

      console.log("录音开始");

    } catch (error) {
      handleError(error);
    }
  };

  // 5. 停止录音
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      console.log("录音停止");
    }
  };

  // 6. 清理资源
  const cleanup = () => {
    if (mediaRecorder) {
      mediaRecorder = null;
    }

    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }

    chunks = [];
    console.log("资源已清理");
  };

  // 7. 错误处理
  const handleError = (error) => {
    console.error("录音错误:", error);

    let errorMsg = "录音失败: ";

    switch (error.name || error.code) {
      case "NotAllowedError":
      case 1: // Permission denied
        errorMsg += "请允许麦克风权限";
        break;
      case "NotFoundError":
      case 2: // NotFoundError
        errorMsg += "未检测到麦克风";
        break;
      case "NotReadableError":
      case 3: // NotReadableError
        errorMsg += "麦克风不可用";
        break;
      default:
        errorMsg += "未知错误，请检查浏览器设置";
    }

    status.textContent = errorMsg;

    // 清理资源
    cleanup();

    // 恢复按钮状态
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-secondary');
  };

  // 8. 绑定按钮事件
  // 确保在用户交互上下文中调用getUserMedia
  btn.addEventListener('click', async () => {
    console.log("按钮点击事件触发");

    if (mediaRecorder && mediaRecorder.state === "recording") {
      // 停止录音
      stopRecording();
    } else {
      // 开始录音
      await startRecording();
    }
  });

  console.log("Recorder setup completed");
}
