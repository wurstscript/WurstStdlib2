![](https://i.imgur.com/L3xfAs4.png) [![Build Status](https://travis-ci.org/wurstscript/WurstStdlib2.svg?branch=master)](https://travis-ci.org/wurstscript/WurstStdlib2)
# Wurst Standard Library

This is the repository of the WurstScript standard library which provides a vast amount of useful packages to users starting out with Wurst.
Many commonly used data structures, wc3 specific utility packages, Object Editing as well as extension wrappers for the blizzard natives have been implemented, are unit tested and therefore ready to use in production immediately.

# Motivation

Wurst aims to provide a better "out of the box" experience when it comes to warcraft III modding. Since Jass is very limited, one has to implement very basic data structures like Lists or warcraft specific functionality like damage detection themselves. Before Wurst these resources had to be gathered from modding forums across the web. These public resources are often untested, interdependent on other resources and incompatible with other code.

By introducing up a standard library, we offer the user everything they need to focus on creating content, rather than implementing fundamentals in order to get started. The standard library frameworks tries to be lightweight and unintrusive, while still configurable. The streamlined API allows external packages to share code and work independently. 

# Contributing

The standard library has greatly flourished due to amazing feedback, pull requests and issue reports. Bugs and anomalies have been fixed and documented. Thus we highly appreciate any PR with fixes or improvements. However a few points of advice:
- Please keep PRs as small as possible to allow for easier review and faster merging
- Anything that can be unit tested, should be unit tested.
- We expect your code to adhere to the existing conventions

If further natives need to be implemented for compiletime, they can be requested via a ticket.

Feel free to join our [irc channel](https://webchat.quakenet.org/?channels=#inwc.de-maps) if you would like to contribute.

# Usage Notes

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

The Stdlib provides natives as well as presets to easily generate wc3 object data such as units, abilities, buffs, as well as constants for all asset paths.




