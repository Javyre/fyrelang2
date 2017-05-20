# Fyrelang2
This is a language written in python in my free time at school in about two weeks...

# Usage

Because I am developing this on my iPad, the `.py` extension is necessary for the Pythonista app to recognize it.

```shell
./lang.py <program.fyr>
```



# Example code

## Number guessing game using registers
```
# We use registers because they share the same
# scope as the rest of the script.
# Functions have their own memory object.

from = 0
to = 20
randnum = random_randint[from to]

(
    guess = input["guess: "]
    numguesses = numguesses + 1
) reg doguess;

echo["Guess a number between "from" to "to]

@doguess do numguesses <- 0;

(
    echo["wrong!"]

    # give hint
    (echo["number is "adj" than "guess]) reg hint;
    (@hint do adj <- "greater";) if randnum > guess $$num;
    (@hint do adj <- "smaller";) ifnot;

    @doguess do;
) loop while guess $$num != randnum;

echo["right!"]
echo["You have guessed the number in "numguesses" guesses!"]
```
