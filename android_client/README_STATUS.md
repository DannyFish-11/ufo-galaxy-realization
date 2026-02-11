# Android 客户端说明

## ⚠️  重要提示

**此目录包含的是旧版/示例 Android 客户端代码，仅供参考。**

## 当前状态

- 📦 **状态**: 旧版/镜像/示例代码
- 🔗 **主仓库**: [DannyFish-11/ufo-galaxy-android](https://github.com/DannyFish-11/ufo-galaxy-android)
- 📅 **最后更新**: 2026-02-06

## Android 开发指引

### 推荐使用独立仓库

Android 客户端已迁移到独立仓库，获得以下优势：

1. **独立的发布周期** - Android 应用可独立于服务端进行版本发布
2. **更好的协作** - 移动端和服务端团队可独立工作
3. **简化的 CI/CD** - 独立的构建和测试流程
4. **更清晰的依赖管理** - Android 和服务端依赖分离

### 获取最新 Android 客户端

```bash
# 克隆 Android 独立仓库
git clone https://github.com/DannyFish-11/ufo-galaxy-android.git
cd ufo-galaxy-android

# 使用 Android Studio 打开项目
# 或使用命令行构建
./gradlew assembleDebug
```

### 下载 APK

从独立仓库的 Releases 页面下载最新版本：

[https://github.com/DannyFish-11/ufo-galaxy-android/releases](https://github.com/DannyFish-11/ufo-galaxy-android/releases)

## 本目录的用途

本目录保留的代码可用于：

- 📚 参考旧版实现
- 🔍 历史代码查询
- 📝 示例代码学习

**不建议**用于生产环境或新功能开发。

## 迁移说明

如果您正在使用此目录的代码，建议迁移到独立仓库：

1. 备份您的本地修改
2. 克隆独立仓库 `ufo-galaxy-android`
3. 将您的修改应用到新仓库
4. 提交 Pull Request 到独立仓库

## 联系方式

- GitHub Issues: [ufo-galaxy-android/issues](https://github.com/DannyFish-11/ufo-galaxy-android/issues)
- 服务端 Issues: [ufo-galaxy-realization/issues](https://github.com/DannyFish-11/ufo-galaxy-realization/issues)

---

**最后更新**: 2026-02-11  
**维护者**: DannyFish-11
