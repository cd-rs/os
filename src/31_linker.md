---
title: Linker
format: html
---

# A word before we begin

- This is continued *directly* from the [Bare Metal](30_metal.qmd) lecture.

## The Code

- We left off with the following code:

```{.rs filename="src/main.rs"}
#![no_std]

#[panic_handler]
#[allow(unconditional_recursion)]
fn panic(info: &core::panic::PanicInfo) -> ! {
    panic(info)
}
```

## The Configuration

- We modified the configuration with a few new lines about panics.

```{.toml code-line-numbers="8-12" filename="Cargo.toml"}
[package]
name = "osirs"
version = "0.1.0"
edition = "2024"

[dependencies]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"
```

## The State of Play

- We encountered the following error:

```{.sh}
$ cargo build
   Compiling osirs v0.1.0 (/home/user/tmp/32)
error: using `fn main` requires the standard library
  |
  = help: use `#![no_main]` to bypass the Rust generated entrypoint and declare a platform specific entrypoint yourself, usually with `#[no_mangle]`

error: could not compile `osirs` (bin "osirs") due to 1 previous error
```

# Onward

## The `start` attribute

- One might think that the `main` function is the first function called when you run a program. 
    - Usually because that is how `main` is taught.
    - It isn't entirely wrong - `main` is the first thing *that you write* that is called when you run a program.
    - But there's often some setup first!
- Most languages have a "[runtime system](https://en.wikipedia.org/wiki/Runtime_system)"
    - For e.g. Java garbage collection (e.g. in Java)
    - For e.g. Go software threads (goroutines)
    - For e.g. Python, Pyodide runs in WebAssembly/Emscripten within your browser engine which itself runs on top of an OS.
- This runtime needs to be called before `main`, since it needs to initialize itself.

## C, again

- In a typical Rust executable that links the standard library, execution starts in a C runtime library 
    - `crt0` for “C runtime zero” 
    - C stands for "cool"
- This creates a stack and places the arguments in the right hardware registers.
    - We recall even in our earliest mentions of C and Rust we always *assume* there just happens to be a stack we can push/pop fixed-size variables onto.

## Getting `_start`ed    

- The C runtime then invokes the entry point of the Rust runtime, which is marked by the `start` language item. 
- I detect a great deal of hand-waving around the term "language item".
- I think "language item" is how Rust people describe (some subset of) things that don't make sense with the language implementation.
- Mostly, they are not expressions.
- [Read more](https://doc.rust-lang.org/beta/unstable-book/language-features/lang-items.html)

## Example

Some features provided by lang items:

> overloadable operators via traits: the traits corresponding to the
  `==`, `<`, dereferencing (`*`) and `+` (etc.) operators are all
  marked with lang items; those specific four are `eq`, `partial_ord`,
  `deref`/`deref_mut`, and `add` respectively.
  
We recall Calvin Deutschbein Thought on both overloading and traits (they're bad).
  
## Example

Some features provided by lang items:
  
> panicking: the `panic` and `panic_impl` lang items, among others.

We have already been bamboozled into using #[panic_handler]

## Example

Some features provided by lang items:

> stack unwinding: the lang item `eh_personality` is a function used by the
  failure mechanisms of the compiler.
 
The `eh_personality` item is cut content present in the reference material. We recall Calvin Deutschbein Thought on unwinding (it's bad).
 

## Back to Rust

- Rust only has a very minimal runtime, which takes care of some small things such as setting up stack overflow guards or printing a backtrace on panic. 
    - We should approach the claim of minimal with some skeptism, but it isn't relevant to us for now.
- The runtime then finally calls the `main` function.

## `crt0` is cheating

- Our freestanding executable does not have access to the Rust runtime and `crt0`
- We need to define our own entry point. 
= Implementing the `start` language item wouldn't help, since it would still require `crt0`. 
- Instead, we need to overwrite the `crt0` entry point directly.

## Overwriting

- To tell the Rust compiler that we don't want to use the normal entry point chain, we add the `#![no_main]` attribute.

```{.rs filename="src/main.rs"}
// main.rs

#![no_std]
#![no_main]

/// This function is called on panic.
#[panic_handler]
#[allow(unconditional_recursion)]
fn panic(info: &core::panic::PanicInfo) -> ! {
    panic(info)
}
```

## No main in main

- At this point we can also remove the `main` function. 
    - But notably still term our file `main.rs`
    - We also pretend this is not confusing.
- Absent a compatible runtime, `main` is meaningless!
- If you `cargo build` at this point, by the way, you will get some fun errors.

## Start in main

- Instead, overwrite the entry point with our own `_start` function:

```{.rs filename="src/main.rs"}
fn _start() -> ! {
    // Code
}
```

- This also won't work.

## Manglin'

- By using the `#[unsafe(no_mangle)]` attribute, we disable "name mangling"
    - The function **must** be named `_start`. 
- Otherwise, compiler generates unique symbols like `_start_imarandomstr_1234` to avoid namespace collisons.
    - Folks... it's key-value storage.
- The attribute is required for the *linker* in the next step.

## Start in main

- Write your own mangle-free `_start`.:

```{.rs filename="src/main.rs"}
#[unsafe(no_mangle)]
fn _start() -> ! {
    // Code
}
```

## C you again

- Mark the function as `extern "C"` to tell the compiler that it should use the "C calling convention"
- The reason for naming the function `_start` is that this is the default entry point name for most systems.

## A Hardware Reality

- The C calling convention is a *hardware* reality 
- It is the implementation of a physical device that assumes C code is running on it, 
- It assumes the C runs in an expected, consistent, historical way.
- This consistency leads to a usable heap and viable `return`.
- *It could be possible to e.g. implement stack-less C*
    - But that would *not* have hardware support.

## Start in main

- Instead, overwrite the entry point with our own `_start` function:

```{.rs filename="src/main.rs"}
#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    // Code
}
```

## C you later

- We don't have a great way to test this at this stage.
    - In fact, most formulations will lead to similar errors...
    - We just put it in now for forwards compatability.
- That said, I got this working without `pub extern "C"`
    - You can try it out soon.

## Read more

- [name mangling](https://en.wikipedia.org/wiki/Name_mangling)
- [C calling convention](https://en.wikipedia.org/wiki/Calling_convention)

## Divergence

- The `!` return type returns!
- This is required because the entry point is not called by any function, but invoked directly by the operating system or bootloader. 
    - It can't return anywhere!
- Cowards use `loop()`, heroes use recursion.

```{.rs filename="src/main.rs"}
#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    _start()
}
```

## Allowance

- As you are aware, `cargo` is counted among the cowards that expect loop.
    - We still haven't shown the trick to compile this yet, but if you knew the trick you would see the following.

```{.sh}
   Compiling osirs v0.1.0 (/home/user/tmp/32)
warning: function cannot return without recursing
 --> src/main.rs:5:1
  |
5 | pub extern "C" fn _start() -> ! {
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ cannot return without recursing
6 |     _start()
  |     -------- recursive call site
  |
  = help: a `loop` may express intention better if this is on purpose
  = note: `#[warn(unconditional_recursion)]` on by default

warning: `osirs` (bin "osirs") generated 1 warning
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.16s
```

## Hash and Hash Bang

- We applied function-level allowances to our `panic` to allow infinite recursion as follows:
    - Immediately prepending, octothorpe/hash prefixed "language items"

```{.rs filename="src/main.rs"}
#[panic_handler]
#[allow(unconditional_recursion)]
fn panic(info: &core::panic::PanicInfo) -> ! {
    panic(info)
}
```

- We applied file-level allowances to our `src/main.rs` as follows:
    - Free-floating, octothorpe+exclamation point (hash+bang)
    
```{.rs filename="src/main.rs"}
#![no_std]
#![no_main]
```

## The Code

- I promoted the recursion allowance to file-level, with the following resultant code:
    
```{.rs filename="src/main.rs"}
#![no_std]
#![no_main]
#![allow(unconditional_recursion)]

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! { _start() }

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! { panic(info) }
```

- Put [a pin](#re-cursed) in this. 
    - We'll be back latter.
    
## Exit

- Before I go out to the clubs I always "X it up" (put X's on my hands) because I'm straight edge.
- Operating systems are similar.
- So instead of returning, the entry point should e.g. invoke the `exit` system call of the operating system.
- [`exit` system call](https://en.wikipedia.org/wiki/Exit_(system_call))
- For now, we fulfill the requirement by recursing endlessly.

## Now it works!

- It doesn't.
```{.sh}
$ cargo build
   Compiling osirs v0.1.0 (/home/user/tmp/32)
error: linking with `cc` failed: exit status: 1
  |
  = note:  "cc" "-m64" "/tmp/rustcheyGtM/symbols.o" "<1 object files omitted>" "-Wl,--as-needed" "-Wl,-Bstatic" "<sysroot>/lib/rustlib/x86_64-unknown-linux-gnu/lib/{librustc_std_workspace_core-*,libcore-*,libcompiler_builtins-*}.rlib" "-L" "/tmp/rustcheyGtM/raw-dylibs" "-Wl,-Bdynamic" "-Wl,--eh-frame-hdr" "-Wl,-z,noexecstack" "-L" "<sysroot>/lib/rustlib/x86_64-unknown-linux-gnu/lib" "-o" "/home/user/tmp/32/target/debug/deps/osirs-80f8eb3240ba748e" "-Wl,--gc-sections" "-pie" "-Wl,-z,relro,-z,now" "-nodefaultlibs"
  = note: some arguments are omitted. use `--verbose` to show all linker arguments
  = note: /usr/bin/ld: /home/user/tmp/32/target/debug/deps/osirs-80f8eb3240ba748e.9chdw59nqscmfe0ef1hrxy2nb.rcgu.o: in function `_start':
          /home/user/tmp/32/src/main.rs:14: multiple definition of `_start'; /usr/lib/gcc/x86_64-linux-gnu/11/../../../x86_64-linux-gnu/Scrt1.o:(.text+0x0): first defined here
          /usr/bin/ld: /usr/lib/gcc/x86_64-linux-gnu/11/../../../x86_64-linux-gnu/Scrt1.o: in function `_start':
          (.text+0x1b): undefined reference to `main'
          /usr/bin/ld: (.text+0x21): undefined reference to `__libc_start_main'
          collect2: error: ld returned 1 exit status

  = note: some `extern` functions couldn't be found; some native libraries may need to be installed or have their path specified
  = note: use the `-l` flag to specify native libraries to link
  = note: use the `cargo:rustc-link-lib` directive to specify the native libraries to link with Cargo (see https://doc.rust-lang.org/cargo/reference/build-scripts.html#rustc-link-lib)

error: could not compile `osirs` (bin "osirs") due to 1 previous error
```

## Linker Errors

- The linker is a program that combines the generated code into an executable.
    - Could be the subject of an entire course.
    - Extremely compiler-relevant.
- Since the executable format differs between Linux, Windows, and macOS, each system has its own linker that throws a different error. 
- The fundamental cause of the errors is the same: the default configuration of the linker assumes that our program depends on the C runtime, which it does not.

## Solution

- To solve the errors, we need to tell the linker that it should not include the C runtime. 
- We can do this either by passing a certain set of arguments to the linker or by building for a bare metal target.

## Building for a Bare Metal Target

- By default Rust tries to build an executable that is able to run in your current system environment. 
- For example, if you're using Linux on `x86_64`, Rust tries to build an ELF that uses `x86_64` instructions. 
- This environment is called your "host" system.

## Target Triple

- To describe different environments, Rust uses a string called [_target triple_](https://clang.llvm.org/docs/CrossCompilation.html#target-triple). 
- You can see the target triple for your host system by running `rustc --version --verbose`:

```{.sh}
$ rustc --version --verbose
rustc 1.87.0 (17067e9ac 2025-05-09)
binary: rustc
commit-hash: 17067e9ac6d7ecb70e50f92c1944e545188d2359
commit-date: 2025-05-09
host: x86_64-unknown-linux-gnu
release: 1.87.0
LLVM version: 20.1.1
```

## Comments

- The above output is from a `x86_64` Linux system. 
- We see that the `host` triple is `x86_64-unknown-linux-gnu`
    - CPU architecture (`x86_64`), 
    - Vendor (`unknown`) - It's Intel #Portland
    - Operating system (`linux`)
    - The [ABI](https://en.wikipedia.org/wiki/Application_binary_interface) (`gnu`).

## On Triples

- For triple, `rustc` and the linker (for me `gcc`, often `clang` is recommended). assume an OS and C runtime. 
- We turned both of those things off.
- So, to avoid the linker errors, we can compile for a different environment with no underlying operating system.

## Bare Metal

- One bare metal environment is the `thumbv7em-none-eabi` target triple
- A embedded ARM system. Used for teaching.
- The details are not important; it has no underlying operating system.
    - That is the `none` in the target triple. 
    
## Rustup
    
- To be able to compile for this target, we need to add it in rustup:

```{.sh}
rustup target add thumbv7em-none-eabihf
```

This downloads a copy of the standard (and core) library for the system. Now we can build our freestanding executable for this target:

```{.sh}
cargo build --target thumbv7em-none-eabihf
```

## Explanation

- By passing a `--target` argument we [cross-compile](30_metal.qmd#cross-compiling)
    - Bare metal compilation! 
- Since the target system has no operating system, the linker does not try to link the C runtime and our build succeeds without any linker errors.

## Looking Ahead

- This is the approach that we will use for building our OS kernel. 
- Instead of `thumbv7em-none-eabihf`, we will use a custom target that describes a `x86_64` bare metal environment. 
    - I don't know how this will work for the Apple Silicon folks.
    - But I am excited to find out!
- The details will be explained next week.

## Summary

A minimal freestanding Rust executable looks like this:

- Code

```{.rs filename="src/main.rs"}
#![no_std]
#![no_main]
#![allow(unconditional_recursion)]

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    _start()
}

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    panic(info)
}
```

- Configuration
    - We made no changes to this during the lab.

```{.toml code-line-numbers="8-12" filename="Cargo.toml"}
[package]
name = "osirs"
version = "0.1.0"
edition = "2024"

[dependencies]

[profile.dev]
panic = "abort"

[profile.release]
panic = "abort"
```

## To build

To build this binary, we need to compile for a bare metal target such as `thumbv7em-none-eabi`:

```{.sh}
cargo build --target thumbv7em-none-eabi
```

Alternatively, we can compile it for Linux by passing additional linker arguments to `rustc`:

```{.sh}
cargo rustc -- -C link-arg=-nostartfiles
```

## To run

- If you build, you can run it!

```{.sh}
$ cargo rustc -- -C link-arg=-nostartfiles
   Compiling osirs v0.1.0 (/home/user/tmp/32)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.14s
user@cd-desk:~/tmp/32$ ./target/debug/osirs
Segmentation fault (core dumped)
```

- Wait a minute!

## RE: cursed

- The C calling convention segfaults on infinite recursion.
- Switch to `loop` to get an infinite loop.
- These two things are equally bad in my view.

```{.rs}
#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    loop {}
}
```

- Pop [the pin](#the-code-1)

# Fin