---
title: "Options"
---

## Announcements

- **Welcome** to Systems in Rust
- **Action Items**:
  - "Hi Cargo" is due on Friday
  - We are now ramping for Wordle

## Today

- [ ] Mutability
- [ ] Typing
- [ ] Parameters
- [ ] Loops
- [ ] Intro to Ownership

# Mutability

## Variables

- Python variables are, I think a bit sketchy.
- There is no difference between *creating* and *updating* the value of a variable.
```{.py filename="file.py"}
x = 10
x = 11
```

## Why it matters

- This isn't objectively bad, but isn't good specifically in the case of languages that track how much memory they use.
- You cannot determine without examining prior code whether the following statement *uses more memory* or *uses existing memory*
```{.py filename="file.py"}
y = 10 # Was there a prior y?
```
- [Backstreet Boys - I Want It That Way (Official HD Video)](https://www.youtube.com/watch?v=4fndeDfaWCg)

## Alternatives

- The other scripting language, JavaScript, doesn't even do this:
```{.js filename="script.js"}
let y = 10;
y = 11 // There was a prior y! (kinda)
```
- .rs is a bit more .js-like than .py-like when it comes to variables.

## Rust let

- Like .js, .rs uses the `let` formulation to create new variables:
```{.rs filename="src/main.rs"}
let s = "Imma string in RUST!"; // Rust comment
```
- However it differs in a critical way.
- Say we wish to reassign `y`:
```{.rs filename="src/main.rs"}
s = "Anything else."
```

## Immutability

- If we attempt to do so in Rust, we'll draw a mutability error:
```{.bash}
error[E0384]: cannot assign twice to immutable variable `s`
 --> src/main.rs:3:4
  |
2 |    let s = "Imma string in RUST!"; // Rust comment
  |        - first assignment to `s`
3 |    s = "Bleeblarbu";
  |    ^^^^^^^^^^^^^^^^ cannot assign twice to immutable variable
  |
```
- And get a helpful recommendation:
```{.bash}
help: consider making this binding mutable
  |
2 |    let mut s = "Imma string in RUST!"; // Rust comment
  |        +++
```

## Defaults

- Rust variables default to immutable.
- You've seen this before, sorta:
```{.bash}
>>> x = (1,2)
>>> x[1] = 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
```
- Rust variables are like Python tuple elements.


## Defaults

- Rust variables default to immutable.
- This follows a post-language release style development in .js, where programmers are now recommended to use `const` rather than `let` for all variables.
```{.js filename="script.js"}
const y = 10; // This reflects recent .js style recommendations.
y = 11;       // This will throw an error.
```
- You can check in `node` or in your browser.
```{.bash}
> const y = 10;
undefined
> y = 11;
Uncaught TypeError: Assignment to constant variable.
```

## Mutability

- If a variable positively, absolutely, must be updated for a program to make sense:
    - Counting words in a file
    - Counting visitors to a website
    - Counting sheep before hitting a honk shoo / snork mimimi angle
- Use the `let mut` formulation.
    - .rs `let mut` :: .js `let` :: .py `[]`
    - .rs `let` :: .js `const` :: .py `()`
    
## Example
    
```{.rs filename="src/main.rs"}
let mut sheeps_counted = 0;
sheeps_counted = 1;
println!("Sheeps accounted for counter count: {sheeps_counted}");
}
```
- This is allowed.
    - It will draw an unused variable warning on the zero, which is for another day.

## My advice

- Use `let`
- If you get an error when using `let`, you should consider changing your code design equally as strongly as you consider adding `mut`
- You can do either (just think about both)

## Today

- [x] Mutability
- [ ] Typing
- [ ] Parameters
- [ ] Loops
- [ ] Intro to Ownership

# Typing

## More than hints

- In Rust, the Pythonic type hint formulation is mandatory in all cases where the type of a variable is non-obvious.
```{.py filename="file.py"}
# Somehow each of this things is totally allowed
x : int
x = 1.5
y : float = "Hi"
```
- It is also enforced.

## Try it v0

- We can yeet the accursed Python directly into `src/main.rs` and just furnish `let` to make the variable declarations well formed:
```{.rs filename="src/main.rs"}
fn main() {
    let x : int;
    x = 1.5;
    let y : float = "Hi";
}
```
- We will yield a somewhat unremarkable error:
```{.bash}
error[E0412]: cannot find type `int` in this scope
 --> src/main.rs:2:13
  |
2 |     let x : int;
  |             ^^^
  |             |
  |             not found in this scope
  |             help: perhaps you intended to use this type: `i32`
```

## Integers

- Rust numerical types have a fixed size.
- They are in that respect like NumPy integers
- They are different in that respect from Python `int` which is of theoretically infinite size and JavaScript, which only has floats.
- You can tell by working with large numbers
```{.bash}
>>> import numpy as np
>>> x = np.int8(100)
>>> x * x
<stdin>:1: RuntimeWarning: overflow encountered in scalar multiply
np.int8(16)
>>> y = 100
>>> y * y
10000
```

## Signage

- In Rust, as in NumPy, we specify whether integers may be signed (negative) or not.
- These are usually referred to as "integer" and "unsigned"

:::: {.columns}

::: {.column width="50%"}      
      
```{.py filename="integer.py"}
>>> x = np.int8(100)
>>> x + x
<stdin>:1: RuntimeWarning: overflow encountered in scalar add
np.int8(-56)
>>> x - 110
np.int8(-10)
```

:::

::: {.column width="50%"}

```{.py filename="unsigned.py"}
>>> x = np.uint8(100)
>>> x + x
np.uint8(200)
>>> x - 110
<stdin>:1: RuntimeWarning: overflow encountered in scalar subtract
np.uint8(246)
```

:::

::::


## On ints

- Unsigned can be twice as big but can't be negative.
- The maximize size is two to the power of "bit length" - the number after int, like 8.
    - One lower power for signed values.
```{.bash}
>>> x = np.int8(2 ** 7)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OverflowError: Python integer 128 out of bounds for int8
>>> x = np.int8(2 ** 7 - 1)
>>> x
np.int8(127)
```
- In Rust, as in NumPy, we must decide how much memory we use before we use it.

## Rust integers

| Length  | Signed  | Unsigned |
| ------- | ------- | -------- |
| 8-bit   | `i8`    | `u8`     |
| 16-bit  | `i16`   | `u16`    |
| 32-bit  | `i32`   | `u32`    |
| 64-bit  | `i64`   | `u64`    |
| 128-bit | `i128`  | `u128`   |
| architecture dependent | `isize` | `usize`  |

- You should use u64 unless you have a compelling reason not to.

## Aside

- The case of wanting to use `-1` for error handling does not apply to Rust for reasons we'll cover latter, so always try to get code working with unsigned first.
- 64 is just (at 99.9%+ probability) the preferred size for your physical device.
- You should use the forthcoming "Option" for these matters.

![](img/option.png)

## Does np.uin64 ~= u64

- What happens if you add `1` to these?
    - Make a hypothesis.
        - E.g. write a comment.
    - Conduct an experiment.
        - E.g. alter and run the code.
    - Update your hypothesis, if not supported.

:::: {.columns}

::: {.column width="50%"}     

```{.py}
>>> x = np.uint64(2 ** 64 - 1)
>>> x
np.uint64(18446744073709551615)
```

:::

::: {.column width="50%"}

```{.rs}
fn main() {
    let x : u64 = 18446744073709551615;
    println!("{x}");
}
```

:::

::::

## Floats

- There are floats in Rust.
- There are not floats in the Linux kernel.

> [Kernel code is normally prohibited from using floating-point (FP) registers or instructions, including the C float and double data types.](https://docs.kernel.org/core-api/floating-point.html)

- Therefore there are not floats in this class.
    - If an operating system can be written without floats, so too can your code.

## Booleans

- Booleans are called `bool` (like Python) and stylized all-lowercase (like JavaScript)
```{.rs filename="src/main.rs"}
fn main() {
    let t = true;

    let f: bool = false; // with explicit type annotation
}
```
- Otherwise unremarkable.

## Characters

- Vs. Python, Rust has a specific character type, distinct from strings of length 1.
- It uses single quotes, which look like this: `''`
- Here is an example:
```{.rs filename="src/main.rs"}
fn main() {
    let c : char = 'a';  // Correct
    let c : char = "a";  // Banned
}
```

## Error message

```{.bash}
error[E0308]: mismatched types
 --> src/main.rs:3:20
  |
3 |     let c : char = "a";
  |             ----   ^^^ expected `char`, found `&str`
  |             |
  |             expected due to this
  |
help: if you meant to write a `char` literal, use single quotes
  |
3 -     let c : char = "a";
3 +     let c : char = 'a';
  |

For more information about this error, try `rustc --explain E0308`.
error: could not compile `scratch` (bin "scratch") due to 1 previous error
user@DESKTOP-THMS2PJ:~/tmp/scratch$ cat src/main.rs
fn main() {
    let c : char = 'a';
    let c : char = "a";
}
```

## Takeaway

- I never used Rust characters but ended up using them on Wordle, so just showing them now.
- I don't expect you to use them pretty much ever, but they motivate the next topic via this line:
```{.bash}
  |             ----   ^^^ expected `char`, found `&str`
```
- What in the name of FeO is a `&str`

## "Strings"

- There are kinda not really exactly strings in Rust.
- This mostly has to do with Rust having unicode support.
- We won't really leverage unicode this term since we aren't writing human-facing applications.
- But we still deal with the consequences.

## Today

- [x] Mutability
- [x] Typing
- [ ] Parameters
- [ ] Loops
- [ ] Intro to Ownership

# Intro to Ownership

## Size

- Versus the other types in Rust, which we stressed were of fixed size...
- A string is not.
```{.rs}
// String of length 0
let s = ""; 
// Complete text of Bhagavad Gita
let t = "Dhritarashtra said: O Sanjay, after gathering on the holy field of Kurukshetra, and desiring to fight, what did my sons and the sons of Pandu do? ...
```
- And in fact, if we implemented Python integers in Rust, they would follow similar rules.
    - Anything that has no bounded upper size, basically.
    
## Ownership Rules

- Each value in Rust has an _owner_.
- There can only be one owner at a time.
- When the owner goes out of scope, the value will be dropped.

## Scope

- Quoth Rust Book:

```{.rs}
    {                      // s is not valid here, since it's not yet declared
        let s = "hello";   // s is valid from this point forward

        // do stuff with s
    }                      // this scope is now over, and s is no longer valid
```

- You can experimentally verify each of the claims.
- Basically, the memory associated with `s` exists at some time points, but not others.

## Capital S String

- We have thus far used "string literals", where the string is typed into the program.
- This is a special case and doesn't allow *working* with strings.
- For that, we use capital S `String`, which is closer to data structure than a data type in some ways:
```{.rs}
    let mut s = String::from("hello");

    s.push_str(", world!"); // push_str() appends a literal to a String

    println!("{s}"); // this will print `hello, world!`
```
- It accepts a push operation a la a queue/stack/list, and must be initialized with a function call.
- A `String` is mutable, a literal is not.

## It's confusing

- This leads to some un-Pythonic behavior.
- Versus the immortal `u64`, our most beloved type, the ignomious `String` is fickle and fleeting.
- We compare *fixed size* and *variable size* types, which have distinct behavior

:::: {.columns}

::: {.column width="50%"}     

- This works.

```{.py}
fn main() {
    let x = 5;
    let y = x;
    println!("{x}");
}
```

:::

::: {.column width="50%"}

- This doesn't.

```{.rs}
fn main() {
    let s = String::from("6");
    let t = s;
    println!("{s}")
}
```

:::

::::

## What's happening?

- I am unwilling to defend this Rust design decision, though we'll understand it better over the course of the term.
- Basically, `s` passes "out of scope" as soon as it is assigned to `t`.
- Thereafter, there is no declared variable of name `s`.
- But this only happens to some types (and in my view which types are non-obvious).
    - It is potentially infinite types, but it's unclear that e.g. `String::from("6")` isn't a fixed width string of lenth 1 (to me at least).

## Clone

- My secret inside source with a real job (e.g. not professor) who writes Rust and also thought this was a bit silly:

> Whenever I use Rust, I just always `.clone` and when someone asks me about it, I say that's a performance optimization for latter.

- Rust says the same thing, actually:

```{.bash}
help: consider cloning the value if the performance cost is acceptable
  |
6 |     let t = s.clone();
  |              ++++++++
```

## Example

- It is reasonable to use `.clone` on capital S `String` for e.g. Wordle, as needed.
- As a challenge, don't use `.clone` (you don't need it)

:::: {.columns}

::: {.column width="50%"}     

- This works.

```{.py}
fn main() {
    let x = 5;
    let y = x;
    println!("{x}");
}
```

:::

::: {.column width="50%"}

- This works.

```{.rs}
fn main() {
    let s = String::from("6");
    let t = s.clone();
    println!("{s}")
}
```

:::

::::

- Both draw warnings for unused variables, but it's a silly example anyway.

## Why it matters?

- You'll probably want to decompose capital S `String` operations into functions.
    - This is known as "programming"
- You may want to `.clone()` a capital S `String` beforing yeeting it into a helper.

## Example Code

```{.rs filename="colour.rs"}
fn print_red(s:String) {
    // Some terminal hacking nonsense for colors
    println!("\u{001b}[31m{s}\u{001b}[0m");
}

fn print_grn(s:String) {
    // More nonsense but 31 -> 32
    println!("\u{001b}[32m{s}\u{001b}[0m");
}

fn main() {
    let s = String::from("6");
    print_red(s.clone());
    print_grn(s.clone());
    println!("{s}")
}
```

## Example output

- I see something like this, your mileage may vary:
<p style="color:red">6</p>
<p style="color:green">6</p>
<p style="color:white">6</p>
- On these slides, that's styled with HTML, in my terminal it is styled with "ANSI Escape Codes"
- My source is here: [Read me!](https://saturncloud.io/blog/how-to-print-colored-text-to-the-terminal/)
```{.py filename="colour.py"}
print("\u001b[31mHello, world!\u001b[0m")
```
- More in the lab.

## Today

- [x] Mutability
- [x] Typing
- [ ] Parameters
- [ ] Loops
- [x] Intro to Ownership

# Parameters

## Declarations

- You have now seen how functions are declared when they accept arguments.

```{.rs filename="colour.rs"}
fn print_red(s:String) {
    // Some terminal hacking nonsense for colors
    println!("\u{001b}[31m{s}\u{001b}[0m");
}

fn print_grn(s:String) {
    // More nonsense but 31 -> 32
    println!("\u{001b}[32m{s}\u{001b}[0m");
}
```

- Same as variables.

## Today

- [x] Mutability
- [x] Typing
- [x] Parameters
- [ ] Loops
- [x] Intro to Ownership

# Loops

## 3 loops

- There are 3 loops in Rust, one of for which I am issuing a partial ban, and also recursion.
    - `loop`
    - `for`
    - `while`
    - Recursion
    
# If
    
- There's the 4th phantom loop type, `if`
    - Python-like, except
        - Curly bracket delimited instead of of colon/indent delimited
        - Uses `else if` instead of `elif`

## Loop

- Rust `loop` is its infinite loop type.
- I don't recommend using it.
```{.rs filename="src/main.rs"}
// The rust book literally tells us to just run this code?
fn main() {
    loop {
        println!("again!");
    }
}
```

## If you must

- If you must `loop`, please use:
    - A named `loop`, with
    - A named `break`

```{.rs filename="src/main.rs"}
// I would never do this, but it can be fun.
fn main() {
    let mut x = 0;
    `loop_city: loop {
        println!("{x}");
        x += 1
        if x > 10 {
            break `loop_city;
        }
    }
}
```

## Just recurse

- This is how I would do that...
```{.rs filename="src/main.rs"}
fn help(x:u64) {
    if x <= 10 {
        println!("{x}");
        help(x + 1);
    }
}

fn main() {
    help(0);
}
```
- By the way - `!` rather than `not` is logical negation.
    - So would be `!(x > 10)` vs. `not (x > 10)`
    
## while

- My second favorite after recursion is `while`
    - I finished undergraduate without using a `for` loop btw.
    - You may not this is identical to the recursive solution.
    


:::: {.columns}

::: {.column width="50%"}      

- Via `while`

```{.rs filename="src/main.rs"}
fn main() {
    let mut x = 0;
    while x <= 10 {
        println!("{x}");
        x += 1;
    }
}
```

:::

::: {.column width="50%"}    


- Via `fn`

```{.rs filename="src/main.rs"}
// elsewhere help is called on 0
fn help(x:u64) {
    if x <= 10 {
        println!("{x}");
        help(x + 1);
    }
}
```

:::

::::

## for

- Rust `for` is Pythonic "for each" rather than C/C++/Java/JavaScript "for" which should help you.
- We also implement a collection type, the array (which is Python tuple-like or NumPy array-like)
```{.rs filename="src/main.rs"}
fn main() {
    let a = [10, 20, 30, 40, 50];

    for element in a {
        println!("the value is: {element}");
    }
}
```

## I don't know...

- I don't know if you'll think of Wordle as loops over elements of a collection:
```{.rs}
    for c in guess.chars() {
        println!("{}", c);
    }
```
- But the alternatives are, I think, pretty bleak:
```{.rs}
    for i in 0..5 { // Rust range
        // Rust strings lack indices
        // Instead they return either a character or a "None"
        // We have to unwrap that
        // Rust strings, amirite
        println!("{}", guess.chars().nth(i).unwrap());
    }
```
- Helpfully, `cargo run` told me how to write that.

## Today

- [x] Mutability
- [x] Typing
- [x] Parameters
- [x] Loops
- [x] Intro to Ownership

## Missing pieces

- We did not discuss the following in detail:
    - Floats (don't use them)
    - Range (`0..5`)
    - Error handling (`unwrap`)
    - String slices (`&str`)
- I think I taught you how to avoid each, however.
- Read more in Rust Book chapters [3](https://doc.rust-lang.org/book/ch03-00-common-programming-concepts.html) and [4](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html).