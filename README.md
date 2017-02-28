# Smart Note

## 简介

smart note 是一个帮助你复习笔记的工具.

如果你是记录的笔记以文件的形式保存在电脑上,并且所使用的笔记格式是可以解析的,那么只需要在记录笔记的时候加入一些简单的标记,就可以让smart note在恰当的时候提醒你复习. 

## 快速开始

### 安装smart note

下载打包好的[smart note](https://github.com/jefffffrey/smart-note/releases/download/v0.1.0/SmartNote-0.1.0.zip),将其解压到电脑上,之后执行文件夹中的SET_PATH.bat将该目录加入到环境变量(之后就可以在系统任何地方执行note命令).

安装好note之后即可:

1. `note init` 创建工作空间
2. 写笔记,执行`note state`确认添加的笔记(该步骤可以跳过),之后执行`note commit`
3. 每天需要复习笔记的时候,执行`note state` ,然后进入TASK目录复习,复习完毕之后执行`note commit`

### 创建工作空间

工作空间即note用来存放用户数据的地方,这些数据包括:用户记录的笔记,和复习笔记相关的数据,程序日志,用户配置文件.

初始化工作空间的方式为创建一个目录,之后在目录中执行`note init` 命令,初始的工作空间的目录结构如下:

```sh
notes/
|---.NOTE/
|   |---db # 复习相关的信息
|   |---log # 日志
|   |---ignore # ignore配置,下文会讲到
|---TASK/ # 需要复习的笔记的快捷方式   
```

### 写笔记

此时就可以在notes目录下面创建笔记,比如我们创建了一个hello-smart-note.md文件,内容如下:

```markdown
# What is smart note ?
smart note 是一个帮助你复习笔记的工具.
```

现在我们执行`note status`命令查看一下工作空间的状态,结果如下:

![](docs/res/after status.png) 

note 识别出了文件中需要复习的条目,但是并未修改文件内容,也没有将其加入复习计划.此时需要执行`note commit`使note将该条目加入复习计划.

加入复习计划后,会发现hello-smart-note.md文件内容发生了变化:

```markdown
# What is smart note    [❓](SOH0000001EOT)  
smart note 是一个帮助你复习笔记的工具.
```

文档中出现了`[❓](SOH0000001EOT)` 这个的字符串,不要担心.如果你用markdown编辑器打开,会发现该部分会被渲染成[❓]().

### 复习笔记

此时该条目已经加入了复习计划,因此note会在恰当的时间提醒你复习.

假设note安排该条目在3天后复习,那么3天后执行`note status`将得到'1个问题需要复习'的提示,并且该文件的快捷方式将放在工作空间根目录下的`TASK` 目录中.进入TASK目录打开文件,会发现之前的[❓]()变成了[🔔](),该符号用来提示条目需要复习.

此时如果你还记得该问题,则在[❓]()后面标注V,如果你不记得该问题,则标注X.之后执行`note commit`即可.note将继续安排下次复习时间,并且在恰当的时间给你提示.

## 约束

- 文件格式支持:程序默认以UTF-8格式打开文件，因此请使用与UTF-8兼容的格式编写笔记,如:ASCII
- 笔记格式支持:目前仅支持markdown格式
- 操作系统支持:目前仅支持Windows操作系统

## 更多资料

本文只介绍了note的基础用法,更多note的命令以及控制方式参考[详细文档](docs/使用说明.md)

## 参与

如果你对smart note感兴趣,并且想要smart note变得更好,你可以:

- 在Issue页面提交你遇到的问题,你想要的功能,你觉得不满意的地方...
- Fork项目参与开发,参考[开发文档](docs/开发文档.md)

