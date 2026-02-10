---
title: Boot
format: html
---

# Recall

## Where we left off.

- We had add a `.cargo/config.toml` and updated our existing files.
- We were able to build an executable for a bare metal target.
- We have not yet run the executable, and will have to do so using `qemu`.

## `qemu`

- Let's break out `qemu`

```{.sh}
$ qemu-system-x86_64 -kernel target/x86_64-osirs/debug/osirs
Command 'qemu-system-x86_64' not found, but can be installed with:
sudo apt install qemu-system-x86      # version 1:6.2+dfsg-2ubuntu6.27, or
sudo apt install qemu-system-x86-xen  # version 1:6.2+dfsg-2ubuntu6.27
```

- Oh right, we only installed "misc" `qemu`
    - Real ones will use `apt`
    
```{.sh}
sudo apt install qemu-system-x86
```

## Boot it

```{.sh}
$ qemu-system-x86_64 -kernel target/x86_64-osirs/debug/osirs
qemu-system-x86_64: Error loading uncompressed kernel without PVH ELF Note
```

- Oh right, we did precisely *nothing* with the BIOS and the bootloader and all that and still need to do those things.
    - I bet that would be a fun topic for a lab.
    
## Main File

- Unaltered except loops for stability.

```{.rs filename="src/main.rs"}
#![no_std]
#![no_main]

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    loop {}
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
```

## Config File

- All new, only works with nightly.

```{.toml filename=".cargo/config.toml"}
[unstable]
build-std = ["core"]
json-target-spec = true

[build]
target = "x86_64-osirs.json"
```

## Target File

- All new, this is the nightly version.

```{.json filename="x86_64-osirs.json"}
{
    "llvm-target": "x86_64-unknown-none",
    "data-layout": "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128",
    "arch": "x86_64",
    "target-endian": "little",
    "target-pointer-width": 64,
    "target-c-int-width": 32,
    "os": "none",
    "executables": true,
    "linker-flavor": "ld.lld",
    "linker": "rust-lld",
    "panic-strategy": "abort",
    "disable-redzone": true
}
```

## Cargo File

- Move panic specification to target.

```{.toml filename="Cargo.toml"}
[package]
name = "osirs"
version = "0.1.0"
edition = "2024"

[dependencies]
```

# The Lab

## Running our Kernel

- Now that we have an executable that does something perceptible, it is time to run it. 
- First, we need to turn our compiled kernel into a bootable disk image by linking it with a bootloader. 
- Then we can run the disk image in `qemu` virtual machine...
- ...or boot it on real hardware using a USB stick.
    - If you do that, you are responsible for what happens.

## Creating a Bootimage

- To turn our compiled kernel into a bootable disk image, we need to link it with a bootloader. 
- Recall the bootloader is responsible for initializing the CPU and loading our kernel.
    - MU/TH/UR dumping a bucket of electrons atop a CPU.

## Work Smart Not Hard

