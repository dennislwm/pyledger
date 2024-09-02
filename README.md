# pyledger

<h1 align="center" style="border-bottom: none;">pyledger</h1>
<h3 align="center">A CLI application to automate debit and credit transactions for Ledger, a double-entry accounting system.</h3>
<br />
<p align="center">
  <p align="center">
    <a href="https://github.com/dennislwm/pyledger/issues/new?template=bug_report.yml">Bug report</a>
    ·
    <a href="https://github.com/dennislwm/pyledger/issues/new?template=feature_request.yml">Feature request</a>
    ·
    <a href="https://github.com/dennislwm/pyledger/wiki">Read Docs</a>
  </p>
</p>
<br />

---

![GitHub repo size](https://img.shields.io/github/repo-size/dennislwm/pyledger?style=plastic)
![GitHub language count](https://img.shields.io/github/languages/count/dennislwm/pyledger?style=plastic)
![GitHub top language](https://img.shields.io/github/languages/top/dennislwm/pyledger?style=plastic)
![GitHub last commit](https://img.shields.io/github/last-commit/dennislwm/pyledger?color=red&style=plastic)
![Visitors count](https://hits.sh/github.com/dennislwm/pyledger/hits.svg)
![GitHub stars](https://img.shields.io/github/stars/dennislwm/pyledger?style=social)
![GitHub forks](https://img.shields.io/github/forks/dennislwm/pyledger?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/dennislwm/pyledger?style=social)
![GitHub followers](https://img.shields.io/github/followers/dennislwm?style=social)

## Purpose

This document describes the `pyledger` CLI application to automate debit and credit transactions for [Ledger](https://github.com/ledger/ledger), a double-entry accounting system.

## Audience

The audience for this document includes:

* Developer who will develop the application, run unit tests, configure build tools and write user documentation.

* DevSecOps Engineer who will shape the workflow, and write playbooks and runbooks.

## Why `pyledger`?

1. Currently, creating a Ledger input requires the User to enter a debit and credit record for each transaction, which may be inefficient and error prone.

2. The `pyledger` allows the User to create a rules file that will govern the transformation process of an input file to an output file, hence reducing the error rate, while increasing the reusability and adding version control for a configuration as code.

3. The rules will be evaluated in order of sequence, i.e. the first rule has higher precedence over the other rules, etc.

## Getting Started 🚀

We have a thorough guide on how to set up and get started with `pyledger` in our [documentation](https://github.com/dennislwm/pyledger/wiki).

## Bugs or Requests 🐛

If you encounter any problems feel free to open an [issue](https://github.com/dennislwm/pyledger/issues/new?template=bug_report.yml). If you feel the project is missing a feature, please raise a [ticket](https://github.com/dennislwm/pyledger/issues/new?template=feature_request.yml) on GitHub and I'll look into it. Pull requests are also welcome.

## 📫 How to reach me
<p>
<a href="https://www.linkedin.com/in/dennislwm"><img src="https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin&labelColor=blue" height=25></a>
<a href="https://twitter.com/hypowork"><img src="https://img.shields.io/badge/twitter-%231DA1F2.svg?&style=for-the-badge&logo=twitter&logoColor=white" height=25></a>
<a href="https://leetradetitan.medium.com"><img src="https://img.shields.io/badge/medium-%2312100E.svg?&style=for-the-badge&logo=medium&logoColor=white" height=25></a>
<a href="https://dev.to/dennislwm"><img src="https://img.shields.io/badge/DEV.TO-%230A0A0A.svg?&style=for-the-badge&logo=dev-dot-to&logoColor=white" height=25></a>
<a href="https://www.youtube.com/user/dennisleewm"><img src="https://img.shields.io/badge/-YouTube-red?&style=for-the-badge&logo=youtube&logoColor=white" height=25></a>
</p>
<p>
<span class="badge-buymeacoffee"><a href="https://ko-fi.com/dennislwm" title="Donate to this project using Buy Me A Coffee"><img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg" alt="Buy Me A Coffee donate button" /></a></span>
<span class="badge-patreon"><a href="https://patreon.com/dennislwm" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
<span class="badge-newsletter"><a href="https://buttondown.email/dennislwm" title="Subscribe to Newsletter"><img src="https://img.shields.io/badge/newsletter-subscribe-blue.svg" alt="Subscribe Dennis Lee's Newsletter" /></a></span>
