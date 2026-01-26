---
title: Transmute 
format: html
---

## Announcements

- Lab Day
    - Play with memory
    - Use `unsafe`

## Homework

- `malloc` is this lab just more complete 
  - Cool, good, fun.
- Due Friday, 06 Feb. at 1440 ET.
  - And also covered in section. 

## Requirements

- [ ] Change the interpretation of numeric *values* with transmute on values
- [ ] Change the interpretation of *memory* with transmute on references.
- [ ] Write a "Hello world!" program that uses no string or character data.

# Exercise

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
