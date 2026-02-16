---
title: Graphics
format: html
---

<!--

array([[  0,   0,   0],
       [  0,   0, 168],
       [  0, 168,   0],
       [  0, 168, 168],
       [168,   0,   0],
       [168,   0, 168],
       [168,  87,   0],
       [168, 168, 168],
       [ 87,  87,  87],
       [ 87,  87, 255],
       [ 87, 255,  87],
       [ 87, 255, 255],
       [255,  87,  87],
       [255,  87, 255],
       [255, 255,  87],
       [255, 255, 255]], dtype=uint8)
-->

## Homework

- Homeworks are due on the Friday *after* the week they correspond to lecture.
- So 9 days after the corresponding lab.

## Requirements

Be advised this is a multistage lab that is intended to be interesting rather than easy.

1. [ ] Create a `src/colors.rs` to display all background colors.
1. [ ] Display and screendump the background colors to `.ppm`
1. [ ] Extract hex values from the `.ppm`
1. [ ] Create a script to convert images from url to VGA buffer array
   1. [ ] Download
   1. [ ] Scale
   1. [ ] Color map
   1. [ ] Output to `src/img.rs` as a datatype of some kind.
1. [ ] Add a function to `src/colors.rs` to display the image in `src/img.rs`

## Step 0

- Complete the "[Format](51_format.md)" lab.

## Step 1

> Add a function to `src/main.rs` to display all background colors in `qemu` via the VGA buffer.

- For this lab, we will display images using the VGA text buffer background color.
- To do that, we need to know what colors we have.
- To learn what colors we have, we will first display all of them.

### Colors

- I created a new file.
    - I am planning to not use it after the lab so I factored it out.

```{.rs filename="src/colors.rs"}   
pub fn colors() {
    // I had 9 total lines here.
    // 1 line was in an unsafe block (which was 3 lines total)
}
```

### Main

- There are two minor changes to main.
    - I call `colors` in `_start` and nothing else.
    - I add `mod colors;` early in the file.
    
```{.rs filename="src/main.rs" code-line-numbers="4,15" }
#![no_std]
#![no_main]

mod colors;
mod vga;

#[panic_handler]
fn panic(info: &core::panic::PanicInfo) -> ! {
    println!("{}", info);
    loop {}
}

#[unsafe(no_mangle)]
pub extern "C" fn _start() -> ! {
    colors::colors();
    loop {}
}
```

### Your task

- Create 16 evenly sized columns, one for each background color, across the screen.
- Display no text.
- Recall that there are 80 horizontal by 25 vertical characters.
- Recall that there are 720 horizontal by 400 vertical pixels.
- I am creating the below example using hexcodes I extracted and raw HTML.
    - It is hardcoded to 720 $\times$ 400 and may look odd on some screens.
    
<table style="border-collapse: collapse; border: none; padding: 0; margin: 0; line-height: 0;">
  <tr style="height: 400px;">
    <td style="width: 45px; background-color: rgb(0, 0, 0); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(0, 0, 168); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(0, 168, 0); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(0, 168, 168); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(168, 0, 0); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(168, 0, 168); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(168, 87, 0); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(168, 168, 168); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(87, 87, 87); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(87, 87, 255); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(87, 255, 87); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(87, 255, 255); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(255, 87, 87); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(255, 87, 255); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(255, 255, 87); padding: 0;"></td>
    <td style="width: 45px; background-color: rgb(255, 255, 255); padding: 0;"></td>
  </tr>
</table>

- It is obviously trivial to extract color values from this.
- Fortunately, you are still required to include a `src/colors.rs` in your `52` folder.

## Step 2

> Display and screendump the background colors to `.ppm`

- Easy step.
- Once your `qemu` is displaying as above, you are ready to proceed.

### The Monitor

- `qemu` has more features than I can recall anymore; most of them very cool.
- One is the "Monitor"
- Within the QEMU window, you can use <p><kbd class="kbd compound docutils literal notranslate"><kbd class="kbd docutils literal notranslate">Ctrl</kbd>+<kbd class="kbd docutils literal notranslate">Alt</kbd>+<kbd class="kbd docutils literal notranslate">2</kbd></kbd>
- From here, you can input a variety of commands.
    - [Read more](https://qemu-project.gitlab.io/qemu/system/monitor.html)
- At least try `help` and have at least on thought about it.
    - `qemu` is listed on a job add for a Google position in Portland starting at 113k/yr as I type this.

### Screendump

- Try to following.
    - You can choose your own filename.
    - I used `dump.ppm`
    - You will want to use `.ppm`

```{.sh}
screendump dump.ppm
```

- QEMU documentation states:

> Save screen into PPM image *filename*.

## Step 3

> Extract hex values from the `.ppm`

### PPM files

- The PPM file format is ancient and I'm not sure of the authoritative documentation.
- This appears correct to me.  [https://netpbm.sourceforge.net/doc/ppm.html](https://netpbm.sourceforge.net/doc/ppm.html)
- You don't need to dwell on it overlong but:
    - There is a header that gives the filetype, the size, and highest brightness value.
    - There's a block write of pixels.

### `head`

- It is trivial to verify you have a well formed PPM file.
    - We use `head` to read the first $n$ lines of a file.
    - We use `-3` to specify that $n=3$
    - Only the first 3 lines are human readable.

```{.sh}
head -3 dump.ppm
```

- If you do not see the following, something went wrong.

```{.sh}
P6
720 400
255
```

- This states that:
    - You have a PPM image of type P6, this is the most common format (there is a less used P3)
    - Your image is 720 by 400 pixels
    - Brightness is out of 255.
- From here I perceive 2 "obvious" options.
    - Use some combination of `head`, `tail`, `hexdump` and other command line utilities to extract all hex values.
    - Use Python, NumPy, and PIL, all of which you likely have on your device, to extract all hex values.
    - Be advised you can compute the precise location of the first instance of every color in either a `.ppm` file or a NumPy array as you have perfect knowledge about the number of pixels.
- These two are free:

```{.py}
import numpy as np
from PIL import Image

IMG_NAME = "dump.ppm"

img = np.array(Image.open(IMG_NAME))
print(img[0][:10])
```

```{.sh}
cat dump.ppm | tail -1 | head -c4 | hexdump
```

- I ended up using Python here because I was going to use Python for the next step.
    - Unless?
    
## Step 4

> Create a script to convert images from url to VGA buffer array

1. [ ] Download
1. [ ] Scale
1. [ ] Color map
1. [ ] Output to `src/img.rs` as a (Rust) datatype of some kind.

The following instructions assume students will proceed using Python's NumPy package. This fulfills a secondary learning objective of familiarity with vector operations that were discussed briefly [here](40_kernel.md#mmxsse).

::: {.callout-note collapse="true"}

### Extension for Advanced Students

Advanced students will already be familiar with these operations and with Python. They should complete Step 4 in CUDA C++, fulfilling the extension learning objective of familiarity with GPU programming and bus operations as mediated by the host/device metaphor. If you do not have access to a physical NVIDIA GPU, I provide instructions on usage in Colab [here](https://github.com/cd-public/coluda/blob/main/GPU_CUDA.ipynb).

Learning CUDA is straight-forward and an all-around good time. Learning C++ is quite the opposite. By combining both, you can practice moderation.

[CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

:::

### Use of Numpy

- 