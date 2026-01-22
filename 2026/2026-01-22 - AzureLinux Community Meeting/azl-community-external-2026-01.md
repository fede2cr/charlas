---
theme: https://github.com/maaslalani/slides/raw/main/styles/theme.json
author: alvaro.figueroa@microsoft.com
date: 2026-01-22
---

# Azure Linux Community Call

<br>

<br>

<br>

<br>

## Topics:

- How to speed up AzureLinux 3?
<br>
- What we won't cover here
<br>
- How to?
<br>
- Benchmarks
<br>
- Bonus
<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

<br>

### By Álvaro Figueroa, Azure Linux Escalation team, from a cloud forest in Costa Rica

---
# What we won't cover here

- General performance: sysctl, filesystems, kernel, etc
- General benchmarking or profiling: only benchmarking of one tool at a time
- Your workload: will be using books from Gutenberg project (string heavy workload)

# What is "coreutils" and what is this new version in rust?

Get ready for the shortest unix history possible.

---

# How to (install rust-coreutils)

```bash
sudo tdnf -y update
sudo tdnf -y install cargo lsb-release
sudo tdnf -y install https://github.com/fede2cr/azurelinux-rust-coreutils/releases/download/v0.5.0/rust-coreutils-0.5.0-1.azl3.$(uname -m).rpm
cargo install --git https://github.com/fede2cr/oxidizr --branch azurelinux
sudo .cargo/bin/oxidizr enable -e coreutils
ls -l $(which ls)
ls --version
```

Once you do that, this is the environment you should have:

```bash
$ sort --version
sort (uutils coreutils) 0.5.0
$ /usr/bin/.sort.oxidizr.bak --version
sort (GNU coreutils) 9.4
```

---
# Benchmarks

Not all tools will have speedups. The ones that call the kernel to do filesystem operations, are still dependent on the speed of the kernel, and still have to wait.*

* Note: There some fancy filesystems that can handle multiple operations, and there are some patches for the filesystem tools comming in. uutils-coreutils is improving by the day, do keep an eye on the project!

## Why are things faster?

GNU coreutils has had decades of patches and development. So why is a newcommer project sudently faster than tools written in C?

- I/O libraries: The I/O libraries that Rust uses, have very efficient asyncronous behaviour and use heaving buffering.
- Easy parallelization: Doing parallel code is extremely easy in Rust, so more projects try taking advantage of this. In the past, parallel was a tool used mostly on high-performance-computers for very heavy number crunching, but today, even microcontrollers have multiple cores. (Even some archs use thousands of cores!)
- Memory safety: Wan't memory safety only a security thingy? Well, so it happens that is also creates zero-cost abstractions, and it also doesn't use garbage collectors (that affect performance and reliability in languages like Python).
- New code: Without legacy, and being a modern and fresh implementation, it does pay to be a re-implementation.

Also, things are always dependent of the workload.

---

# Test environment

Using size Standard_D8als_v6 for amd64 and size Standard_D8ps_v6 for arm64. Always output to /dev/null to take away the writing of disks out of the benchmark.

Let's install hyperfine in azl3:

```bash
rustup update stable
cargo install --locked hyperfine
```

Now, let's download 10 large books from Project Gutenberg:

```bash
mkdir -p gutenberg_books
cd gutenberg_books

# Download 10 large books (plain text UTF-8)
wget -O war_and_peace.txt https://www.gutenberg.org/files/2600/2600-0.txt
wget -O les_miserables.txt https://www.gutenberg.org/files/135/135-0.txt
wget -O moby_dick.txt https://www.gutenberg.org/files/2701/2701-0.txt
wget -O ulysses.txt https://www.gutenberg.org/files/4300/4300-0.txt
wget -O don_quixote.txt https://www.gutenberg.org/files/996/996-0.txt
wget -O david_copperfield.txt https://www.gutenberg.org/files/766/766-0.txt
wget -O anna_karenina.txt https://www.gutenberg.org/files/1399/1399-0.txt
wget -O brothers_karamazov.txt https://www.gutenberg.org/files/28054/28054-0.txt
wget -O middlemarch.txt https://www.gutenberg.org/files/145/145-0.txt
wget -O clarissa.txt https://www.gutenberg.org/files/121/121-0.txt

cat *.txt > all_books.txt

ls -lh (with awk...)
20M all_books.txt
3.2M les_miserables.txt
(...)
```

---

# tr

Translate characters. In this example, turn all uppercase to lowercase.

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.tr.oxidizr.bak A-Z a-z < all_books.txt > /dev/null' \
  'tr A-Z a-z < all_books.txt > /dev/null'
```
---

# sort

Sorts the lines in a file, in alphabetic or numeric order.

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.sort.oxidizr.bak all_books.txt > /dev/null' \
  'sort all_books.txt > /dev/null'
```

---

# wc

Counts "words", but also lines and bytes. In this example, it's doing those 3 counts.

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.wc.oxidizr.bak all_books.txt > /dev/null' \
  'wc all_books.txt > /dev/null'
