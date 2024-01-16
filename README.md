# pylox
lox library in python from crafting interpreters book

To fire it up:
```
$python lox.py 
> var a = 69;
> print a;
69.0
```

## Variables
Data-Types: numbers(floats), strings, booleans(`true` and `false`) and `nil`
```
> var a = 69;
> var b = 420;
> print a + b;
489.0
> var c = "Hello There";
> var d = "General Kenobi!";
> print c;
Hello There 
> var prequel = c + ". " + d;
> print prequel;
Hello There. General Kenobi!
> var e = true;
print e;
True 
> var f = nil;
> print f;
nil
```

## Control Flow
```
var age = 21;

if (age >= 18) {
    print "Adult";
  }
  else {
      print "Child";
    }
```

## Loops
```
var c = 21;
while (c > 0) {
    print c;
    c = c - 1;
  }

for (var i = 21; i > 0; i = i - 1) {
    print i;
  }
```

## Functions
```
fun square(a) {
    print a * a;
  }

square(6); // 36.0
```

## Classes
```
class Rectangle {
    area(a, b) {
        print a * b;
      }

    perimeter(a, b) {
        print 2 * (a + b);
      }
  }

Rectangle().area(2, 3);      // 6.0
Rectangle().perimeter(2, 3); // 10.0

class Square < Rectangle {
    area(a) {
        print a * a;
      }

    perimeter(a) {
        print 4 * a;
      }
  }

Square().area(3);      // 9.0
Square().perimeter(3); // 12.0
```
