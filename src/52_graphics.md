---
title: Graphics
format: html
---

<!--

```{.py}
import numpy as np
from PIL import Image

IMG_NAME = "dump.ppm"

img = np.array(Image.open(IMG_NAME))
print(img[0][::45])
```

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
   1. [ ] Output to `src/colors/img.rs` as a datatype of some kind.
1. [ ] Add a function to `src/colors.rs` to display the image in `src/img.rs`.
    1. [ ] And call the function from `src/main.rs

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
    - It is *not* an image.
    
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

<!--

```{.rs}
pub fn colors() {
    for i in 0..16 {
        for j in 0..25 {
            for k in 0..5 {
                unsafe {
                    *((0xb8000 + (5 * i + 80 * j + k) * 2 + 1) as *mut u8) = (i as u8) << 4;
                }
            }
        }
    }
}
```
-->

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
    - `qemu` is listed on a job ad for a Google position in Portland starting at 113k/yr as I type this.

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

The following instructions assume students will proceed using Python's NumPy package. This fulfills a secondary learning objective of familiarity with vector operations that were discussed briefly [here](40_kernel.qmd#mmxsse).

- As a fun bit, you may want to set up your script to optionally accept a URL at command line. 
    - I did this, and it made testing a bit easier.
    - I *also* had an `IMG_URL` pointed at something that would otherwise display if there was no argument.

::: {.callout-note collapse="true"}

### Extension for Advanced Students

Advanced students will already be familiar with these operations and with Python. They should complete Step 4 in CUDA C++, fulfilling the extension learning objective of familiarity with GPU programming and bus operations as mediated by the host/device metaphor. If you do not have access to a physical NVIDIA GPU, I provide instructions on usage in Colab [here](https://github.com/cd-public/coluda/blob/main/GPU_CUDA.ipynb).

Learning CUDA is straight-forward and an all-around good time. Learning C++ is quite the opposite. By combining both, you can practice moderation.

[CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)

:::

### Use of Numpy

#### Download

Given this is an advanced class, I'm going to trust you to do the following without providing example code.

- Regard it as "unsporting" to download a file and work with a local copy.

- Use `requests` to get an image by url.
    - You can [read this](https://cd-public.github.io/courses/cs1/slides/requests.html)
    - You can use [this URL](https://cd-public.github.io/ai101/images/photo-cat.jpg)
```{.email}
https://cd-public.github.io/ai101/images/photo-cat.jpg
```
- Use `BytesIO` to interpret the HTTP response as a file.
- Use PIL's `Image` API to open the image.
    - You can [read this](https://cd-public.github.io/courses/old/ccf24/slides/04_1_img.html)
- Coerce the image to a NumPy array using NumPy.

##### Images

I only got `.jpg` and `.webp` to work for some reason, but it's not a big deal and you aren't required to learn `PIL`.

- I took [this](https://cd-public.github.io/ai101/images/photo-cat.jpg) myself so it is definitely free to use.
    - Her name is Ursula.
```{.email}
https://cd-public.github.io/ai101/images/photo-cat.jpg
```
- [This](https://www.leadvilletwinlakes.com/wp-content/themes/yootheme/cache/ba/View-of-Mount-Massive-LCTP-Cropped-scaled-ba58e696.webp) is a wide picture that should be fine, from a tourism bureau.
    - [Read more](https://www.leadvilletwinlakes.com/listing/mt-massive/)
```{.email}
https://www.leadvilletwinlakes.com/wp-content/themes/yootheme/cache/ba/View-of-Mount-Massive-LCTP-Cropped-scaled-ba58e696.webp
```
- And maybe the best for testing, an Adobe Stock [rainbow](https://stock.adobe.com/search?k=rainbow&asset_id=114495172)
    - The url looked unstable so I'm [rehosting](https://cd-rs.github.io/os/img/rainbow.jpg).
    - Hopefully *I'm* hosting stably.
```{.sh}
https://cd-rs.github.io/os/img/rainbow.jpg
```


<!--

```{.py filename="url_to_rs.py"}
from io import BytesIO
import requests
from PIL import Image
import numpy as np
import sys

IMG_URL = "https://t4.ftcdn.net/jpg/01/14/49/51/360_F_114495172_sTd0Eu8Tv1BP3LBYzgsd5YlADuF31Scj.jpg"
IMG_NAME = "dump.ppm"
ROWS = 80
COLS = 25

len(sys.argv) > 1 and (IMG_URL := sys.argv[1],)

colors = np.array(Image.open(IMG_NAME))[0][::45].astype(np.int32)

arr = np.array(Image.open(BytesIO(requests.get(IMG_URL).content)))

