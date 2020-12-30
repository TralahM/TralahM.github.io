---
title: Acceptance Testing FYI
toc_sticky: true
categories: technology test-driven-development programming software
tags: tdd testing software technology clean-code
excerpt: "One of the most common ambiguities we face as software professionals is the ambiguity of “done”."
---

# ACCEPTANCE TESTS
The term acceptance test is overloaded and overused.
Some folks assume that these are the tests that users execute before they accept a release.
Other folks think these are QA tests.
In this post we will define acceptance tests as tests written by a collaboration of the stakeholders and the programmers in order to define when a requirement is done.

## The Definition of "Done"

One of the most common ambiguities we face as software professionals is the ambiguity of “done”.

When a developer says he’s done with a task, what does that mean?
Is the developer done in the sense that he’s ready to deploy the feature with full confidence?
Or does he mean that he’s ready for QA?
Or perhaps he’s done writing it and has gotten it to run once but hasn’t really tested it yet.

Professional developers have a single definition of done: Done means done.
Done means all code written, all tests pass, QA and the stakeholders have accepted.
Done.


But how can you get this level of done-ness and still make quick progress from iteration to iteration? You create a set of automated tests that, when they pass, meet all of the above criteria! When the acceptance tests for your feature pass, you are done.

Professional developers drive the definition of their requirements all the way to automated acceptance tests.
They work with stakeholder’s and QA to ensure that these automated tests are a complete specification of done.


## Communication
The purpose of acceptance tests is communication, clarity, and precision.
By agreeing to them, the developers, stakeholders, and testers all understand what the plan for the system behavior is.
Achieving this kind of clarity is the responsibility of all parties.
Professional developers make it their responsibility to work with stakeholders and testers to ensure that all parties know what is about to be built.

## Automation
Acceptance tests should always be automated.
There is a place for manual testing elsewhere in the software lifecycle, but these kinds of tests should never be manual.
The reason is simple: cost.


The cost of automating acceptance tests is so small in comparison to the cost of executing manual test plans that it makes no economic sense to write scripts for humans to execute.
Professional developers take responsibility for their part in ensuring that acceptance tests are automated.

These tests will prevent you from implementing the wrong system and will allow you to know when you are done.


## Who writes acceptance tests

In an ideal world, the stakeholders and QA would collaborate to write these tests, and developers would review them for consistency.
In the real world, stakeholders seldom have the time or inclination to dive into the required level of detail.
So they often delegate the responsibility to business analysts, QA, or even developers.
If it turns out that developers must write these tests, then take care that the developer who writes the test is not the same as the developer who implements the tested feature.

Typically business analysts write the “happy path” versions of the tests, because those tests describe the features that have business value.
QA typically writes the “unhappy path” tests, the boundary conditions, exceptions, and corner cases.
This is because QA’s job is to help think about what can go wrong.




Following the principle of “late precision,” acceptance tests should be written as late as possible, typically a few days before the feature is implemented.
In Agile projects, the tests are written after the features have been selected for the next Iteration or Sprint.


## The Developer's Role
Implementation work on a feature begins when the acceptance tests for that feature are ready.
The developers execute the acceptance tests for the new feature and see how they fail.
Then they work to connect the acceptance test to the system, and then start making the test pass by implementing the desired feature.



As a professional developer, it is your job to negotiate with the test author for a better test.
What you should never do is take the passive-aggressive option and say to yourself, “Well, that’s what the test says, so that’s what I’m going to do.”

Remember, as a professional it is your job to help your team create the best software they can.
That means that everybody needs to watch out for errors and slip-ups, and work together to correct them.


## Conclusion
The only way I know of to effectively eliminate communication errors between programmers and stakeholders is to write automated acceptance tests.
These tests are so formal that they execute.
They are completely unambiguous, and they cannot get out of sync with the application.
They are the perfect requirements document.


# Testing strategies

## Unit Tests 100%

At the bottom of the pyramid are the unit tests.
These tests are written by programmers, for programmers, in the programming language of the system.

The intent of these tests is to specify the system at the lowest level.
Developers write these tests before writing production code as a way to specify what they are about to write.
They are executed as part of Continuous Integration to ensure that the intent of the programmers’ is upheld.

## Component Tests 50%
These are some of the acceptance tests mentioned in the previous chapter.
Generally they are written against individual components of the system.
The components of the system encapsulate the business rules, so the tests for those components are the acceptance tests for those business rules.

## Integration Tests 20%
These tests only have meaning for larger systems that have many components.
These tests assemble groups of components and test how well they communicate with each other.
The other components of the system are decoupled as usual with appropriate mocks and test-doubles.
Integration tests are choreography tests.
They do not test business rules. Rather, they test how well the assembly of components dances together.
They are plumbing tests that make sure that the components are properly connected and can clearly communicate with each other.

## System Tests  10%
These are automated tests that execute against the entire integrated system.
They are the ultimate integration tests.
They do not test business rules directly.
Rather, they test that the system has been wired together correctly and its parts interoperate according to plan.
We would expect to see throughput and performance tests in this suite.

## Exploratory Tests  5%
This is where humans put their hands on the keyboards and their eyes on the screens.
These tests are not automated, nor are they scripted.
The intent of these tests is to explore the system for unexpected behaviors while confirming expected behaviors.
Toward that end we need human brains, with human creativity, working to investigate and explore the system.
Creating a written test plan for this kind of testing defeats the purpose.
