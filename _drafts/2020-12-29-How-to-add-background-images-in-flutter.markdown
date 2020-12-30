
 What you can do is give the Scaffold a transparent color and put it in a Container and use the decoration property to pull in the required background image. The app bar is also transparent.

 ```dart
Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Welcome to Flutter',
      home: Container(
        decoration: BoxDecoration(
            image: DecorationImage(
                image: AssetImage("images/logo.png"), fit: BoxFit.cover)),
        child: Scaffold(
          backgroundColor: Colors.transparent,
          appBar: AppBar(
            elevation: 0,
            backgroundColor: Colors.transparent,
            title: Text('My App'),
            centerTitle: true,
            leading: IconButton(
                icon: Icon(
                  Icons.list,
                  color: Colors.white,
                ),
                onPressed: () {}),
          ),
        ),
      ),
    );
  }
 ```

Use BoxDecoration as the decoration attribute of the Container:
 ```dart
Container(
    decoration: new BoxDecoration(
      image: new DecorationImage(
        image: new AssetImage("images/logo.png"),
        fit: BoxFit.fill,
      ),
    ),
  ),
 ```

 ```dart
Widget build(BuildContext context) {
    Size size = MediaQuery.of(context).size;
    return Container(
      decoration: BoxDecoration(
          color: Colors.white,
          image: DecorationImage(
              image: AssetImage("asset/images/image.png"),
              fit: BoxFit.cover)),
      child: Scaffold(
        backgroundColor: Colors.transparent,
      ),
    );
  }
 ```


```dart
Container(
          decoration: BoxDecoration(
            image: DecorationImage(
              image: NetworkImage(
                  "https://cdn.pixabay.com/photo/2015/08/28/16/38/stars-912134_960_720.jpg"),
              fit: BoxFit.cover,
            ),
          ),
          // child: <Widget>
),
```
