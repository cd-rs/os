---
title: Hello
format: html
---

## Homework

- Homeworks are due on the Friday *after* the week they correspond to lecture.
- So 9 days after the corresponding lab.

## Requirements

- [ ] `371rs/42` crate; I named mine "osirs"
- [ ] Modify `src/main.rs` from the [boot](41_boot.md) lab.
- [ ] Do *not* modify other files.
- [ ] Run on emulated x86-64 in QEMU.

## Printing to Screen

- The easiest way to print text to the screen at this stage is the [VGA text buffer](https://en.wikipedia.org/wiki/VGA-compatible_text_mode). 
    - I regard VGA as an *aspect ratio* like SD (standard definition), 480p, 1080p, 4k, etc.
    - In practice, means "Video Graphics Array"
    - IBM standard for 1987 that is widely adotped.
    - 640 $\times$ 480.
    - "lowest common denominator that virtually all post-1990 PC graphics hardware"
- The *text buffer* is a special memory area.
    - It maps memory locations to screen locations.
    - It normally consists of 25 lines that each contain 80 character cells. 
        - This is why I sometimes require line lengths less than 80 for backwards compatability.
        - This is why legacy assignment ["snek.c"](https://cd-public.github.io/snek/snek.html) assumed a 24-by-80 screen (to allow I/O on the last line).
    - Each character cell displays an ASCII character with some foreground and background colors. 
- The screen output looks like this:

![screen output for common ASCII characters](https://upload.wikimedia.org/wikipedia/commons/f/f8/Codepage-437.png)

- We will discuss the exact layout of the VGA buffer next week.
  - We write a first small driver for it. 
- For printing “Hello World!”, we just need to know:
    - The buffer is located at address `0xb8000`, and 
    - Each character cell consists of an ASCII byte and a color byte.
    
::: {.callout-tip}
## Emphasis "a byte and a byte"

You must write *two bytes per character*.

1. An ASCII value, like 72.
```{.sh}
$ python3 -c "print(ord('H'))"
72
```
2. A color value, for which you can review [Wordle](https://cd-c89.github.io/rs/22_wordle.html) or just use `0xF` or `0xF0`.

Obviously I used `0x0` and then nothing showed up because that was the existing background color.

:::

## Recall

- We recall the solution to the [Transmute lab](21_xmute.md).

```{.rs filename="src/main.rs"}
fn main() {
    unsafe {
        println!("{}", std::mem::transmute::<&[u8], &str>(&std::mem::transmute::<[i32; 3], [u8; 12]>([1819043144, 1870078063, 560229490])));
    }
}
```

- I will urge that you use this `[i32; 3]` as your payload and regard other solutions as "unsporting".
    - We regard the failure of that solution to fit in 80 horizontal characters as a personal moral failing of the course instructor.
    - We will regard specification of those numerical values in hexadecimal as acceptable.
- Here is a bit more information about my source code.

```{.sh}
$ python3 -c "print(ord('H'))"
72
$ wc src/main.rs
 23  88 565 src/main.rs
$ grep ello src/main.rs
$ grep tranmute src/main.rs
$ grep 1819043144 src/main.rs
        let ints: [i32; 3] = [1819043144, 1870078063, 560229490];
```

- There is a solution on the blog (which I will not link) that I find banal and uninteresting, but to be of idiomatic Rust.
    - It is the "blog" solution, which an interested student can find and consult.
- I found this a much better opportunity to practice working with memory.
    - I used no Rust functions or methods.
    - I exclusively used casts and arithmetic on raw pointers.
        - I did not use `transmute` but do not regard its usage as unsporting.
    - I used the same number of unsafe lines (2) as the blog.
        - But in typical fashion, I just enclosed the entire function body in `unsafe` out of pure spite.
        - Do *not* do that in a job interview.
    - I also turned my panic back to recursion because that sounded fun.
        - This required an addition line of code to quell the compiler.
        
## Bonus

- Precompute a `[u32; 6]` with color data and write it in a block.
    - For extra fun, color letters uniquely, perhaps by lexicographical order or consonant/vowel classification.