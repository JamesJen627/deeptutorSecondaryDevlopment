# 迁移到 D 盘说明

## 新路径

| 内容 | 新路径 |
|------|--------|
| Fork 源码 | `D:\Dev\deeptutorSecondaryDevlopment` |
| 运行工作区 | `D:\Dev\DeepTutor` |

## 迁移后必做

1. **在 Cursor 中打开新工作区**：`D:\Dev\deeptutorSecondaryDevlopment`
2. **重装 editable 包**（指向 D 盘源码）：
   ```powershell
   cd D:\Dev\deeptutorSecondaryDevlopment
   D:\python3.12\python.exe -m pip install -e .
   ```
3. **从新工作区启动**：
   ```powershell
   cd D:\Dev\DeepTutor
   D:\python3.12\Scripts\deeptutor.exe start
   ```

## 清理 C 盘旧目录（可选）

关闭所有占用旧路径的 Cursor 窗口/终端后：

```powershell
Remove-Item -Recurse -Force "C:\Users\36739\deeptutorSecondaryDevlopment" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "C:\Users\36739\DeepTutor" -ErrorAction SilentlyContinue
```

若提示「文件正在使用」，先完全退出 Cursor 再删。

## 数据说明

`D:\Dev\DeepTutor\data\user\` 已包含原 C 盘工作区的完整拷贝（含 `chat_history.db`、知识库、events 等）。
