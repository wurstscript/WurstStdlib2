[![Build Status](http://peeeq.de/hudson/job/StdLib2/badge/icon)](http://peeeq.de/hudson/job/StdLib2/) 
# StdLib2
Revamped version of the WurstScript Standard Library. Provides core packages for basic mapping needs as well as advanced math and system packages for advanced users.

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

The Stdlib provides natives as well as presets to easily generate wc3 object data such as units, abilities, buffs, etc.




