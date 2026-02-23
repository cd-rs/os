---
title: Guest
format: html
---

# Guest Lecture

Today we are taking a brief reprieve from the lecture-lab cadence to allow my voice to recover.

## Part I 

- Motivated by *Calvin Deutschbein Thought* on Rust: "It's good because of error handling."
- We welcome Jane Lusby, who is at high probability [this Jane Losare-Lusby](https://github.com/yaahc)
- Jane's talk at RustConf 2020 is titled "Error handling Isn't All About Errors" and I find it's thesis convincing.
- Here is a [direct link](https://www.youtube.com/watch?v=rAF8mLI0naQ).
- Here is an embed:

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/rAF8mLI0naQ?si=6gdPawbuBVUl9-rc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Part II

- Motivated by the planned extension for the final week of class, on asynchronous computing.
- A great way to understand `async` is write 20 lines of JavaScript.
    - [Like this](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- You should also be thinking about a looming problem.
    - What happens if you want to be updating the VGA text buffer to, for example, display an animation that changes ever $n$ nanoseconds.
    - What happens if at the same time, you direct inputs into the OS through some means (to be introduced this and in coming weeks).
    - How does the OS juggle timing-based and what we usually call *interrupt*-based (e.g. driven by exogenous factors) tasks?
- This essay is hosted on a talk webpage, and can be seen at [https://sunshowers.io/posts/cancelling-async-rust/](https://sunshowers.io/posts/cancelling-async-rust/)