- We do not write our own bootloader[^1].
- We use the [`bootloader`](https://crates.io/crates/bootloader) crate. 
- This crate implements a basic BIOS bootloader without any C dependencies.
    - Just Rust and 
    - inline assembly (`asm!`, handwaved for the compilers class)
- To use it for booting our kernel, we need to add a dependency on it:

[^1]: This would be cool and fun and we should do it sometime, we just have other things to do!

```{.toml filename="Cargo.toml" code-line-numbers="7"}
[package]
name = "osirs"
version = "0.1.0"
edition = "2024"

[dependencies]
bootloader = "0.9"
```

- **Note:** We use `bootloader v0.9`. 
- Newer versions allegedly use a different build system and will result in build errors.
    - I didn't check.

## Onward!

- Adding the bootloader as a dependency is not enough to actually create a bootable disk image. 
- The problem is that we need to link our kernel with the bootloader after compilation.
- But Cargo has no support for [post-build scripts].(https://github.com/rust-lang/cargo/issues/545)
    - Typical Cargo L.
   
## Install Bootimage

- To solve this problem, use a tool named `bootimage` 
- It first compiles the kernel and bootloader.
- Then it links them together to create a bootable disk image. 
- To install the tool, we will use... cargo:

```{.sh}
cargo install bootimage
```

## Create Bootimage

- Once installed it is a simple matter to use:

```{.sh}
cargo bootimage
```

- This will obviously work on the first try, unless it doesn't.
- In point of fact, I expect you to be able to fix two or three sequential errors you should see after using this command.
    - Stop here and get a bootimage working with no errors.
    - You can consult lecture materials and also review the recommendations of Cargo when it reports an error.
    - If you get stuck here's a spoiler.

<details>

```{.sh}
rustup +nightly component add llvm-tools-preview
cargo +nightly bootimage
```

</details>

## How does it work?

The `bootimage` tool performs the following steps behind the scenes:

- It compiles our kernel to an [ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) file.
- It compiles the bootloader dependency as a standalone executable.
- It links the bytes of the kernel ELF file to the bootloader.
    - Read about the [rust-osdev/bootloader](https://github.com/rust-osdev/bootloader)

## On Boot

- When booted, the bootloader reads and parses the appended ELF file. 
- It then maps the program segments to virtual addresses.
- Zeroes the `.bss` section, and sets up a stack. 
    - [.bss](https://en.wikipedia.org/wiki/.bss) holds static variables.
    - Like `static mut BUS` from the Malloc assignment. 
- It reads the entry point address (`_start`).
- It "jumps" to `_start` and begins executing the code there.

## Booting it in QEMU

- We can now boot the disk image in a virtual machine. 
- To boot it in `qemu`, execute the following command:

```{.sh}
qemu-system-x86_64 -drive format=raw,file=target/x86_64-osirs/debug/bootimage-osirs.bin
```

- Naturally this won't work if you have other names for your files, but hopefully you get the gist.
- This opens a separate window "QEMU" window and currently display nothing.
    - We want to continue to open this graphics window so we have somewhere to look at text when we finally get it to work!

## Real Machine

::: {.callout-caution}

## Don't do this

Don't do this.

:::

- It is also possible to write it to a USB stick and boot it on a real machine, **but be careful** to choose the correct device name, because **everything on that device is overwritten**:

```{.sh}
dd if=target/x86_64-blog_os/debug/bootimage-blog_os.bin of=/dev/sdX && sync
```

- Where `sdX` is the device name of your USB stick. 
- After writing the image to the USB stick, you can run it on real hardware by booting from it. 
- You probably need to use a special boot menu or change the boot order in your BIOS configuration to boot from the USB stick. 
- Note that it currently doesn't work for UEFI machines, since the `bootloader` crate has no UEFI support yet.

## Using `cargo run`

To make it easier to run our kernel in QEMU, we can set the `runner` configuration key for cargo:


```{.toml filename=".cargo/config.toml" code-line-numbers="8-9"}
[unstable]
build-std = ["core"]
json-target-spec = true

[build]
target = "x86_64-osirs.json"

[target.'cfg(target_os = "none")']
runner = "bootimage runner"
```

- `target.'cfg(target_os = "none")'` matches any case where `"os"` is `"none"`. 
    - Like our custom target. 
- The `runner` key specifies the command that should be invoked for `cargo run`. 
- The command is run after a successful build with the executable path passed as the first argument. 

## Runners

- The `bootimage runner` command is specifically designed to be usable as a `runner` executable. 
- It links the given executable with the project's bootloader dependency and then launches QEMU. 
- See the [Readme of `bootimage`](https://github.com/rust-osdev/bootimage) for more details and possible configuration options.
- Now we can use `cargo run` to compile our kernel and boot it in QEMU!

# Fin

```{.sh}
$ cargo +nightly r
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.06s
     Running `bootimage runner target/x86_64-osirs/debug/osirs`
Building bootloader
    Finished `release` profile [optimized + debuginfo] target(s) in 0.06s
Running: `qemu-system-x86_64 -drive format=raw,file=target/x86_64-osirs/debug/bootimage-osirs.bin`
```