# Aurora

Aurora - Erlang and Rust crossbreeded language

## Overview

Aurora is a programming language that combines the concurrency model of Erlang with the performance and safety features of Rust. It is designed to facilitate the development of highly concurrent, fault-tolerant, and efficient applications.

## Features

- **Actors and Supervisors**: Inspired by Erlang's actor model, Aurora provides built-in support for actors and supervisors, making it easy to build concurrent and fault-tolerant systems.
- **Strong Typing**: Aurora uses a strong, static type system similar to Rust, ensuring type safety and reducing runtime errors.
- **Memory Safety**: Aurora incorporates Rust's ownership model to ensure memory safety without a garbage collector.
- **Pattern Matching**: Aurora supports pattern matching, allowing for expressive and concise code.

## Example

Here is a simple example of Aurora code:

```aur
actor Counter {
    let count: Int = 0;

    func increment() -> Int {
        count += 1;
        return count;
    }

    on unknown(msg) {
        log("Unhandled message: " + msg);
    }
}

supervisor CounterSupervisor {
    var counter: Actor<Counter>;

    func start() {
        counter = spawn(Counter);
    }

    on error(actor, err) {
        log("Error in " + actor + ": " + err);
        restart(actor);
    }
}

func main() {
    let supervisor = spawn(CounterSupervisor);
    supervisor.send(message: { actor in actor.increment() });
}
