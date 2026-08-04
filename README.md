![](https://i.imgur.com/L3xfAs4.png)

[![Build](https://github.com/wurstscript/WurstStdlib2/actions/workflows/build.yml/badge.svg)](https://github.com/wurstscript/WurstStdlib2/actions/workflows/build.yml)
# Wurst Standard Library

This is the repository of the WurstScript standard library. It provides commonly used data structures, math and string utilities, Warcraft III native wrappers, and reusable WC3 systems for maps.

The repository also contains opt-in object-editing APIs and generated Warcraft III asset catalogs. These map game data into Wurst so map authors can use typed constants instead of raw IDs and paths.

Packages are unit tested and intended to be usable in production. Tests live in dedicated `*Tests` packages so production packages contain only their runtime and compiletime APIs.

# Motivation

Wurst aims to provide a better "out of the box" experience when it comes to warcraft III modding. Since Jass is very limited, developers have to implement basic data structures, like Lists, or Warcraft specific functionality, like damage detection, themselves. Before Wurst these resources had to be gathered and copied manually from modding forums across the web. Public code resources in forums threads are not only hard to maintain and keep up to date, but also often untested, interdependent on other resources and incompatible with other code.

By introducing a standard library, we offer the developers everything they need to start focusing on creating content, rather than implementing basics to even get started. The frameworks provided by the standard library try to be lightweight and unintrusive, while still configurable for your needs. The streamlined API allows external packages to share code and work independently. 

# Contributing

[View CONTRIBUTING.md](https://github.com/wurstscript/WurstStdlib2/blob/master/CONTRIBUTING.md)

# Documentation

https://wurstlang.org/stdlib


