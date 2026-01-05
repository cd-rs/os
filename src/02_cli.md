---
title: CLI
format: html
---


## Homework

- Homeworks are due on the Friday *after* the week they correspond to lecture.
- So 9 days after the corresponding lab.

## Citation

- [An I/O Project: Building a Command Line Program](https://doc.rust-lang.org/book/ch12-00-an-io-project.html)
- In a way, an OS is a "command line program"...

## Requirements

- [ ] New repository for this course.
- [ ] New crate for this lab.
- [ ] Crate when built creates an executable that behaves identically to GNU Coreutils `wc` when provided with a file name and either (1) no options or a (2) options a single letter.
    - That is, you must support `wc -c src/main.rs` but not `wc --files0-from=F`
    - Check out `wc` and `wc --help` (which *you* don't need to provide) to get a sense of the task.

## Crate

- To complete the lab today, create a crate named `my_wc` in a folder named `02` in your `371os` repository.
```{.bash}
cargo new 02 --name my_wc --vcs none
```
- I understand this is the same name as the lab.
    - I am not as clever as I either think I am or would like to be.
- If you're stuck, read more [here](https://cd-c89.github.io/rs/11_packages.html#option-1-names)

## `wc`

Implement the complete functionality of `wc` using this crate.

- [ ] Accept character command line flags prefixed with `-`
- [ ] Accept string command line flags prefixed with `--`
- [ ] Configure your `my_wc` to work on standard input if a file name is not provided.

### Full functionality

- Here is `wc --help`
- Your `--help` and `--version` may differ, but should otherwise be identical.

```{.sh}
Usage: wc [OPTION]... [FILE]...
  or:  wc [OPTION]... --files0-from=F
Print newline, word, and byte counts for each FILE, and a total line if
more than one FILE is specified.  A word is a non-zero-length sequence of
characters delimited by white space.

With no FILE, or when FILE is -, read standard input.

The options below may be used to select which counts are printed, always in
the following order: newline, word, character, byte, maximum line length.
  -c, --bytes            print the byte counts
  -m, --chars            print the character counts
  -l, --lines            print the newline counts
      --files0-from=F    read input from the files specified by
                           NUL-terminated names in file F;
                           If F is - then read names from standard input
  -L, --max-line-length  print the maximum display width
  -w, --words            print the word counts
      --help     display this help and exit
      --version  output version information and exit

GNU coreutils online help: <https://www.gnu.org/software/coreutils/>
Report any translation bugs to <https://translationproject.org/team/>
Full documentation <https://www.gnu.org/software/coreutils/wc>
or available locally via: info '(coreutils) wc invocation'
```

### Rubric

- Setup - optional

```{.sh}
$ curl https://raw.githubusercontent.com/cd-public/books/main/pg1342.txt -o book.txt
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  739k  100  739k    0     0  1446k      0 --:--:-- --:--:-- --:--:-- 1447k
$ head -23 book.txt | tail -1
*** START OF THE PROJECT GUTENBERG EBOOK PRIDE AND PREJUDICE ***
```

- Character flags - required

```{.sh}
$ wc book.txt
 14911 130408 757509 book.txt
$ wc -cl book.txt
 14911 757509 book.txt
$ wc -c book.txt -cl
 14911 757509 book.txt
$ wc -l book.txt -c
 14911 757509 book.txt
$ wc -Ll book.txt
 14911    159 book.txt
```

- String flags - required

```{.sh}
$ wc --bytes -c book.txt
757509 book.txt
$ wc --lines -c book.txt
 14911 757509 book.txt
$ printf "book.txt" > file.txt
$ wc --lines -c --files0-from=file.txt
 14911 757509 book.txt
$ wc --version | head -1
wc (GNU coreutils) 8.32
$ wc --help | head -1
Usage: wc [OPTION]... [FILE]...
```

- Standard I/O - required

```{.sh}
$ cat book.txt | head -100 | wc
    100     277    2787
$ cat book.txt | head -200 | wc
    200    1360    9359
$ wc book.txt | wc
      1       4      30
```

## Helpful Reference

- While linked above, I think it will be very helpful to review the following:
- [Accepting Command Line Arguments - The Rust Programming Language](https://doc.rust-lang.org/book/ch12-01-accepting-command-line-arguments.html)