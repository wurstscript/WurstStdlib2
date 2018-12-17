![](https://i.imgur.com/L3xfAs4.png) [![Build Status](https://travis-ci.org/wurstscript/WurstStdlib2.svg?branch=master)](https://travis-ci.org/wurstscript/WurstStdlib2)
# Wurst Standard Library

This is the repository of the WurstScript standard library which provides a vast amount of useful packages to users starting out with Wurst.
Many commonly used data structures, wc3 specific utility packages, Object Editing as well as extension wrappers for the blizzard natives have been implemented, are unit tested and therefore ready to use in production immediately.

# Motivation

Wurst aims to provide a better "out of the box" experience when it comes to warcraft III modding. Since Jass is very limited, developers have to implement basic data structures, like Lists, or Warcraft specific functionality, like damage detection, themselves. Before Wurst these resources had to be gathered and copied manually from modding forums across the web. Public code resources in forums threads are not only hard to maintain and keep up to date, but also often untested, interdependent on other resources and incompatible with other code.

By introducing a standard library, we offer the developers everything they need to start focusing on creating content, rather than implementing basics to even get started. The frameworks provided by the standard library try to be lightweight and unintrusive, while still configurable for your needs. The streamlined API allows external packages to share code and work independently. 

# Contributing

[View CONTRIBUTING.md](https://github.com/wurstscript/WurstStdlib2/blob/master/CONTRIBUTING.md)

# Usage Notes

Documentation: https://wurstlang.org/stdlib

## Linked Lists

### The Linked List Module

If you encounter the case that you always want to iterate over all instances of a class, creating LinkedList objects and storing the instances in it is unnecessary overhead.

```python
# bad
LinkedList<A> list
class A
  construct()
    list.add(this)
    
...
for a in list

```

Instead the class itself can act as a linked list, so that each instance knows it's next and previous neighbour.

```python
# better, but still allocating iterators
class A
  use LinkedListModule
    
...
for a in A

```

### Efficiently Iterating LinkedLists

If you have a for each loop over a list like so:

```python
LinkedList<X> list
for elem in list 
```

Then wurst will create and destroy an iterator object each time you execute the loop.

If you know that your loop is not nested, you can use the static iterator instead and save the overhead.

```python
# better, but limited
LinkedList<X> list
for elem from list.staticItr()
```

**Note** that it has to be a for .. *from* loop now.

## Object Editing



