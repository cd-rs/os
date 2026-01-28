---
title: malloc
format: html
---

## Homework

- Homeworks are due on the Friday *after* the week they correspond to lecture.
- So 9 days after the corresponding lab.

## Citation

- [An I/O Project: Building a Command Line Program](https://doc.rust-lang.org/book/ch12-00-an-io-project.html)
- In a way, an OS is a "command line program"...

## Requirements

- [ ] `371rs/22` crate; I named mine "malloc"
- [ ] You write `src/lib.rs` that implements functions in the `src/main.rs` I provide.

# main

## Code

```{.rs filename="src/main.rs"}
use malloc::*; // crate name

fn main() {
    let p0 = malloc(16).unwrap();
    let p1 = malloc(32).unwrap();
    let x = 0x44332211;
    let y = 0x12345678;
    setter(x, p0);
    setter(y, p1);
    let z: i32 = getter(p0);
    let w: i32 = getter(p1);
    assert!(x == z);
    assert!(y == w);
    println!("A+");
    // Advanced topics.

    // Big alloc should fail

    assert!(malloc(2048).is_none());
    println!("A++");

    // Allocs totaling > SIZE should fail

    // We have alloc (16 + 32) * 8 = 384 of 1024
    // Try annother small malloc
    malloc(32).unwrap();
    // And then one too large.
    assert!(malloc(64).is_none());
    println!("A+++");

    // Easiest to test these together:
    //  - Gets to uninitialized memory should fail
    //  - You should write free()
    // No graceful way to autotest these. Left as an exercise to the interested student.
}
```

## Explanation

- This is based on the C language `malloc` function.
    - Probably the most important function.
    - [My slides on C](https://cd-public.github.io/crypto/qmd/malloc.html#/today)

### Malloc

- We begin with calls to our own `malloc`:
```{.rs filename="src/main.rs"}
    let p0 = malloc(16).unwrap();
    let p1 = malloc(32).unwrap();
```
- `malloc` takes one argument, a `usize`, the number of bytes to allocate.
    - It returns a `Option<usize>`, the "offset" of those bytes from general reference point.
    - We can regard this as the address.
    - We can ask `malloc` for more memory then is available, and then we get `None`.
- Here is my `malloc`, with code removed.
```{.rs filename="src/lib.rs"}
// Return an index in BUS of s reserved bytes
pub fn malloc(s: usize) -> Option<usize> {
    unsafe {
        // Ensure BUS is initialized.
        < 3 lines snipped > 

        // Reserve a block of s bytes
        < 4 lines snipped > 

        // Scan for a contigious region of size s
        // In s > 8, word level allocation
        // "Could be more efficient" it's an exercise!
        < ~20 lines snipped> 
    }
    return None;
}
```
- Some interest things here:
    - This relies on a new Rust "thing", a `static mut`.
        - They may hold the record for being the most unsafe.
        - Think of it maybe as a Python global.
        - I named mine `BUS`.
    - This relies on a helper function to initialize `BUS`
        - I am requiring the following implementation for your `BUS`:
        - For me, declared at the beginning of `lib`

### Static mut

```{.rs filename="src/lib.rs"}
// Treat ourselves to a kb (1024 bits)
// 1024 >> 3 == 128 == 0x80
pub const SIZE: usize = 0x80;

// Not really a BUS but we gotta call it something.
static mut BUS: [u8; SIZE] = [0u8; SIZE];
```
- The requirements are:
    - A `static mut` of a fixed size `u8` array.
    - Must support any size which is a power of 2.
    - May not use any other `static mut`
        - An astute observer will note that then any tracking information related to `BUS` *must be stored within BUS itself*
        - This is non-trivial
- I am not aware of high quality reference materials on `static mut`, here is an example use apparently.

```{.rs}
static mut COUNTER: u32 = 0;

fn add_to_counter(inc: u32) {
    // SAFETY: There are no other threads which could be accessing `COUNTER`.
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    add_to_counter(42);

    // SAFETY: There are no other threads which could be accessing `COUNTER`.
    unsafe {
        dbg!(COUNTER);
    }
}
```
- This fixed-size array of bits is meant to be consistent with underlying hardware, at least theoretically.

### Initialization

- You are not required to use a helper for this, but I did.
- I am permitting/encouraging an `assert!` that enforced power-of-two sizing.
- Naively using `BUS` didn't work well for me.
    - I had to check to make sure I wasn't giving away bits already in use.
    - So I had to *persist* some *state*
        - I had to use memory to provide memory.
    - I just reserved some bits at the beginning of the array as a *validity bitmask*
        - If a bit is set to 1, the corresponding byte is in use.
        - So a 1-in-8 overhead cost.
        - This is why 64 bit words are popular.
    - However, I had to mark within that bitmask *that the bitmask was already using memory*.
    - This formed my `init`.
```{.rs filename="src/lib.rs"}
// Zero the array except the mask.
fn init() {
    unsafe {
        // Initialize mask
        // The following explodes if SIZE isn't a power of 2
        assert!(SIZE & (SIZE - 1) == 0);
        // First SIZE >> 3 bits are reserved as a validty byte/bit mask
        < snip >
        // Which has to reserve enough bytes for itself.
        < snip >
        // Set to 1
        < snip >

        // Initialize memory
        // Set to zero.
        < snip >
    }
    return;
}
```

## Crate

- To complete the lab today, create a crate named `helloworld` in a folder named `21` in your `371os` repository.
```{.bash}
cargo new 21 --name hello_world --vcs none
```

## "Hello world!" 

- Implement "Hello world!" using this crate.
- Use `i32` to store the "Hello world" data.
- While you do not have to develop it this way, the code could be a single line within an unsafe block containing only built-in function calls/declarations and `i32` literals.

```{.sh}
calvin@calvin:~/tmp/helloworld$ wc src/main.rs # 2 lines main, 2 lines unsafe, 1 line code
  5  15 174 src/main.rs
calvin@calvin:~/tmp/helloworld$ grep world src/main.rs # no plaintext in file
calvin@calvin:~/tmp/helloworld$ cargo r --release
   Compiling helloworld v0.1.0 (/home/calvin/tmp/oneone)
    Finished `release` profile [optimized] target(s) in 0.14s
     Running `target/release/helloworld`
Hello world!
```

### I love Python

- The following may be useful here, to the interested student.

```{.sh}
python3 -c '[print(ord(a)) for a in "Hello world!"]'
```

- This is probably insufficient for your purposes and will require some hacking.

### Transmute

- Since it is more idiomatic to use code other people have written in Rust...
    - I have an opinion on this.
- ...while it is possible to conduct this exercise using only raw pointers and casts...
    - (in the voice of Palpatine) "Do it!"
- ...it is my professional responsibility to recommend you use `transmute`.

```{.rs}
pub const unsafe fn transmute<Src, Dst>(src: Src) -> Dst
```

- [Read more](doc.rust-lang.org/std/mem/fn.transmute.html)

### Raw Pointers

- Also can use raw pointers here.
- Will get in the way of a single-line solution but that is okay - you should do you!

### Numeric Values

- One obvious way to use `transmute` is to change one type of data into another, without altering the underlying numeric values that exist in memory.
- For example, we can convert an array of `u8`s to an `i32`.

```{.rs}
unsafe {
    let bytes: [u8;4] = [0x12,0x34,0x56,0x78];
    let num: i32 = std::mem::transmute(bytes);
    println!("{:x}", num);
}
```

- I drew a warning when doing this, but it turns out I was doing what I wanted and did not wnat to do what `rustc` wanted, so I didn't worry about it. 

### Endianness

- The warning refers to the topic of *endianness*.
    - Big deal in C, kinda not in Rust actually.
        - Precisely because of that warning basically.
        - This lab was very involved.  [Endian](https://cd-public.github.io/courses/old/c89s25/qmd/endian.html)
- [Read more](https://en.wikipedia.org/wiki/Endianness)

> In computing, endianness is the order in which bytes within a word data type are transmitted over a data communication medium or addressed in computer memory, counting only byte significance compared to earliness. 

- Regard an `i32` as a word and a `u8` as a bit.
- Take note of the endianness revealed by the prior code.

### Numeric Address

- One possibly more advanced use of transmute is upon numeric addresses
    - The *key*, the numeric value of the address, stays the same.
    - The value, the numeric value in the memory location decribed by the address, stays the same.
    - The interpretation - how Rust understands the value at that location - changes.

```{.rs}
unsafe {
    let nats: &[u32] = &[0x3F800000];
    let nums: &[f32] = std::mem::transmute(nats);
    println!("{}", nums[0]);
}
```

- [Recall the meaning of 0x3F8000000](11_unsafe.qmd#/unions)
- I usually do this on arrays but I guess I'm not sure why.
    - Try things out.
    - Vectors are definitely banned though, that is way too high level.

# Fin

- To be continued in the homework.
