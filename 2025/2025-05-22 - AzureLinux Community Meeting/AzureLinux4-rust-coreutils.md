%title: Rust coreutils for AzureLinux
%author: alvaro.figueroa@microsoft.com
%date: 2025-05-22

-> Agenda <-
=========

-> Rust coreutils for AzureLinux <-

-> _Wait, is there something wrong with coreutils?_ <-

<br>
* What are coreutils?
<br>
* Why for AzureLinux?
<br>
* Why in Rust?
<br>
* Howto
<br>
    * oxidizr (for AzureLinux)
<br>
    * rust-coreutils RPM
<br>
    * Benchmark software
<br>
* Any reason why not to do it?
<br>
* Next steps

-------------------------------------------------

-> # $ whoami <-

* Álvaro Figueroa, from a cloud forest in Costa Rica.
<br>
* Azure Linux Escalation Team (CSS)
<br>
* Worked on multiple Linux distributions, a bit with kernel, a bit with filesystems
<br>
* Have to many hobbies (help?)
<br>
* Linux+OSS Champ, Love hackathons. Happy to help. Love doing collabs, specially when there is overlap with my hobbies. Put me to work, really.

-------------------------------------------------

-> # What are coreutils? <-

112 tools, for example:

* Filesystem tools
ls, chmod, chown, cp, dd, ln
<br>

* Text tools
cat, join, nl, sort, uniq, tee
<br>

* Unix programming tools
seq, sleep, pwd, wc
<br>

* Unix tools
id, uname, who, tty, sha512sum, nice

-------------------------------------------------

-> # Why AzureLinux? <-

In an internal talk, the suggestion was made to the AzureLinux developers to include it in the roadmap for AzureLinux 4, with rust coreutils as default.

This will continue the modernization process of the distro, plus the Rust advantages (next slide).

The GNU coreutils package is not discarded, but included as an optional package.

For AzureLinux 3 users, the process has been simplified and its now very easy to test this. Even if you don't switch to rust coreutils as default, there are important advantages.

-------------------------------------------------

-> # Why in rust? <-

4 main advantages:

<br>
* The Rust community is amazing. Microsoft has also made great contributions to both the Rust Language, and the Rust Foundation.
<br>
* It has memory safety and thread safety by default ("ownership model"), and this will help with a particular set of security issues.
    * [NIST recommendation](https://www.nist.gov/itl/ssd/software-quality-group/safer-languages)
    * [OpenSSF recommendation](https://memorysafety.openssf.org/memory-safety-continuum/) Microsoft has a heavy hand on this recommendation, as we contribute to OpenSSF.
<br>
* It's really fast. For many reasons. (Aggressive compiler optimizations, inline assembly, ownership system allows for multicore performance, no garbage collection, how abstractions are managed)
    * Don't believe me. Benchmark it!
<br>
* VM/Container size, rust-coreutils is much smaller than GNU Coreutils, so it would make containers way smaller.

-------------------------------------------------

-> # Howto: oxidizr <-

Canonical shared the [idea with the community](https://discourse.ubuntu.com/t/migration-to-rust-coreutils-in-25-10/59708) about replacing GNU Coreutils in Ubuntu 25.10 (next dev release).

In order for users to test it, instead of having two distributions, a tool called Oxidizr. It moves the GNU Coreutils commands out of the way and creates the soft links for the rust Coreutils commands.

It works in "experiments", and you can enabled them and disable them. No need to add/remove packages, no need to reboot.

The original version is for Ubuntu, so I did a [quick and dirty patch](https://github.com/fede2cr/oxidizr) so that it works in AzureLinux. Mostly a s/apt/tdnf/g :þ

**Important**: You don't need to run oxidizr, or to change all of the coreutils to test it. Both GNU and rust coreutils can co-exist, and you can change a particular script to use the **sort** tool from rust-coreutils to get better perfomance.

-------------------------------------------------

-> # Howto: rust-coreutils RPM <-

I have made an AzureLinux 3 [RPM Package](https://github.com/fede2cr/azurelinux-rust-coreutils/) for version 0.0.30 of rust-coreutils.

```
sudo tdnf -y update
sudo tdnf -y install cargo lsb-release
sudo tdnf -y install https://github.com/fede2cr/azurelinux-rust-coreutils/releases/download/v0.0.30-azl2/rust-coreutils-0.0.30-1.azl3.$(uname -m).rpm
cargo install --git https://github.com/fede2cr/oxidizr --branch azurelinux
sudo .cargo/bin/oxidizr enable -e coreutils
ls -l $(which ls)
ls --version
```


-------------------------------------------------

-> # Benchmark software <-

So, is it faster?
<br>
Filesystem tools ask the kernel to do things, so maybe there would be little difference.
<br>
With text processing there is a *huge speedup*. Download Moby Dick in txt from the Guttenberg project, and try to sort it. What about an SHA512 hash? How about tac (reverse cat)?

A perfect tool for this type of benchmarks, is [hyperfine](https://github.com/sharkdp/hyperfine). You specify the two commands to compare, a warmup if needed.

```
hyperfine --warmup 10 '/usr/bin/.sort.oxidizr.bak moby.txt' 'sort moby.txt'
```

-------------------------------------------------

-> ## Any reason why not to do it? <-

<br>
* Don't do this in production, always experiment and verify.
<br>
* It's possible the AzureLinux team won't support this (yet?).
<br>
* If we find any bugs, we report them upstream.
<br>
* The license is not GPL, but MIT. Is this a reason against?

-------------------------------------------------

-> # Next steps <-

Things are going up to plan for Ubuntu 25.10 about rust-coreutils, that they have now [shared plans for sudo-rs](https://discourse.ubuntu.com/t/adopting-sudo-rs-by-default-in-ubuntu-25-10/60583): a compatible sudo written in Rust! How important it would be to have the same security benefits on a tool such as sudo.

In a similar way to rust-coreutils and oxidizr, I also have a SPEC file for sudo-rs, and it seems to work nicely. See you in the next community meeting?

<br>

[Findutils](https://github.com/uutils/findutils) (find, locate, updatedb and xargs) would be nice as well. Oxidizr already support this experiment, so only the SPEC and lots of testing is needed.
<br>

[Diffutils](https://github.com/uutils/diffutils) (diff, cmp, diff3, sdiff). Same.
<br>

There is also [Sequoia PGP](https://sequoia-pgp.org/) as a Rust version of PGP/GPG, that is being integrated into package managers, another critical infrastructure that benefits from Rust.
