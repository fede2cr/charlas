---
theme: https://github.com/maaslalani/slides/raw/main/styles/theme.json
author: alvaro.figueroa@microsoft.com
date: 2026-05-28
---

# Azure Linux Community Call

<br>

<br>

# Is Azure Linux 4 PQC?

<br>

<br>

## Topics:

- What is PQC and what is 'hybrid'?
<br>
- How is AZL4 ready for it?
<br>
- PQC ssh
<br>
- PQC web (nginx)
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

# What is PQC? 

PQC is Post-quantum cryptography. Some (not all!) of the current crypto algorithms, are based in the complexity of factorization: Keys are the result of multiplication of large prime numbers which are kept secret.

Quantum computer allow using an algorithm created by Peter Shor in 1994, that **in theory** can find out these prime numbers (factorization), in minutes, so they won't be secret any more.

In a classical computer, this can also be done, but it will take more time than the lifetime of the Sun; so let's not even try.

Lots of governments now have policies that recommend that software (like Operating systems) has to be ready, so that they can use PQC alternatives, **in hybrid modes**.

**Important**: Not all cryto algos are based on the complexity of factorization. A quick example would be SHA for doing hash (for verification of file or network packets) that uses very simple operations (bit rotations, ANDs, ORs, XORs) but on complex sequences that cannot be solved by Shor's. AES for encryption, is also mature and PQC.

# What is 'hybrid'?

For the algorithms that we need to replace, we are thinking about the future/present (more on this later), but today they are considered safe from any attack that can be executed in the present. 

But some of the newer stuff, like key-exchange using PQC methods, are very new. This, in cryptography is something to be taken with extreme care, as being new implementations they haven't hold through time for long enough to be considered mature. Lots of effort has been put into validating and auditing the software implementations, but during NIST competitions, some of the new algorithms were broken quite easily.

---

# How is AZL4 ready for PQC? 

A library called Open Quantum Safe (OQS) has been integrated into recent versions of OpenSSL. AZL4 has such a recent version, and **most** of the server applications have been modified by upstream to include PQC capabilities.

## Is that all?

By just using AZL4, is that all? Am I safe?

You need to review your company's practices on key management, encryption, Certificate Authorities, an many more. AZL4 is the tool to get you safe, but security is both about **compliance and tools**.

## By which date do I need to be ready?

Don't know, but start now.

## Is it complicated?

Not really. As complicated as validating that a web server is running TLS 1.3.

## Are there any terminology required for this mini-talk?

- ML-KEM: Module-Lattice Key Encapsulation Mechanism (also know as **Kyber**. NIST 2024, FIPS 203)
- ECDH: Elliptic Curve Diffie-Hellman, for working with public+private key pairs. Non PQC.
- X25519: The function defined by Curve25519 (by DJB in 2005, used by OpenSSH since 2013)

---

# PQC ssh

The OpenSSH in newer versions, is not printing this warning on every connection, I hope you have noticed!


```bash
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
```

**Note:** You can also modify system-wide, by using ``update-crypto-policies```

## On the client

```bash
ssh -Q kex | grep mlk
```

## On the server

```bash
echo "KexAlgorithms mlkem768x25519-sha256" | sudo tee /etc/ssh/sshd_config.d/99-PQC-test.conf
sudo sshd -t
sudo systemctl reload sshd
```

## How to validate

From the client:
```bash
ssh -v user@server
```
Look for:
```bash
debug1: kex: algorithm: mlkem768x25519-sha256
```

Also, no warning from the recent openssh client.

---

# PQC nginx

## On the client

Nothing, your web browser should be PCQ ready since aprox last year.

## On the server

Visit [Mozilla SSL Generator](https://ssl-config.mozilla.org/) web page.

```bash
sudo nginx -t
sudo systemctl reload nginx 
```

## How to validate

```bash
openssl s_client -connect web-server:443
```
Look for:

```bash
Negotiated TLS1.3 group: X25519MLKEM768
```

