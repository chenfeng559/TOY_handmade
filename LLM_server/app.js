/**
 * 从第一次发起RunSynthesis指令发送文本开始，到收到SynthesisCompleted之间会收到音频流。

在流式语音合成中，是将一个完整的音频文件分多次返回。在播放流式音频时，需要使用支持流式播放的音频播放器，而不是将每一帧当作一个独立的音频播放，这样无法成功解码。

在保存音频时，请使用追加模式写入同一个文件。

在使用wav/mp3格式合成音频时，由于文件按照流式合成，因此只在第一帧中包含当前任务的文件头信息。
 */


(function () {
    /**
     * 生成32位随机字符串
     * @returns {string} 随机字符串
     */
    function generateUUID() {
        let d = new Date().getTime();
        let d2 = (performance && performance.now && (performance.now()*1000)) || 0;
        return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            let r = Math.random() * 16; //random number between 0 and 16
            if(d > 0){
                r = (d + r)%16 | 0;
                d = Math.floor(d/16);
            } else {
                r = (d2 + r)%16 | 0;
                d2 = Math.floor(d2/16);
            }
            return (c == 'x' ? r :(r&0x3|0x8)).toString(16);
        });
    }

    /**
     * 生成 WebSocket 消息的头部信息
     * @returns {Object} 包含头部信息的对象
     */
    const getHeader = () => {
        const timestamp = Date.now(); // 获取当前时间戳
        return {
            message_id: generateUUID(), // 消息ID，包含随机值以确保唯一性
            task_id: task_id, // 任务ID，包含时间戳和随机值以确保唯一性
            namespace: 'FlowingSpeechSynthesizer', // 命名空间
            name: '', // 消息名称，初始化为空
            appkey: appkey, // 应用密钥
        };
    };
    /**
     * appkey和token需要替换为实际的值
     */
    let appkey = 'your-nls-appkey'
    let token = 'your-nls-token'
    let ws = null; // WebSocket 实例
    let task_id = null;
    let isSynthesisStarted = false; // 状态变量，用于跟踪合成是否已经开始

    /**
     * 发送 RunSynthesis 指令
     * @param {string} text - 要合成的文本
     */
    const sendRunSynthesis = (text) => {
        if (ws && isSynthesisStarted) { // 确保 WebSocket 连接已经建立并且合成已经开始
            const header = getHeader(); // 获取新的头部信息
            const params = {
                header: { ...header, name: 'RunSynthesis' }, // 更新消息头部信息中的名称为 'RunSynthesis'
                payload: {
                    text, // 要合成的文本
                },
            };
            ws.send(JSON.stringify(params)); // 发送消息
        } else {
            console.error('Cannot send RunSynthesis: Synthesis has not started');
        }
    };

    /**
     * 发送 StopSynthesis 指令
     */
    const sendStopSynthesis = () => {
        if (ws && isSynthesisStarted) { // 确保 WebSocket 连接已经建立并且合成已经开始
            const header = getHeader(); // 获取新的头部信息
            const params = {
                header: { ...header, name: 'StopSynthesis' }, // 更新消息头部信息中的名称为 'StopSynthesis'
            };
            ws.send(JSON.stringify(params)); // 发送消息
        } else {
            console.error('Cannot send StopSynthesis: Synthesis has not started');
        }
    };

    /**
     * 开始连接 WebSocket 并处理语音合成数据
     * @param {MediaSource} mediaSource - 音频输出的目标 MediaSource 实例
     */
    const connectAndStartSynthesis = (mediaSource) => {
        const sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg'); // 创建 SourceBuffer 对象以处理音频数据
        const queue = []; // 队列，用于管理待处理的音频数据
        ws = new WebSocket('wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1?token=' + token); // 初始化 WebSocket 连接
        // 当 WebSocket 连接打开后发送 StartSynthesis 指令
        ws.onopen = () => {
            if (ws.readyState === WebSocket.OPEN) {
                task_id = generateUUID();
                const header = getHeader(); // 获取新的头部信息
                const params = {
                    header: { ...header, name: 'StartSynthesis' }, // 更新消息头部信息中的名称为 'StartSynthesis'
                    payload: {
                        voice: 'zhixiaoxia', // 选择音色
                        format: 'MP3', // 文件格式
                        sample_rate: 16000, // 采样率
                        volume: 100, // 音量
                        speech_rate: 0, // 语速
                        pitch_rate: 0, // 音调
                        enable_subtitle: true, // 是否启用字幕
                        platform: 'javascript'
                    },
                };
                ws.send(JSON.stringify(params)); // 发送开始合成消息
            }
        };
        // 当 WebSocket 连接发生错误时触发
        ws.onerror = (err) => {
            console.error(err);
            mediaSource.endOfStream(); // 结束 MediaSource 流
        };
        // 当 WebSocket 连接关闭时触发
        ws.onclose = (err) => {
            console.info(err);
            mediaSource.endOfStream(); // 结束 MediaSource 流
        };
        // 当 WebSocket 收到消息时触发
        ws.onmessage = (event) => {
            const data = event.data;
            // 如果收到的是二进制数据（Blob 类型）
            if (data instanceof Blob) {
                const reader = new FileReader(); // 创建 FileReader 对象读取二进制数据
                reader.onload = () => {
                    const arrayBuffer = reader.result; // 获取读取结果（ArrayBuffer）
                    queue.push(arrayBuffer); // 将数据添加到队列
                    processQueue(); // 处理队列中的数据
                };
                reader.readAsArrayBuffer(data); // 读取 Blob 数据为 ArrayBuffer
            } else { // 如果收到的是文本消息
                const body = JSON.parse(data); // 解析 JSON 数据
                console.log('* text msg', body);
                // 如果消息名称为 'SynthesisStarted' 指令 且状态为成功
                if (body.header.name === 'SynthesisStarted' && body.header.status === 20000000) {
                    isSynthesisStarted = true; // 更新合成状态为已经开始
                }
                // 如果消息名称为 'SynthesisCompleted' 指令 且状态为成功
                if (body.header.name === 'SynthesisCompleted' && body.header.status === 20000000) {
                    ws.close(); // 关闭 WebSocket 连接
                    ws = null; // 重置 WebSocket 实例
                    isSynthesisStarted = false; // 更新合成状态为未开始
                }
            }
        };
        /**
         * 处理队列中的音频数据
         */
        const processQueue = () => {
            if (queue.length > 0 && !sourceBuffer.updating) { // 确保队列中有数据且 SourceBuffer 未在更新中
                sourceBuffer.appendBuffer(queue.shift()); // 从队列中取出数据并添加到 SourceBuffer
            }
        };
        // 监听 SourceBuffer 的 updateend 事件，处理队列中的数据
        sourceBuffer.addEventListener('updateend', processQueue);
    };

    // 设置 start 按钮的点击事件
    document.querySelector('#button-start').addEventListener('click', () => {
        const mediaSource = new MediaSource(); // 创建 MediaSource 实例
        const player = document.getElementById('player'); // 获取播放器元素
        player.src = URL.createObjectURL(mediaSource); // 设置播放器的源为 MediaSource 对象
        // 监听 MediaSource 的 sourceopen 事件
        mediaSource.addEventListener('sourceopen', () => {
            connectAndStartSynthesis(mediaSource); // 开始 WebSocket 连接和语音合成
            player.play(); // 播放音频
        });
    });
    // 设置 run 按钮的点击事件，发送合成文本消息
    document.querySelector('#button-run').addEventListener('click', () => {
        sendRunSynthesis('欢迎使用阿里云语音服务。');
    });
    // 设置 stop 按钮的点击事件，发送停止合成消息
    document.querySelector('#button-stop').addEventListener('click', () => {
        sendStopSynthesis();
    });
})();
