---
title: Linker
format: html
---


## Linker Errors

- The linker is a program that combines the generated code into an executable. 
- Since the executable format differs between Linux, Windows, and macOS, each system has its own linker that throws a different error. 
- The fundamental cause of the errors is the same: the default configuration of the linker assumes that our program depends on the C runtime, which it does not.

## Solution

- To solve the errors, we need to tell the linker that it should not include the C runtime. 
- We can do this either by passing a certain set of arguments to the linker or by building for a bare metal target.

### Building for a Bare Metal Target

By default Rust tries to build an executable that is able to run in your current system environment. For example, if you're using Windows on `x86_64`, Rust tries to build an `.exe` Windows executable that uses `x86_64` instructions. This environment is called your "host" system.

To describe different environments, Rust uses a string called [_target triple_]. You can see the target triple for your host system by running `rustc --version --verbose`:

[_target triple_]: https://clang.llvm.org/docs/CrossCompilation.html#target-triple

```
rustc 1.35.0-nightly (474e7a648 2019-04-07)
binary: rustc
commit-hash: 474e7a6486758ea6fc761893b1a49cd9076fb0ab
commit-date: 2019-04-07
host: x86_64-unknown-linux-gnu
release: 1.35.0-nightly
LLVM version: 8.0
```

The above output is from a `x86_64` Linux system. We see that the `host` triple is `x86_64-unknown-linux-gnu`, which includes the CPU architecture (`x86_64`), the vendor (`unknown`), the operating system (`linux`), and the [ABI] (`gnu`).

[ABI]: https://en.wikipedia.org/wiki/Application_binary_interface

By compiling for our host triple, the Rust compiler and the linker assume that there is an underlying operating system such as Linux or Windows that uses the C runtime by default, which causes the linker errors. So, to avoid the linker errors, we can compile for a different environment with no underlying operating system.

An example of such a bare metal environment is the `thumbv7em-none-eabihf` target triple, which describes an [embedded] [ARM] system. The details are not important, all that matters is that the target triple has no underlying operating system, which is indicated by the `none` in the target triple. To be able to compile for this target, we need to add it in rustup:

[embedded]: https://en.wikipedia.org/wiki/Embedded_system
[ARM]: https://en.wikipedia.org/wiki/ARM_architecture

```
rustup target add thumbv7em-none-eabihf
```

This downloads a copy of the standard (and core) library for the system. Now we can build our freestanding executable for this target:

```
cargo build --target thumbv7em-none-eabihf
```

By passing a `--target` argument we [cross compile] our executable for a bare metal target system. Since the target system has no operating system, the linker does not try to link the C runtime and our build succeeds without any linker errors.

[cross compile]: https://en.wikipedia.org/wiki/Cross_compiler

This is the approach that we will use for building our OS kernel. Instead of `thumbv7em-none-eabihf`, we will use a [custom target] that describes a `x86_64` bare metal environment. The details will be explained in the next post.

[custom target]: https://doc.rust-lang.org/rustc/targets/custom.html

### Linker Arguments

Instead of compiling for a bare metal system, it is also possible to resolve the linker errors by passing a certain set of arguments to the linker. This will be the subject of the lab this week.


## Summary

A minimal freestanding Rust binary looks like this:

`src/main.rs`:

```rust
#![no_std] // don't link the Rust standard library
#![no_main] // disable all Rust-level entry points

#[unsafe(no_mangle)] // don't mangle the name of this function
pub extern "C" fn _start() -> ! {
    // this function is the entry point, since the linker looks for a function
    // named `_start` by default
    loop {}
}

/// This function is called on panic.
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
```

`Cargo.toml`:

```toml
[package]
name = "crate_name"
version = "0.1.0"
authors = ["Author Name <author@example.com>"]

# the profile used for `cargo build`
[profile.dev]
panic = "abort" # disable stack unwinding on panic

# the profile used for `cargo build --release`
[profile.release]
panic = "abort" # disable stack unwinding on panic
```

