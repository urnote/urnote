[中文文档](./docs/index.md)

# Urnote Description

## Profile

Urnote is a tool helping you review your markdown notes.

![example](./docs/res/example.png)

Editor: [Typora](https://typora.io/)

## Quick start

## Installation 

**Windows**

Download [Urnote](https://github.com/urnote/urnote/releases/),  unzip it on your computer, then click the `SET_PATH.bat` in the directory to add it into the computer's environment variable.

**Linux/Unix**

Download [Urnote](https://github.com/urnote/urnote/releases/),  unzip it on your computer, then click the `install.sh` in the directory to add it into the computer's environment variable. 

After the installation:

1. execute `note init`  to create a workspace
2. write your notes, execute  `note status` to  confirm (this step can be skipped), then execute `note commit` 
3. every day when you want to review your notes, please execute `note status`,Urnote will tell you how many notes you need to review, then enter the `TASK` directory, review those notes.Finally,execute `note commit` to commit.

### Create workspace

Workspace is a directory where note stores user data. These data include: users notes, related information of your notes,  program log, user config file.

create a directory to Initialize workspace, then execute `note init`. The directory structure is as follows:

```sh
notes/
|---.NOTE/
|   |---db # review related information
|   |---log # log
|   |---ignore # ignore configuration mentioned below
|---TASK/ # shortcut to your notes which should be reviewed 
```

## Written notes

Now you can create notes under the workspace, for example, we create a `hello-urnote.md`  file, as follows:

```markdown
# What is urnote?
urnote is a tool that helps you review your notes.
```

Now we excute `note status`  to view the status of our workspace, the result is as follows:

![status](./docs/res/after_status.png)

Note identifies the entries need to be added to the review plan through the question mark at the end of the title ,after confirmation execute `note commit` to commit it.

After adding the review plan, you will find the file content of`hello-urnote.md` has changed:

```markdown
# What is urnote [❓] (1)
urnote is a tool to help you review your notes.
```

The only constraint you should know is that you can't use symbols which Urnote treat as control characters at the end of title.

### Review your notes

When entry has been added to the review plan, Urnote will remind you at the right time. Execute `note status` , if there are some entrys in the workspace need to be reviewed today , Urnote will tell you the number of entrys need to be reviewed  and create  shortcut linked to those file in the TASK directory.

Enter the TASK directory ,open a file, you will find ❓ turns into 🔔 which indicates the entry need to be reviewed. Add symbol in the tail to tell  Urnote your review results:

- If you remember, mark `v`
- If you do not remember, mark `x`

Execute `note status`  to view the status of our workspace. Execute `note commit  `after you confirm it.

![complex status](./docs/res/complex_status.png)

### Support

- File format support: UTF-8
- Note format support: Markdown
- OS support: Windows, Linux and Mac

## States and transitions

Note introduces the concept of `question`, see the complete instructions below.

### Question recognition

Urnote uses the Markdown title syntax to recognize `question`, such as:

```markdown
# Question I
answer
# Question II
answer
```

Note will identify the two `question`: "Question I" and "Question II" 

### Question State

In Urnote, there are 4 states: normal, in the review plan, need to be reviewed, paused.

**Normal**

All notes written by users should belong to this category.

**In the review plan**

Title of those questions end with "❓"

**Need to be reviewed**

Title of those questions end with "🔔"

**Paused**

Title of those questions end with "📕", The symbol indicates that the question is temporarily withdrawn from the review plan (no longer remind).

### State transitions

Users are allowed to change the state of note in  3 cases , other state transitions are handled by the program:

1. Add normal note to the review plan, only need to add a `? `at the end of the title
2. After reviewing your notes, add  any character of`XVP` at the end of the title to submit you review result
3. Add a `C` at the end of the title which has been paused to readd the question into review plan (review progress is not lost )

Each state transition require you execute the `note commit` to commit.

### Control character description

| State                 | control characters available | function                     |
| --------------------- | ---------------------------- | ---------------------------- |
| Normal                | ?                            | Add to the review plan       |
| Need to be reviewed🔔 | V                            | You remember it              |
|                       | X                            | You forget it                |
|                       | P                            | You want stop it temporarily |
| Paused📕              | C                            | Readd it                     |

 All the characters above are not case-sensitive, and also support full-width.

## Commands described

All the commands provided by note are described in this chapter.

### -h/--help

Show help message of all commands,such as `note -h`.

Use this after other commands could get more complete message of special command, such as`note status -h`

### status

Displays the status of workspace. 

### init

Create the workspace.

### commit

Commit your change.

### purge

Specify a file or directory, and note will create a copy of all the files in the target file or directory, copy is in the PURGE directory under the root directory , and then Urnote will clear all control information. so all questions will become normal question. 

### --doc

Show online document.

## Configuration

The program will process all files in the workspace by default. If you want to ignore some files, modify the `ignore`  file in `.NOTE`  directory, the file name support wildcard syntax, such as:

```sh
*.py # ignore all python scripts
git/ # ignore git directory
hello.png/# ignore hello.png
```