arr = arr[::len(arr)//COLS, ::len(arr[0])//ROWS][:COLS, :ROWS].reshape((ROWS*COLS,3))

nearest = lambda color : int(np.argmin(np.sum((color - colors) ** 2, 1)))

open("src/colors/img.rs", "w").write(f"pub const ARR: [u8; {ROWS*COLS}] = " + str([nearest(c) << 4 for c in arr]) + ";")
```

-->

#### Scale

- Do I look like I know how to scale images?
    - Probably either sample or average.
    - I don't think I care.
- My code scales to fit the VGA buffer horizontally.
    - Then either "squish" or "stretch" vertically.
    - You could also crop horizontally.
        - Doesn't matter to me.
    - Recall, the VGA buffer has more pixels than we are addressing.
    - You can only address characters, which are many pixels in size.
    - Your image will be *low* resolution.

#### Color Map

::: {.callout-note appearance="simple"}

## Code Structure Note

I included my code extracting hex-values from `dump.ppm` here.

I thought it made more sense than making a new file, it shared similar imports, and was only a few lines.

Plus, if I run on another system, which may have a different color representation, I'll be able to quickly generate the `.ppm` and have no other steps!

:::

- You image will include colors that cannot be recognized by the VGA text buffer.
- You will need to compute color distance between the 
    - Color you are trying to show, and
    - The 16 available colors you computed in a previous step.
- A naive approach would be to regard colors in 3-space with dimensions of `R`, `G`, and `B` values.
    - This is appropriate, but sub-optimal.
    - So it's what I did.

::: {.callout-note collapse="true"}

### Extension for Advanced Students

Advanced students will already be familiar with distance in $n$-space and hexcodes and should use a perceptually uniform color space. In this case, `L*a*b`.

[Read more](https://en.wikipedia.org/wiki/CIELAB_color_space)

There is first class support in Python, I hear, and you can learn more from this poster, but one of Professor Brown's undergraduate researchers.

[Poster](https://luebke.us/publications/pdf/vss2019.poster1.pdf)

:::

You are doing this in NumPy to take advantage of vectorized operations.

- [Read more](https://cd-public.github.io/scicom/05_numpy.html#vectorization)
- Regard it as "unsporting" to use loops for a single pixel.
    - I didn't vectorize across the full pixel array because I converted to a string in the same stage (as a list comprehension).
    - You will want to look up "argmin".
        
#### Output

- I used a list comprehension to map my colormapper across the scaled pixel array, format to string, and write to a `.rs` file.
    - You are not required to use a single line, obviously.
- I want to show file sizes.
    - I wrote only single lines of code (no blocks) with open lines between.
    - It was not minimized but it was not verbose either.
        - 5 `import`s
        - 4 "constants"
            - Python doesn't have constants.
        - 6 lines of executable code.
```{.sh}
$ wc url_to_rs.py src/colors/img.rs
  22   75  704 url_to_rs.py
   0 2006 9257 src/colors/img.rs
```
- I wrote to `src/colors/img.rs` as it was *I think* the place a file used by `src/colors.rs` should be.
    - I didn't love this because I had to make a new directory.
        - I just `mkdir` once rather than scripting this step.
    - Do whatever you want here, as long as your `url_to_rs.py` writes to the right place.
    
## Step 5

- Add a `image()` function to `src/colors.rs` that:
    - Reads the image data from `src/colors/img.rs`
    - Writes the image data to the VGA text buffer as background colors.
- Call this function from `src/main.rs`
- Look at your image.

### Example

- Here is my result over the "Mt. Massive" image from the tourism bureau.

#### Original

- Hosting cross-site.

![](https://www.leadvilletwinlakes.com/wp-content/themes/yootheme/cache/ba/View-of-Mount-Massive-LCTP-Cropped-scaled-ba58e696.webp)

#### VGA Text Buffer

- Extracted to `.ppm`, converted to `.png`, converted to base64 and directly embedded.

<img src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAtAAAAGQCAIAAAAIhcA6AAAJ70lEQVR4nO3dQY7jugFAwTiYC3rF
PqK48hE72wSINAN+PVnuqdoSoihKbTxw049t2/4FAFD697sXAAD8fIIDAMgJDgAgJzgAgJzgAABy
ggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkO
ACAnOACAnOAAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACD3690L
gJ9sjHHZveacC1dduUI+y9oXBXuccAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAA
ADnBAQDkBAcAkBMcAEBOcAAAOcEBAOQEBwCQe2zbtnDZGOP0pfxt5px7Q2vbezDhTRw81+m7AfwM
9/9l+6nWfrEPOOEAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAn
OACAnOAAAHKCAwDICQ4AIPf4/v7eGzv4h/djjGY9AMCtreWBEw4AICc4AICc4AAAcoIDAMgJDgAg
JzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4AICc4AAAco9t2/bGDv6rPf/cnHNv
yM4D8MM44QAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4AICc
4AAAcoIDAMgJDgAg99i27d1r+I0xxmX3mnMuXHWTFV65jJ/K9gJEnHAAADnBAQDkBAcAkBMcAEBO
cAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAAADnBAQDkBAcAkPs1xjh3xjnnuRNe
ea+D3Ti419oyTt/5n+r07V2b8OCqtXudvsKbfFFX/lXyz619oldOyI/hhAMAyAkOACAnOACAnOAA
AHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACA3OP7+/uym805
F64aYyxMeHDVmrXFr7n/4tdeytqEB658KbzL6/XaG9q2bW/oym8e+BNOOACAnOAAAHKCAwDICQ4A
ICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDIPb6/v8+dcc55
7oQfbYyxcNXBHh5MuHbV2jJIvV6vvaHn87kw4doHcODr62tvaG2FVzp9e2/ipz7X6V8v7+KEAwDI
CQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4
AIDcY9u2c2ccY5w74Zo5597QlSs8WAbv8nq99oaez+cdJjzd/VcIe9Z+sf32ptZeihMOACAnOACA
nOAAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKP
bdsuu9kY47J7XWnOuTd08MgHV51ubRmv12tv6Pl8/tM1/a+1FZ7+RX19fZ074YGDPbxy56908Fxr
Pno3SN3kt5f/5oQDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4AICc
4AAAcoIDAMgJDgAgJzgAgNzj+/v7spvNOReuGmOcO+Gag2V8fX0tTPh8PveGXq/XuRMeOLjXwYRr
u7E24YGDD2BtwjVrj3xg7aV8tPs/8toK7/9ccBknHABATnAAADnBAQDkBAcAkBMcAEBOcAAAOcEB
AOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAAADnBAQDkHtu2LVw2xli4as65MOHBVWter9fe
0PP5PPde/KG1l3L/V3n6Cq/cqJu8lPu/5QNX7saB+2/U/X30d3gTTjgAgJzgAAByggMAyAkOACAn
OACAnOAAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyD22bdsbG2PsDc05
m/W82ev12ht6Pp93WMaa0xd/k436aKfv4dqEH/0qT3/kK/mr/Bv8hX+VB5xwAAA5wQEA5AQHAJAT
HABATnAAADnBAQDkBAcAkBMcAEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJB7bNv27jX8
xuv1OnfC5/P5I+91/2X8he6/8wcrPHCTxR+4/87Duda++bVfgAMH93LCAQDkBAcAkBMcAEBOcAAA
OcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAAADnBAQDkBAcAkBMcAEDuMcZ49xrgUnPO
vaH7/zl89OLhR3o+n+dO+Hq9LrvXlZxwAAA5wQEA5AQHAJATHABATnAAADnBAQDkBAcAkBMcAEBO
cAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJB7jDHevQb4bHPOvaEr/74OlnHgo38BbrLzwJ9w
wgEA5AQHAJATHABATnAAADnBAQDkBAcAkBMcAEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQH
AJATHABA7nEwNsa4bB03MefcG/oLdwMAzuKEAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzg
AAByggMAyAkOACAnOACAnOAAAHKCAwDICQ4AICc4AIDcY4yxcNmcc2/o9AnXrC3j/k7f+SutveX7
Pxfc3Ef/bvBjOOEAAHKCAwDICQ4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAn
OACAnOAAAHKCAwDICQ4AIPfr9BnnnHtDY4yFCQ+uOrjXgdNXuLaMmzzX2r0OrO3hgdPfF9zclb+i
cBknHABATnAAADnBAQDkBAcAkBMcAEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABA
TnAAADnBAQDkHmOMd6+Bd5pz7g2tfRtrE95kGbDAxwZ/wgkHAJATHABATnAAADnBAQDkBAcAkBMc
AEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAAALnHGOPda4BFc869obUP+2DC
A/6IAH7LCQcAkBMcAEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5wQEA5AQHAJATHABATnAAADnBAQDk
BAcAkBMcAEBOcAAAuccY491r4PPMOfeGfFEpOw98KCccAEBOcAAAOcEBAOQEBwCQExwAQE5wAAA5
wQEA5AQHAJATHABATnAAADnBAQDkBAcAkBMcAEBOcAAAOcEBAOQeY4x3r+Enm3PuDf2FO283buj0
l+ItA/+XEw4AICc4AICc4AAAcoIDAMgJDgAgJzgAgJzgAAByggMAyAkOACAnOACAnOAAAHKCAwDI
CQ4AICc4AICc4AAAcv8B/pXD9XQXqvEAAAAASUVORK5CYII="/>