To build this binary, we need to compile for a bare metal target such as `thumbv7em-none-eabihf`:

```
cargo build --target thumbv7em-none-eabihf
```

Alternatively, we can compile it for the host system by passing additional linker arguments:

```bash
# Linux
cargo rustc -- -C link-arg=-nostartfiles
# Windows
cargo rustc -- -C link-args="/ENTRY:_start /SUBSYSTEM:console"
# macOS
cargo rustc -- -C link-args="-e __start -static -nostartfiles"
```

Note that this is just a minimal example of a freestanding Rust binary. This binary expects various things, for example, that a stack is initialized when the `_start` function is called. **So for any real use of such a binary, more steps are required**.

## Making `rust-analyzer` happy

The [`rust-analyzer`](https://rust-analyzer.github.io/) project is a great way to get code completion and "go to definition" support (and many other features) for Rust code in your editor.
It works really well for `#![no_std]` projects too, so I recommend using it for kernel development!

If you're using the [`checkOnSave`](https://rust-analyzer.github.io/book/configuration.html#checkOnSave) feature of `rust-analyzer` (enabled by default), it might report an error for the panic function of our kernel:

```
found duplicate lang item `panic_impl`
```

The reason for this error is that `rust-analyzer` invokes `cargo check --all-targets` by default, which also tries to build the binary in [test](https://doc.rust-lang.org/book/ch11-01-writing-tests.html) and [benchmark](https://doc.rust-lang.org/rustc/tests/index.html#benchmarks) mode.

<div class="note">

### The two meanings of "target"

The `--all-targets` flag is completely unrelated to the `--target` argument.
There are two different meanings of the term "target" in `cargo`:

- The `--target` flag specifies the **[_compilation target_]** that should be passed to the `rustc` compiler. This should be set to the [target triple] of the machine that should run our code.
- The `--all-targets` flag references the **[_package target_]** of Cargo. Cargo packages can be a library and binary at the same time, so you can specify in which way you like to build your crate. In addition, Cargo also has package targets for [examples](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#examples), [tests](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#tests), and [benchmarks](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#benchmarks). These package targets can co-exist, so you can build/check the same crate in e.g. library or test mode.

[_compilation target_]: https://doc.rust-lang.org/rustc/targets/index.html
[target triple]: https://clang.llvm.org/docs/CrossCompilation.html#target-triple
[_package target_]: https://doc.rust-lang.org/cargo/reference/cargo-targets.html

</div>

By default, `cargo check` only builds the _library_ and _binary_ package targets.
However, `rust-analyzer` chooses to check all package targets by default when [`checkOnSave`](https://rust-analyzer.github.io/book/configuration.html#checkOnSave) is enabled.
This is the reason that `rust-analyzer` reports the above `lang item` error that we don't see in `cargo check`.
If we run `cargo check --all-targets`, we see the error too:

```
error[E0152]: found duplicate lang item `panic_impl`
  --> src/main.rs:13:1
   |
13 | / fn panic(_info: &PanicInfo) -> ! {
14 | |     loop {}
15 | | }
   | |_^
   |
   = note: the lang item is first defined in crate `std` (which `test` depends on)
   = note: first definition in `std` loaded from /home/[...]/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/lib/libstd-8df6be531efb3fd0.rlib
   = note: second definition in the local crate (`blog_os`)
```

The first `note` tells us that the panic language item is already defined in the `std` crate, which is a dependency of the `test` crate.
The `test` crate is automatically included when building a crate in [test mode](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#tests).
This does not make sense for our `#![no_std]` kernel as there is no way to support the standard library on bare metal.
So this error is not relevant to our project and we can safely ignore it.

The proper way to avoid this error is to specify in our `Cargo.toml` that our binary does not support building in `test` and `bench` modes.
We can do that by adding a `[[bin]]` section to our `Cargo.toml` to [configure the build](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#configuring-a-target) of our binary:

```toml
# in Cargo.toml

[[bin]]
name = "blog_os"
test = false
bench = false
```

The double-brackets around `bin` are not a mistake, this is how the TOML format defines keys that can appear multiple times.
Since a crate can have multiple binaries, the `[[bin]]` section can appear multiple times in the `Cargo.toml` as well.
This is also the reason for the mandatory `name` field, which needs to match the name of the binary (so that `cargo` knows which settings should be applied to which binary).

By setting the [`test`](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#the-test-field) and [`bench` ](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#the-bench-field) fields to `false`, we instruct `cargo` to not build our binary in test or benchmark mode.
Now `cargo check --all-targets` should not throw any errors anymore, and the `checkOnSave` implementation of `rust-analyzer` should be happy too.

<!--

In this section we discuss the linker errors that occur on Linux, Windows, and macOS, and explain how to solve them by passing additional arguments to the linker. Note that the executable format and the linker differ between operating systems, so that a different set of arguments is required for each system.

#### Linux

On Linux the following linker error occurs (shortened):

```
error: linking with `cc` failed: exit code: 1
  |
  = note: "cc" […]
  = note: /usr/lib/gcc/../x86_64-linux-gnu/Scrt1.o: In function `_start':
          (.text+0x12): undefined reference to `__libc_csu_fini'
          /usr/lib/gcc/../x86_64-linux-gnu/Scrt1.o: In function `_start':
          (.text+0x19): undefined reference to `__libc_csu_init'
          /usr/lib/gcc/../x86_64-linux-gnu/Scrt1.o: In function `_start':
          (.text+0x25): undefined reference to `__libc_start_main'
          collect2: error: ld returned 1 exit status
```

The problem is that the linker includes the startup routine of the C runtime by default, which is also called `_start`. It requires some symbols of the C standard library `libc` that we don't include due to the `no_std` attribute, therefore the linker can't resolve these references. To solve this, we can tell the linker that it should not link the C startup routine by passing the `-nostartfiles` flag.

One way to pass linker attributes via cargo is the `cargo rustc` command. The command behaves exactly like `cargo build`, but allows to pass options to `rustc`, the underlying Rust compiler. `rustc` has the `-C link-arg` flag, which passes an argument to the linker. Combined, our new build command looks like this:

```
cargo rustc -- -C link-arg=-nostartfiles
```

Now our crate builds as a freestanding executable on Linux!

We didn't need to specify the name of our entry point function explicitly since the linker looks for a function with the name `_start` by default.

#### Windows

On Windows, a different linker error occurs (shortened):

```
error: linking with `link.exe` failed: exit code: 1561
  |
  = note: "C:\\Program Files (x86)\\…\\link.exe" […]
  = note: LINK : fatal error LNK1561: entry point must be defined
```

The "entry point must be defined" error means that the linker can't find the entry point. On Windows, the default entry point name [depends on the used subsystem][windows-subsystems]. For the `CONSOLE` subsystem, the linker looks for a function named `mainCRTStartup` and for the `WINDOWS` subsystem, it looks for a function named `WinMainCRTStartup`. To override the default and tell the linker to look for our `_start` function instead, we can pass an `/ENTRY` argument to the linker:

[windows-subsystems]: https://docs.microsoft.com/en-us/cpp/build/reference/entry-entry-point-symbol

```
cargo rustc -- -C link-arg=/ENTRY:_start
```

From the different argument format we clearly see that the Windows linker is a completely different program than the Linux linker.

Now a different linker error occurs:

```
error: linking with `link.exe` failed: exit code: 1221
  |
  = note: "C:\\Program Files (x86)\\…\\link.exe" […]
  = note: LINK : fatal error LNK1221: a subsystem can't be inferred and must be
          defined
```

This error occurs because Windows executables can use different [subsystems][windows-subsystems]. For normal programs, they are inferred depending on the entry point name: If the entry point is named `main`, the `CONSOLE` subsystem is used, and if the entry point is named `WinMain`, the `WINDOWS` subsystem is used. Since our `_start` function has a different name, we need to specify the subsystem explicitly:

```
cargo rustc -- -C link-args="/ENTRY:_start /SUBSYSTEM:console"
```

We use the `CONSOLE` subsystem here, but the `WINDOWS` subsystem would work too. Instead of passing `-C link-arg` multiple times, we use `-C link-args` which takes a space separated list of arguments.

With this command, our executable should build successfully on Windows.

#### macOS

On macOS, the following linker error occurs (shortened):

```
error: linking with `cc` failed: exit code: 1
  |
  = note: "cc" […]
  = note: ld: entry point (_main) undefined. for architecture x86_64
          clang: error: linker command failed with exit code 1 […]
```

This error message tells us that the linker can't find an entry point function with the default name `main` (for some reason, all functions are prefixed with a `_` on macOS). To set the entry point to our `_start` function, we pass the `-e` linker argument:

```
cargo rustc -- -C link-args="-e __start"
```

The `-e` flag specifies the name of the entry point function. Since all functions have an additional `_` prefix on macOS, we need to set the entry point to `__start` instead of `_start`.

Now the following linker error occurs:

```
error: linking with `cc` failed: exit code: 1
  |
  = note: "cc" […]
  = note: ld: dynamic main executables must link with libSystem.dylib
          for architecture x86_64
          clang: error: linker command failed with exit code 1 […]
```

macOS [does not officially support statically linked binaries] and requires programs to link the `libSystem` library by default. To override this and link a static binary, we pass the `-static` flag to the linker:

[does not officially support statically linked binaries]: https://developer.apple.com/library/archive/qa/qa1118/_index.html

```
cargo rustc -- -C link-args="-e __start -static"
```

This still does not suffice, as a third linker error occurs:

```
error: linking with `cc` failed: exit code: 1
  |
  = note: "cc" […]
  = note: ld: library not found for -lcrt0.o
          clang: error: linker command failed with exit code 1 […]
```

This error occurs because programs on macOS link to `crt0` (“C runtime zero”) by default. This is similar to the error we had on Linux and can also be solved by adding the `-nostartfiles` linker argument:

```
cargo rustc -- -C link-args="-e __start -static -nostartfiles"
```

Now our program should build successfully on macOS.

#### Unifying the Build Commands

Right now we have different build commands depending on the host platform, which is not ideal. To avoid this, we can create a file named `.cargo/config.toml` that contains the platform-specific arguments:

```toml
# in .cargo/config.toml

[target.'cfg(target_os = "linux")']
rustflags = ["-C", "link-arg=-nostartfiles"]

[target.'cfg(target_os = "windows")']
rustflags = ["-C", "link-args=/ENTRY:_start /SUBSYSTEM:console"]

[target.'cfg(target_os = "macos")']
rustflags = ["-C", "link-args=-e __start -static -nostartfiles"]
```

The `rustflags` key contains arguments that are automatically added to every invocation of `rustc`. For more information on the `.cargo/config.toml` file, check out the [official documentation](https://doc.rust-lang.org/cargo/reference/config.html).

Now our program should be buildable on all three platforms with a simple `cargo build`.

#### Should You Do This?

While it's possible to build a freestanding executable for Linux, Windows, and macOS, it's probably not a good idea. The reason is that our executable still expects various things, for example that a stack is initialized when the `_start` function is called. Without the C runtime, some of these requirements might not be fulfilled, which might cause our program to fail, e.g. through a segmentation fault.

If you want to create a minimal binary that runs on top of an existing operating system, including `libc` and setting the `#[start]` attribute as described [here](https://doc.rust-lang.org/1.16.0/book/no-stdlib.html) is probably a better idea.

-->