---
title: Format 
format: html
---

# Recall

- We wrote `str_to_vga`.
- We handled a bunch of corner cases.
- We had an all-around great time.

## Today

- We recall our two main source code files.
    - We anticipate our configuration files to be unaltered.

### Main

```{.rs filename="src/main.rs"}
#![no_std]
#![no_main]

mod vga;

#[panic_handler]
#[allow(unconditional_recursion)]
fn panic(info: &core::panic::PanicInfo) -> ! {
    panic(info)
}

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    vga::str_to_vga("Hello, world!");
    loop {}
}
```

### VGA

```{.rs filename="src/vga.rs"}
static mut LATEST: usize = 0;
const MMIO: *mut u8 = 0xb8000 as *mut u8;
const COLOR: u8 = 0xF;

fn char_to_vga(a: u8) {
    unsafe {
        let rel: *mut u8 = ((MMIO as usize) + (LATEST * 2)) as *mut u8;
        *rel = a;
        *((rel as usize + 1) as *mut u8) = COLOR;
        LATEST = LATEST + 1;
    }
}

const ROWS: usize = 80;
const COLS: usize = 25;
const MAX: usize = ROWS * COLS;

fn scroll() {
    unsafe {
        for i in 80..MAX {
            let src: *mut u8 = ((MMIO as usize) + (i * 2)) as *mut u8;
            let dst: *mut u8 = ((MMIO as usize) + ((i - 80) * 2)) as *mut u8;
            *dst = *src;
            *((dst as usize + 1) as *mut u8) = COLOR;
        }
        for i in (MAX-80)..MAX {
            let dst: *mut u8 = ((MMIO as usize) + ((i) * 2)) as *mut u8;
            *dst = 32;
            *((dst as usize + 1) as *mut u8) = COLOR;
        }
        LATEST = LATEST - 80;
    }
}

pub fn str_to_vga(s: &str) {
    let v = s.as_bytes();
    unsafe {
        for i in 0..v.len() {
            if LATEST > MAX {
                scroll();
            }
            match v[i] {
                10 => LATEST = ((LATEST / 80) + 1) * 80,
                _ => char_to_vga(v[i]),
            }
        }
    }
}
```

# Format

## Formatting Macros

- It would be nice to support Rust's formatting macros, too. 
- We will also discover that Rust is, in point of fact, an object-oriented language.
  	- Read: bad.
- I was extremely annoyed by how to get this working, but I did it.

## Functionality

- We need to implement the [`core::fmt::Write`] trait. 
	- I had foolishly assumed we could just use `format!`
	- That would tragically be too reasonable.
	- (It also would raise some unanswered questions about memory but whatever).
- The only required method of this trait is `write_str`:
  - [`core::fmt::Write`](https://doc.rust-lang.org/nightly/core/fmt/trait.Write.html)

## Sketch

- Basically we need to write this:

```{.rs filename="src/vga.rs"}
impl core::fmt::Write for ??? {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        // Do the thing. 
        return Ok(());
    }
}
```

- The `Ok(())` is just a `Ok` Result containing the `()` "unit type".

## Workaround

- I already can write text!

```{.rs filename="src/vga.rs"}
impl core::fmt::Write for ??? {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        str_to_vga(s); 
        return Ok(());
    }
}
```

## Dummy struct

- I just make an arbitrary structure.

```{.rs filename="src/vga.rs"}
struct Dummy { } 

impl core::fmt::Write for Dummy {
    fn write_str(&mut self, s: &str) -> fmt::Result {
        str_to_vga(s); 
        return Ok(());
    }
}
```

- Presumably it is clear why someone would find this an annoying way to do things.

## This works

- I'm not kidding it actually does.
- I was surprised too.
	- I did forget to capitalized the W in write but...

```{.rs filename="src/main.rs"}
#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    use core::fmt::Write;
    let mut d = vga::Dummy { };
    write!(d, "Hello {}!", "world");
    loop {}
}
```

- It throws an uninteresting warning.
    - Make sure you know how to fix and why it happens.

## A println Macro

- We can add a `println` macro.
- Rust's [macro syntax](https://doc.rust-lang.org/nightly/book/ch20-05-macros.html#declarative-macros-for-general-metaprogramming) is a bit strange.
- So we won't try to write a macro from scratch. 
- Instead, we look at the source of `println!` in the standard library:

```{.rs filename="std/macros.rs"}
#[macro_export]
macro_rules! println {
    () => (print!("\n"));
    ($($arg:tt)*) => (print!("{}\n", format_args!($($arg)*)));
}
```

## Rules

- Macros are defined through one or more rules, similar to `match` arms. 
- The `println` macro has two rules: 
    - The first rule is for invocations without arguments, e.g., `println!()`, which is expanded to `print!("\n")` and thus just prints a newline. 
    - The second rule is for invocations with parameters such as `println!("Hello")` or `println!("Number: {}", 4)`. 
        - It is also expanded to an invocation of the `print!` macro.
        - It passes all arguments and an additional newline `\n` at the end.
- The `#[macro_export]` attribute makes the macro available to the whole crate. 
- It also places the macro at the crate root.
    - Import the macro through `use std::println` instead of `std::macros::println`.

## print

```{.rs filename="std/macros.rs"}
#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => ($crate::io::_print(format_args!($($arg)*)));
}
```

- The macro expands to a call of the `_print` function in the `io` module. 
- The `$crate` variable ensures that the macro also works from outside the `std` crate by expanding to `std` when it's used in other crates.
- The `format_args` macro builds a `fmt::Arguments` type from the passed arguments, which is passed to `_print`. 
- The `_print` function calls `print_to`, which is rather complicated because it supports different `Stdout` devices. 
    - We don't need that complexity since we just want to print to the VGA buffer.

- [`_print` function](https://github.com/rust-lang/rust/blob/29f5c699b11a6a148f097f82eaa05202f8799bbc/src/libstd/io/stdio.rs#L698)
- [`$crate` variable](https://doc.rust-lang.org/1.30.0/book/first-edition/macros.html#the-variable-crate)
- [`format_args` macro](https://doc.rust-lang.org/nightly/std/macro.format_args.html)
- [`fmt::Arguments`](https://doc.rust-lang.org/nightly/core/fmt/struct.Arguments.html)

- To print to the VGA buffer, we just copy the `println!` and `print!` macros, but modify them to use our own `_print` function:

```{.rs filename="src/vga.rs"}
#[macro_export]
macro_rules! print {
    ($($arg:tt)*) => ($crate::vga::_print(format_args!($($arg)*)));
}

#[macro_export]
macro_rules! println {
    () => ($crate::print!("\n"));
    ($($arg:tt)*) => ($crate::print!("{}\n", format_args!($($arg)*)));
}

pub fn _print(args: fmt::Arguments) {

}
```

- Here's mine:

<details>

```{.rs}
pub fn _print(args: core::fmt::Arguments) {
    use core::fmt::Write;
    let mut d = Dummy { };
    d.write_fmt(args).unwrap();
}
```

</details>

## Hello World using `println`

Now we can use `println` in our `_start` function:

```{.rs filename="src/main.rs"}

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    println!("Hello World{}", "!");
    loop {}
}
```

- We don't have to import the macro in the main function, because it already lives in the root namespace.

## Printing Panic Messages

- Now that we have a `println` macro, we can use it in our panic function to print the panic message and the location of the panic:
- Using your boundless intellect and and unbreakable work ethic, implement a panic handler that prints out some relevant information.
- It is easy enough to test.

```{.rs}
panic!("It is I, a panic!");
```
