[中文文档](./docs/index.md)

# SmartNote Description

## Profile

Smartnote is a tool  helping you review your notes.

If your notes are saved in a file on your computer, and the note's format can be resolved, then you only need to add some simple marks,smartnote will remind you to review them at the right time.

![example](./docs/res/example.png)

Editor: [Typora](https://typora.io/)

## Quick start

## Installation 

Download [SmartNote.zip](https://github.com/jefffffrey/smart-note/releases/download/v0.1.0/SmartNote-0.1.0.zip),  unzip it on your computer, then click the SET_PATH.bat in the directory to add it into the environment variable 

After the Installation:

1. execute `note init`  to create a workspace
2. write your notes, execute  `note status` to  confirm (this step can be skipped), then execute `note commit` 
3. every day when you want to review your notes, please execute `note status`,smartnote will tell you how many notes you need to review, then enter the `TASK` directory, review those notes.Finally,execute `note commit` to commit.

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

Now you can create notes under the workspace, for example, we create a `hello-smart-note.md`  file, as follows:

```markdown
# What is smart note?
smart note is a tool that helps you review your notes.
```

Now we excute `note status`  to view the status of our workspace, the result is as follows:

![status](./docs/res/after_status.png)

Note identifies the entries need to be added to the review plan through the question mark at the end of the title ,after confirmation execute `note commit` to commit it.

After adding the review plan, you will find the file content of`hello-smart-note.md` has changed:

```markdown
# What is smart note [❓] (SOH0000001EOT)
smart note is a tool to help you review your notes.
```

When the  [❓] (SOH0000001EOT) string appear, don't worry. If you use markdown Editor to open the file, you will find this part will be rendered as a single ❓.

The only constraint you should know is that you can't use symbols which smartnote treat as control characters at the end of title.

### Review your notes

When entry has been added to the review plan, smartnote will remind you at the right time. Execute `note status` , if there are some entrys in the workspace need to be reviewed today , smartnote will tell you the number of entrys need to be reviewed  and create  shortcut linked to those file in the TASK directory.

Enter the TASK directory ,open a file, you will find ❓ turns into 🔔 which indicates the entry need to be reviewed. Add symbol in the tail to tell  smartnote your review results:

- If you remember, mark `v`
- If you do not remember, mark `x`

Execute `note status`  to view the status of our workspace. Execute `note commit  `after you confirm it.

![complex status](./docs/res/complex_status.png)

### Support

- File format support: program open file in UTF-8 by default , so please use a format that is compatible with UTF-8, such as: ASCII
- Note format support: only supports Markdown now
- Operating systems support: currently only supports Windows operating system

## States and transitions

Note introduces the concept of chapter and state, see the complete instructions below.

### Chapter recognition

Smartnote uses the Markdown title syntax to recognize chapter, such as:

```markdown
# chapter I
The first chapter
# chapter II
The second chapter
```

Note will identify the two chapters "chapter I" and "chapter II" 

### Chapter State

In smartnote, there are 4 states: normal, in the review plan, need to be reviewed, paused.

**Normal**

All notes written by users should belong to this category.

**In the review plan**

Title of those chapters end with "❓"

**Need to be reviewed**

Title of those chapters end with "🔔"

**Paused**

Title of those chapters end with "📕", The symbol indicates that the chapter is temporarily withdrawn from the review plan (no longer remind).

### State transitions

Users are allowed to change the state of note in  3 cases , other state transitions are handled by the program:

1. Add normal note to the review plan, only need to add a `? `at the end of the title
2. After reviewing your notes, add  any character of`XVP` at the end of the title to submit you review result
3. Add a `C` at the end of the title of the charpter which has been paused to readd the chapter into review plan (review progress is not lost )

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

Specify a file or directory, and note will create a copy of all the files in the target file or directory, copy is in the PURGE directory under the root directory , and then smartnote will clear all control information. so all chapters will become normal chapter. 

### --doc

Show RST version of this document

## Configuration

The program will process all files in the workspace by default. If you want to ignore some files, modify the `ignore`  file in `.NOTE`  directory, the file name support wildcard syntax, such as:

```sh
*.py # ignore all python scripts
git/ # ignore git directory
hello.png/# ignore hello.png
```
