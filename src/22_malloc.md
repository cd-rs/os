---
title: malloc
format: html
---

## Homework

- Homeworks are due on the Friday *after* the week they correspond to lecture.
- So 9 days after the corresponding lab.

## Requirements

- [ ] `371rs/22` crate; I named mine "malloc"
- [ ] You write `src/lib.rs` that implements functions in the `src/main.rs` I provide.
- [ ] Regard it as "unsporting" to use `Vec<T>` or any other Rust built-in data structure.
    - **Unless** you are storing it (e.g. as an argument to `setter`).
    - Use arrays and raw pointers.
    - If you can't solve it without them, use them, but...
    - ...at least understand why it's hard and that there's an alternative.
    - *If you hand-implement a vector-like on top of static mut within the overhead allowance, you may use **your own** vectors*

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
        - You are permitted have overhead costs as high as 1-in-4 if you need them.
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

### Setter

- After the calls to `malloc` within main, we use a wrapping function `setter` to set memory at the location reserved by the malloc to have certain values.

```{.rs filename="src/main.rs"}
    let x = 0x44332211;
    let y = 0x12345678;
    setter(x, p0);
    setter(y, p1);
```

- This maybe isn't the most typical way to access memory.
    - A more common metaphor is `lw` and `sw` [more](https://stackoverflow.com/questions/54136371/understanding-how-lw-and-sw-actually-work-in-a-mips-program) 
    - I found this metaphor more interesting.
        - Words are fixed size, and felt quite trivial.
- Given some value returned by malloc, store up to that many bytes of information within the `BUS`.
    - `malloc` and `setter` together are responsible for ensuring the correctness and consistency of these bytes.
    - In this case, I malloc much more than I needed (16 and 32 bytes, respectively, for 4 byte words).
        - This is allowed, but wasteful.
        - It also makes testing easier.
- We note that `setter` does not ask have an argument for the size of memory being set.
    - It is your responsibility to infer this size using the type of the arguments.
    - This is to learn Rust, not to learn about memory, so a secondary objective but one I found worthwhile.