```

---

# head

Fetches the -n *first* lines, in this example 1000.

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.head.oxidizr.bak -n 1000 all_books.txt > /dev/null' \
  'head -n 1000 all_books.txt > /dev/null'
```

---

# tail

Fetches the -n *last* lines, in this example 1000.

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.tail.oxidizr.bak -n 1000 all_books.txt > /dev/null' \
  'tail -n 1000 all_books.txt > /dev/null'

```

---

# cat

It prints the content of a file as in this example. (It also con*cat*tenates files)

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.cat.oxidizr.bak all_books.txt > /dev/null' \
  'cat all_books.txt > /dev/null'

```

---

# One large example

Not that realistic, but let's use as many of the tools as we can, trying to do as much processing as we can to see how much improvement we will get:

```bash
hyperfine --warmup 2 --runs 20 \
  '/usr/bin/.cat.oxidizr.bak all_books.txt \
   | /usr/bin/.tr.oxidizr.bak A-Z a-z \
   | /usr/bin/.cut.oxidizr.bak -d" " -f1 \
   | /usr/bin/.sort.oxidizr.bak \
   | /usr/bin/.uniq.oxidizr.bak -c \
   | /usr/bin/.shuf.oxidizr.bak \
   | /usr/bin/.head.oxidizr.bak -n 5000 \
   | /usr/bin/.tee.oxidizr.bak sample.txt \
   | /usr/bin/.wc.oxidizr.bak -l \
   > /dev/null' \
  'cat all_books.txt \
   | tr A-Z a-z \
   | cut -d" " -f1 \
   | sort \
   | uniq -c \
   | shuf \
   | head -n 5000 \
   | tee sample.txt \
   | wc -l \
   > /dev/null'
```

---

# Results

```
Benchmark 1: (cmd)
  Time (mean ± σ):      4.257 s ±  0.162 s    [User: 4.801 s, System: 2.269 s]
  Range (min … max):    4.111 s …  4.753 s    20 runs
Benchmark 2: (cmd)
  Time (mean ± σ):      1.474 s ±  0.064 s    [User: 2.093 s, System: 1.129 s]
  Range (min … max):    1.400 s …  1.611 s    20 runs
Summary: cmd1 is 2.89 ± 0.17 times faster than cmd2
```

| Test description | Arch | Speedup |
|:-----------------|------|--------:|
| tr: uppercase to lowercase | amd64 | 1.23 ± 0.13 times faster|
| | arm64 | 1.12 ± 0.03 times faster |
| sort: all lines | amd64 | 1.21 ± 0.06 times faster |
| | arm64 | 1.56 ± 0.08 times faster |
| wc: lines, words, bytes | amd64 | 1.40 ± 0.01 times faster |
| | arm64 | 1.16 ± 0.01 times faster |
| head: first 1000 lines | amd64 | 1.86 ± 0.22 times slower |
| | arm64 | 2.02 ± 0.09 times slower |
| tail: last 1000 lines | amd64 | 2.10 ± 0.10 times slower|
| | arm64 | 1.81 ± 0.13 times slower |
| cat: display entire file | amd64 | 1.04 ± 0.05 times slower |
| Complex example: cat+tr+cut+sort+uniq+shuf+head+wc (Gutenberg books) | amd64 | 3.24 ± 0.23 times faster |
|  | arm64 | 3.36 ± 0.06 times faster |
| Complex example: cat+tr+cut+sort+uniq+shuf+head+wc (Wikipedia 1G) | amd64 | 2.89 ± 0.17 times faster |
|  | arm64 | 3.11 ± 0.02 times faster |
| Complex example: cat+tr+cut+sort+uniq+shuf+head+wc (Wikipedia 10G) | amd64 | 2.96 ± 0.06 times faster |
|  | arm64 | 3.32 ± 0.03 times faster |


---

# Bonus

```
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   Cargo.toml
        modified:   src/uu/tail/src/chunks.rs
        modified:   src/uu/tail/src/follow/files.rs
        modified:   src/uu/tail/src/tail.rs
```

```
Benchmark 1: GNU_tail
  Time (mean ± σ):      10.3 ms ±   0.7 ms    [User: 1.1 ms, System: 9.0 ms]
  Range (min … max):     9.2 ms …  17.2 ms    2000 runs

Benchmark 2: tail_rust
  Time (mean ± σ):       2.1 ms ±   0.7 ms    [User: 1.6 ms, System: 0.4 ms]
  Range (min … max):     1.5 ms …  12.5 ms    2000 runs

Benchmark 3: tail_rust_patch
  Time (mean ± σ):       1.9 ms ±   0.5 ms    [User: 1.5 ms, System: 0.3 ms]
  Range (min … max):     1.5 ms …   7.1 ms    2000 runs

Summary
  tail_rust_patch ran
    1.07 ± 0.47 times faster than tail_rust
    5.37 ± 1.35 times faster than GNU_tail
```
