Andrea Bizzotto
Widget-Async-Bloc-Service: A Practical Architecture for Flutter Apps
Posted by Andrea Bizzotto on May 21, 2019
Difficulty level: Intermediate/advanced. All opinions are my own.

Introduction
State management is a hot topic in Flutter right now.

Over the last year, various state management techniques were proposed.

The Flutter team and community have not (yet) settled on a single "go-to" solution.

This makes sense, because different apps have different requirements. And choosing the most appropriate technique depends on what we're trying to build.

Truth be told, some state management techniques have proven very popular.

Scoped Model is known for its simplicity.
BLoCs are also widely used, and they work well with Streams and RxDart for more complex apps.
Most recently at Google I/O, the Flutter team showed us how to use the Provider package and ChangeNotifier to propagate state changes across widgets.
Having multiple choices can be a good thing.

But it can also be confusing. And choosing a technique that will work and scale well as our apps grow is important.

What's more, making the right choice early on can save us a lot of time and effort.

My take on state management and app architecture
Over the last year I've been building a lot of Flutter apps, big and small.

During this time, I have encountered and solved many problems.

And I have learned that there is no silver bullet for state management.

However, after building things and taking them apart over and over, I have fine-tuned a technique that works well in all my projects.

So in this article I introduce a new architectural pattern that I have defined by:

borrowing a lot of ideas from existing patterns
tweaking them to suit the needs of real-world Flutter apps
Before we see what this pattern looks like, let me define some goals.

This pattern should:

Be easy to understand, once the fundamental building blocks are clear
Be easy to replicate when adding new features
Build upon clean architecture principles
Work well when writing reactive Flutter apps
Require little or no boilerplate code
Lead to testable code
Lead to portable code
Favour small, composable widgets and classes
Integrate easily with asynchronous APIs (Futures and Streams)
Scale well with apps that increase in size and complexity
Out of the existing state management techniques for Flutter, this pattern builds most heavily on BLoCs, and is quite similar to the RxVMS architecture.

Without further ado, I am pleased to introduce:

The Widget-Async-BLoC-Service Pattern
Shorthand: WABS (which is cool because it contains my initials :D)

This architectural pattern comes in four variants.

Widget-Bloc-Service



Widget-Service



Widget-Bloc



Widget only



NOTE: aside from the Widget item, the BLoC and Service items are both optional.

In other words: you can use or omit them as appropriate on a case-by-case basis.

Now, let's explore the full implementation with a more detailed diagram:



First of all, this diagram defines three application layers:

The UI layer: this is always necessary as it is where our widgets live.
The data layer (optional): this is where we add our logic and modify state.
The service layer (optional): this is what we use to communicate to external services.
Next, let's define some rules for what each layer can (and cannot) do.

Rules of play
UI Layer
This is where we put our widgets.

Widgets can be stateless or stateful, but they should not include any explicit state management logic.

An example of explicit state management is the Flutter counter example, where we increment the counter with setState() when the increment button is pressed.

An example of implicit state management is a StatefulWidget that contains a TextField managed by a TextEditingController. In this case we need a StatefulWidget because TextEditingController introduces side effects (I discovered this the hard way), but we are not managing any state explicitly.

Widgets in the UI layer are free to call sync or async methods defined by blocs or services, and can subscribe to streams via StreamBuilder.

Note how the diagram above connects a single widget to both the input and output of the BLoC. But we can use this pattern to connect one widget to the input, and another widget to the output:



In other words, we can implement a producer  consumer data flow.

The WABS pattern encourages us to move any state management logic to the data layer. So let's take a look at it.

Data Layer
In this layer we can define local or global application state, as well as the code to modify it.

This is done with business logic components (BLoCs), a pattern first introduced during DartConf 2018.

BLoC was conceived to separate the business logic from the UI layer, and increase code reuse across multiple platforms.

When using the BLoC pattern, widgets can:

