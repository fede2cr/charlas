---
theme: https://github.com/maaslalani/slides/raw/main/styles/theme.json
author: alvarof@microsoft.com
date: 2025-07-24
---

# Azure Linux Community Call

<br>

<br>

<br>

<br>

## Topics:

- sudo and su in Rust
<br>
- oxidizr for multidistribution
<br>
- Azurelinux for Raspberry Pi
<br>
- Azurelinux LiveCD


<br>

<br>

<br>

### By Álvaro Figueroa, Azure Linux Escalation team, from a cloud forest in Costa Rica

---
# sudo and su in Rust

In the last meeting we saw how to use Coreutils written in rust, in Azurelinux.

It's part of a project to "oxidize" (add rust to) Ubuntu 25.10 [with coreutils first](https://discourse.ubuntu.com/t/migration-to-rust-coreutils-in-25-10/59708), and [sudo+su](https://discourse.ubuntu.com/t/migration-to-rust-coreutils-in-25-10/59708) just a few days later.

## Let's talk a bit about sudo

Not all Unix-type systems use sudo. As an example, FreeBSD uses a tool called ```doas```, and sudo is only an option for compatiblity. This is because "regular" sudo is a huge tool. Did you know it has an *insult* mode?

```
Defaults: insults
```

With coreutils, both speed and security are mayor features. With sudo and su, security will be our focus.

Recently, "normal" sudo had 2 huge security issues: CVE-2025-32462 (score: 9.3/10) and CVE-2025-32463 (2.8/10), for features that might not be needed for most users.  

*Important*: sudo-rs is not magically safe software. In 2025 it has CVE-2025-46718 (score 3.3/10).


---
# sudo and su in Rust

## Let's talk a bit about sudo

sudo-rs is a reimplementation of sudo, that provides the commands ```sudo```, ```su``` and ```visudo```.

In contrast to Coreutils in rust, that is design to look and work exactly like GNU Coreutils, sudo-rs is similar enough for using in production, but it doesn't have all of the rare and weird features that sudo has for no reason.

So, sudoers and sudoers.d/ should work well enough. But remember, we are here to do an experiment! We are only going to know how does it work with "your" config files, until we test them.

Testing all of the Azure extensions that use sudo in one way or another, should keep us entretained for a bit.

Start integrating into CI/CD (like GitHub actions) testing as soon as possible.

---

# sudo and su in Rust

[GitHub repo](https://github.com/fede2cr/azurelinux-rust-coreutils)

## Howto

Just like with coreutils, we will use the oxidizr tool to test sudo-rs as an "experiment". This means that we don't replace the sudo+su package (yet?), we just use oxidizr to change the binaries so that we can test how a system will behave with sudo and su written in rust.

```bash
sudo tdnf -y update
sudo tdnf -y install cargo
sudo tdnf -y install https://github.com/fede2cr/azurelinux-sudo-rs/releases/download/v0.2.6-2/sudo-rs-0.2.6-2.azl3.$(uname -m).rpm
cargo install --git https://github.com/fede2cr/oxidizr --branch azurelinux
sudo .cargo/bin/oxidizr enable -e sudo-rs
ls -l $(which sudo)
sudo --version
sudo ls
```

If you find an issue with the new version, you can ask oxidizr to *undo* the experiment and leave the system as it was.
```bash
sudo .cargo/bin/oxidizr disable -e sudo-rs
```

---
# oxidizr for multidistribution

Oxidizr started as an Ubuntu only tool. Then, I came and ruined it by doing some amateurish s/apt-get/tdnf/ to make it work in Azurelinux.

When I adapted it to work with sudo-rs as well, I had to refactor the code. This allowed me to re-factor the code, to make it work in multiple distributions.

For now, just the code for Fedora is there, but the data structures make it easy to add other distros later on.

I will send the current code on a Pull Request, in a hope that the developers that started with an Ubuntu-only tool see the value of other distributions testing coreutils and sudo versions in rust. The more testing, the more hope we can have that the 25.10 oxidation will happen. This is the only chance they have before 26.04. If it doesn't work, they will have to wait to 2028!

You can find the [branch with the code, here](https://github.com/fede2cr/oxidizr/tree/azurelinux)

---
# Azurelinux for Raspberry Pi

In an earlier AZL Community *public* call, a user asked about running Azurelinux on a Raspberry Pi. The more people we have using this amazing distro, the stronger community we will have. A distribution is not a collection of packages, but the community that is behind them.

*Warning*: This project was created with AI cooperation!

I started doing the manual steps to merge the Azurelinux 3.0 for aarch64 distro, with the boot loader, kernel and firmware from RaspiOS. And after every succesfull command, I asked Copilot in Visual Studio Code's chat to integrate the commands into a Python script that would rebuild the distro-merge in a repeatable way.

It's important to create a distinction. I didn't ask Copilot to "merge the distros" and just stared at the screen, but I gave very detailed instructions. Let's think of this as a smart copy paste from my terminal to the script. Working this way, I only had to do very tiny adjusments in the code.

---
# Azurelinux for Raspberry Pi

The merge is happening in GitHub action by using a local runner (cross compiler won't work here, and qemu emulation is very slow). If GitHub offered native aarch64, it would be easier to rebuild. For now, I have to turn on my local runner every time I need to create a new image. Yet, the code to rebuild is quite simple.

Please test it and let me know what I should add to it.

TODO:
- Wifi
- Testing in Pi5, CM or Zero
- Serial console
- Lots of minor things (boot mount, firstboot, etc)

Please download, test, and add issues [here](https://github.com/fede2cr/azurelinux-pi)

---
# Azurelinux LiveCD


So, we can test Azurelinux on a Raspberry Pi, by creating VMs in Azure using ```az cli```, or by using WSL. Where else?

This one day project is using the AZL build system to create a LiveCD. Now you can also test Azurelinux in a hypervisor like KVM or Hyper-V, without having to complete an install process. Just point it to the ISO, boot, and that's it!

It looks like a one-file-project, but most of the fun is in the CI/CD that released the ISO.

Other steps:
- As installer for AZL4?
- Aarch64 ISO (no idea how to test it)

Take a peek or download the [ISO from here](https://github.com/fede2cr/azl-livecd)