dispatch events to a sink
be notified of state updates via a stream
According to the original definition, we can only communicate with BLoCs via sinks and streams.

While I like this definition, I find it too restrictive in a number of use cases. So in WABS I use a variant of BLoC called Async BLoC.

Just like with BLoCs, we have output stream(s) that can be subscribed to.

However, the BLoC input(s) can include a synchronous sink, an asynchronous method, or both.

In other words, we go from this:



to this:



The asyncrhonous method(s) can:

Add zero, one or more values to the input sink.
Return a Future<T> with a result. The calling code can await for the result and do something accordingly.
Throw an exception. The calling code can detect this with try/catch and show an alert if desired.
Later on, we will see a full example of how useful this is in practice.

More on BLoCs

An Async BLoC can define a StreamController/Stream pair, or the equivalent BehaviorSubject/Observable if using RxDart.

If we want, we can even perform advanced stream operations, like combining streams with combineLatest. And just to be clear:

I recommend having multiple streams in a single BLoC if they need to be combined in some way.

I discourage having multiple StreamControllers in a single BLoC. Instead, I prefer breaking up the code in two or more BLoC classes, for better separation of concerns.

Things we should/shouldn't do in the data layer / BLoCs

BLoCs should only contain pure Dart code. No UI code, no importing Flutter files, or using a BuildContext inside BLoCs.
BLoCs should not call 3rd party code directly. This is the job of service classes.
The interface between Widgets and BLoCs is the same as the interface between BLoCs and services. That is, BloCs can communicate directly with service classes via sync/async methods, and be notified of updates via streams.
Service layer
Service classes have the same input/output interface as BLoCs.

However, there is one fundamental distinction between services and BLoCs.

BLoCs can hold and modify state.
Services can't.
In other words, we can think of services as pure, functional components.

They can modify and transform data they receive from 3rd party libraries.

Example: Firestore service

We can implement a FirestoreDatabase service as a domain-specific API-wrapper for Firestore.
Data in (read): This transforms streams of key-value pairs from Firestore documents into strongly-typed immutable data models.
Data out (write): This converts data models back to key-value pairs for writing to Firestore.
In this case, the service class performs simple data manipulation. Unlike BLoCs, it doesn't hold any state.

A note about terminology: Other articles use the term Repository when referring to classes that talk to 3rd party libraries. Even the definition of the Repository pattern has evolved over time (see this article for more info). In this article, I don't make a clear distinction between Service and Repository.

Putting things together: the Provider package
Once we have defined our BLoCs and services, we need to make them available to our widgets.

For some time now, I have been using the provider package by Remi Rousselet. This is a full dependency injection system for Flutter, based on InheritedWidget.

I really like its simplicity. Here is how to use it to add an authentication service:

return Provider<AuthService>(
  builder: (_) => FirebaseAuthService(), // FirebaseAuthService implements AuthService
  child: MaterialApp(...),
);
And this is how we could use it to create a BLoC:

return Provider<SignInBloc>(
  builder: (_) => SignInBloc(auth: auth),
  dispose: (_, bloc) => bloc.dispose(),
  child: Consumer<SignInBloc>(
    builder: (_, bloc, __) => SignInPage(bloc: bloc),
  ),
);
Note how the Provider widget takes an optional dispose callback. We use this to dispose BLoCs and close the corresponding StreamControllers.

Provider gives us a simple and flexible API that we can use to add anything we want to our widget tree. It works great with BLoCs, services, values and more.



I'll talk in more detail about how to use Provider in some of my upcoming articles. For now, I highly recommend this talk from Google I/O:

Pragmatic State Management in Flutter (Google I/O'19)
A real-world example: Sign-In Page
Now that we have seen how WABS works conceptually, let's use it to build a sign in flow with Firebase authentication.

Here is a sample interaction from my Reference Authentication Flow with Flutter & Firebase:



A few observations:

When sign-in is triggered, we disable all buttons and show a CircularProgressIndicator. We set a loading state to true to do this.
When sign-in succeeds or fails, we re-enable all buttons and restore the title Text. We set loading=false to do this.
When sign-in fails, we present an alert dialog.
Here is a simplified version of the SignInBloc used to drive this logic:

import 'dart:async';
import 'package:firebase_auth_demo_flutter/services/auth_service.dart';
import 'package:meta/meta.dart';

class SignInBloc {
  SignInBloc({@required this.auth});
  final AuthService auth;

  final StreamController<bool> _isLoadingController = StreamController<bool>();
  Stream<bool> get isLoadingStream => _isLoadingController.stream;

  void _setIsLoading(bool isLoading) => _isLoadingController.add(isLoading);

  Future<void> signInWithGoogle() async {
    try {
      _setIsLoading(true);
      return await auth.signInWithGoogle();
    } catch (e) {
      rethrow;
    } finally {
      _setIsLoading(false);
    }
  }

  void dispose() => _isLoadingController.close();
}
Note how the public API of this BLoC only exposes a Stream and a Future:

Stream<bool> get isLoadingStream;
Future<void> signInWithGoogle();
This is in line with our definition of Async BLoC.

All the magic happens in the signInWithGoogle() method. So let's review this again with comments:

Future<void> signInWithGoogle() async {
  try {
    // first, add loading = true to the stream sink
    _setIsLoading(true);
    // then sign-in and await for the result
    return await auth.signInWithGoogle();
  } catch (e) {
    // if sign in failed, rethrow the exception to the calling code
    rethrow;
  } finally {
    // on success or failure, add loading = false to the stream sink
    _setIsLoading(false);
  }
}
Just like a normal BLoC, this method adds values to a sink.

But in addition to that, it can return a value asynchronously, or throw an exception.

This means that we can write code like this in our SignInPage:

// called by the `onPressed` callback of our button
Future<void> _signInWithGoogle(BuildContext context) async {
  try {
    await bloc.signInWithGoogle();
    // handle success
  } on PlatformException catch (e) {
    // handle error (show alert)
  }
}
This code looks simple enough. And it should be, because all we need here is async/await and try/catch.

And yet, this is not possible with the "strict" version of BLoC that only uses a sink and a stream. For reference, implementing something like this in Redux is… uhm… not fun! 😅

Async-BLoC may seem like a small improvement to BLoC, but it makes all the difference.

A note on handling exceptions

By the way, another possible way of handling exceptions would be to add an error object to the stream, like so:

Future<void> signInWithGoogle() async {
  try {
    // first, add loading = true to the stream sink
    _setIsLoading(true);
    // then sign-in and await for the result
    return await auth.signInWithGoogle();
  } catch (e) {
    // add error to the stream
    _isLoadingController.addError(e);
  } finally {
    // on success or failure, add loading = false to the stream sink
    _setIsLoading(false);
  }
}
Then, in the widget class we could write code like this:

class SignInPage extends StatelessWidget {
  SignInPage({@required this.bloc});
  final SignInBloc bloc;

  // called by the `onPressed` callback of our button
  Future<void> _signInWithGoogle(BuildContext context) async {
    await bloc.signInWithGoogle();
  }

  void build(BuildContext context) {
    return StreamBuilder(
      stream: isLoadingStream,
      builder: (context, snapshot) {
        if (snapshot.hasError) {
          // show error
          showDialog(...);
        }
        // build UI based on snapshot
      }
    )
  }
}
However, this is bad for two reasons:

It shows a dialog inside the builder of the StreamBuilder. This is not great because the builder is only supposed to return a widget, and not execute any imperative code.
This code lacks clarity. The place where we show the error is completely different from the place where we sign in.
So, don't do this, and use try/catch as shown above. 😉

Moving on…

Can we use WABS to create an Async-Service?
Of course. As I said before:

BLoCs can hold and modify state.
Services can't.
However, their public-facing APIs obey the same rules.

Here's an example of a service class for a database API:

abstract class Database {
  // CRUD operations for Job
  Future<void> setJob(Job job);
  Future<void> deleteJob(Job job);
  Stream<List<Job>> jobsStream();

  // CRUD operations for Entry
  Future<void> setEntry(Entry entry);
  Future<void> deleteEntry(Entry entry);
  Stream<List<Entry>> entriesStream({Job job});
}
We could use this API to write and read data to/from Cloud Firestore.

The calling code could define this method to write a new Job to the database:

Future<void> _submit(Job job) async {
  try {
    await database.setJob(job);
    // handle success
  } on PlatformException catch (e) {
    // handle error (show alert)
  }
}
Same pattern, very simple error handling.

Comparison with RxVMS
In this article, I have introduced Widget-Async-BLoC-Service as an adaptation of existing architectural patterns in Flutter.

WABS is most similar to the RxVMS pattern by Thomas Burkhart.

There is even a close match between the individual layers:

WABS	RxVMS
Widget	View
Async	RxCommand
BLoC	Manager
Service	Service
The main differences between the two are that:

WABS uses the Provider package, while RxVMS uses the GetIt service locator
WABS uses simple async methods to handle UI events, while RxVMS uses RxCommand.
RxCommand is a powerful abstraction to handle UI events and updates. It removes the boilerplate code required to create a StreamController/Stream pair with BLoCs.

It does however come with a bigger learning curve. For my use cases Async-Bloc does the job and is simpler, despite a bit of extra boilerplate.

I also like that WABS can be implemented without any external libraries (aside from the Provider package).

Ultimately choosing one or the other depends on your use cases, but also personal preference and taste.

Should I use BLoCs in my apps?
BLoCs come with a steep learning curve. To understand them, you need to also be familiar with Streams and StreamBuilder.

When working with streams, there are various considerations to make:

what is the connection state of the stream? (none, waiting, active, done)
is the stream single or multiple subscription?
StreamController and StreamSubscription always need to be disposed
dealing with nested StreamBuilders can lead to thorny debugging issues when Flutter rebuilds the widget tree
All of this adds more overhead to our code.

And when updating local application state (e.g. propagating state from one widget to another), there are simpler alternatives to BLoC. I plan to write about this on a follow-up article.

In any case, I found BLoCs very effective when building realtime apps with Firestore, where the data flows from the backend into the app via streams.

In this scenario, it is common to combine streams or perform transformations with RxDart. BLoCs are a great place to do this.

Conclusion
This article was an in-depth introduction to WABS, an architectural pattern that I have been using for some time in multiple projects.

Truth be told, I have been been refining this over time, and I didn't even have a name for it until I wrote this article.

As I said before, architectural patterns are just tools to get our job done. My advice: choose the tools that make more sense for you and your projects.

And if you use WABS in your projects, let me know how it works for you. 😉

Happy coding!

Source code
The example code from this article was taken from my Reference Authentication Flow with Flutter & Firebase:

Reference Authentication Flow with Flutter & Firebase
In turn, this project complements all the in-depth material from my Flutter & Firebase Udemy course. This is available for early access at this link (discount code included):

Flutter & Firebase: Build a Complete App for iOS & Android
References
Provider package
Pragmatic State Management in Flutter (Google I/O'19)
RxVMS a practical architecture for Flutter Apps
RxVMS foundations: RxCommand and GetIt
Flutter / AngularDart – Code sharing, better together (DartConf 2018)
LEARN FLUTTER TODAY


Sign up for updates and get my free Flutter Layout Cheat Sheet.

Email Address

We use this field to detect spam bots. If you fill this in, you will be marked as a spammer.
No Spam. Ever. Unsubscribe at any time.
 PREVIOUS POSTNEXT POST


Copyright © Andrea Bizzotto 2019
