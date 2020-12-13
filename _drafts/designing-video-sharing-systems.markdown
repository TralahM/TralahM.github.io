---
title: Design Video Sharing Service System
---

## PURPOSE OF VIDEO SHARING SERVICE SYSTEM

Youtube is the advertisement based video sharing service that allows users to upload video based media contents. Users can upload, watch, search, like, dislike videos, add comments to videos. Users uploads/deletes videos only as a logout user but they can search/watch videos as a logout user. This service is an advertisement based service and free so users will see advertisements during watching the video. Moreover users can follow other users or channels by their accounts. Additionally users can add comments to videos only when they login the system.

Before starting to design any system like photo and video sharing social networking service system, it is recommended to think system boundaries and requirements in detail and try to understand what will be the system capacities in the future (like 5 or 10 years) This is very critical since at some point if the system's user count goes exponentially, the system's capacity will not enough to give fast response. Behind architectural design, you have to think about five (availability, reliability, resiliency, durability, cost performance) pillars. These are the pillars that we should consider together since they are coupled to each other. In brief, availability means that system should be always available. Reliability means that system should work as expected. Resiliency means that how and when system will recover itself if there is any problem. Durability is the one pillar that each part of system should exists until we delete. Cost performance is also important topic that will basically related to use services under cost efficiency. It can be illustrated like if the system will be built on AWS and it is enough to use t2 micro EC2 instances, there will be no any reason to use larger EC2 instances and pay extra money.

## REQUIREMENTS AND GOALS OF THE SYSTEM

Youtube is one of the biggest video sharing service and it has a lot of components now however that's not how it was created in the past. Each system is increasingly focused on growth and systems will have more components then their first versions. Now we will design the main features of Youtube. We will not go in detail for recommendation system, channels background, search system since They all are separate discussion topics.



So, if you want to design a system, you must first define the requirements and system boundaries. Probably you will have a service design documents and you will define requirements, boundaries, architectural decisions and others in this service design documents. Youtube is a video sharing service that user can upload/view videos. So your system will support these features;

- Users must be able to create an account.
- Each registered users must have their own personal account page.
- Users must be able to login the system and logout from the system.
- Users must be able to upload/delete videos in the system when they login.
- Users must be able to add comments to videos in the system when they login.
- Users must be able to watch videos in the system when they login or logout.
- Users must be able to search videos/users/groups when they login or logout.
- Users must be able to follow channels.
- Users must be able like/dislike videos.
- Users can like or dislike the videos, under this condition, the system should keep numbers of likes, dislikes, comments, views to present these number to users.

- System must be able to monitor.
- System must be able to support public and private account.
- System must be able to support public and private videos.

When system boundaries and functional requirements are defined, it is needed to think about cloud or on-promise options. Your system can be;

- 100% on-promise (Your own data center/server)
- 100% cloud (AWS, Google Cloud, Azure)
- Mix of on-promise and cloud (You can have both during the migration process)

Todays, cloud services have a huge popularity thanks to cloud mechanism advantages. These advantages;

- Cost efficiency
- High speed
- Security
- Back-up solutions
- Unlimited storage capacity
- A lot of different service options. You do not need to create world from scratch
- Reliability
- Durability
- Resiliency
- Monitoring for almost all services
- Easy software integration with other services

If we talk about Youtube, Netflix or other large scalable systems, this means that these systems are going to be exposed to large traffic. There can be a huge number of request at the same time at the system and system should tend to respond to all requests in a real-time experience. Replication, sharding and load balancer helps the system to be highly available. We will talk about all three features later.



Also, system should respond with minimum latency. You imagine that you would be a user and you want to do anything on the Youtube, do you really want to wait to much time to get the response? I think you don't want to wait too much time as well as you want to experience the system with real-time. To illustrate this, when you search for a video in the system, this system should suggest related videos as soon as possible.

Let's think about design boundaries;

Service will be read-heavy since a lot user will watch videos in system so system will be stay consistent and reliable which means there should not be any data loss. Additionally, service will be durable which means all piece of system should exists until they are delete manually. Before capacity consideration, you have to define what is the purpose of the service. Even if it is more essential for on-promise services, it is essential for both on-promise and cloud services since you can select right services based on purpose, locate them based on available regions and define capacities. Such examples are;

- Create more read services than write services.
- Select the server type according to the type of operation.
- Define caching strategies based on your capacity estimation.
- Select database type (SQL, NoSQL) based on your requirements.
- Define back-up solutions based on your capacity estimations.
- Define data sharding strategies based on your requirements and etc…

Let's assume you have 100M total users and we will assume that read traffic is heavier than write traffic and let's assume the ratio of downloading and uploading data is 25:1.

We will assume that average size of video is 250 MB so the system will have;

Videos capacity in 5 years;

- 5 * 100M * 1 * 250 MB = 120 PB. (Assuming each user will upload 1 videos each year).
- 360 PB with replication and back-up.

This calculation is just a brief example of how to define system capacity and we will not calculate daily download/upload capacity and metadata capacities but you should consider this calculation (and daily read/write capacity estimation) for service/database scaling.

Additionally, cache is an essential system to return data. If you are building large scalable system you have to think different caching strategies. You can use CDN as a video content cache and Redis/Memcache as a metadata cache. The biggest problem of cache will be scaling (global caching mechanism) and cache eviction policies. If you are building your service on AWS, you can use Cloudfront as a CDN (content cache) and you can use elasticache service on AWS for metadata cache. Notice that Cloudfrount is highly scalable AWS service that you do not need to work with maintenance/scalability. AWS will maintain and scale Cloudfront service in itself.



## API DESIGN

In today's world, a lot of systems support mobile platform so APIs are the best choices to be able to provide the distinction between developers and support mobile support as well. We can use REST or SOAP. A lot of huge companies prefer to REST or SOAP according to their systems. There are three main API's we will mention below:

1. UploadVideo(apiKey, title, description, categoryID, language)

     Upload video is the first API that we should mention. There are basically five main properties of this API. You can add more properties to UploadVideo API. Note that, apiKey is the developer key of registered account of service. Thanks to apiKey we can eliminate hacker attacks. UploadVideo returns the HTTP response that demonstrates video is uploaded successfully or not.

2. DeleteVideo (apiKey, videoID)

     Check if user has permission to delete video. It will return HTTP response 200 (OK), 202 (Accepted) if the action has been queued, or 204 (No Content) based on your response.

3. GetVideo (apiKey, query, videoCountToReturn, pageNumber)

     Return JSON containing information about the list of videos and channels. Each video resource will have a title, creation date, like count, total view count, owner and other meta informations.

**There are more APIs to design video sharing service, however, these three APIs are more important than the others. Other APIs will be like likeVideo, addComment, search, recommendation or etc…

## DATABASE DESIGN

There are two choices to define the database schema. These are SQL and NoSQL. We can use traditional database management system like MsSQL or MySQL to keep data. As you know, we should keep information about videos and users into RDBMS.  Other information about videos, called metadata, should be kept too. Now we have the main three tables to keep data. (Notice that we just only think the basic properties of Youtube. We can forget the recommendation system).

###  User

- UserID (primary key)
- Name (nvarchar)
- Age (Integer)
- Email (nvarchar)
- Address (nvarchar)
- Register Date (DateTime)
- Last Login (DateTime)



###  Video

- VideoID (primary key – generated by KGS – Key generation service)
- VideoTitle (nvarchar)
- Size (float)
- UserID (foreign key with User Table)
- Description (nvarchar)
- CategoryID (int) : Note that we can create Category Table to define categories
- Number of Likes (int)
- Number of Dislikes (int)
- Number of Displayed (int) – We can use big int to keep displayed number
- Uploaded Date (DateT?me)

###  VideoComment

- CommentID (primary key)
- UserID (foreign key with User Table)
- VideoID (foreing key with Video Table)
- Comment (nvarchar)
- CommentDate (DateTime)

## SYSTEM DESIGN CONSIDERATION

There are basic features found in web-based systems. The main ones are client, web server, application server, database and cache systems. Depending on the intensity of system traffic, the number of servers or services increases and the load balancer distributes incoming requests between these servers or services. Additionally, queues can be used depending on the density of incoming requesters. Queue operation helps users to keep from waiting more time to get respond. In our Youtube service;

- Client
- Web Server
- Application Server
- Database
- Video Storage
- Encode Service
- Queue
- Replication
- Redundancy
- Load balancing
- Sharding

We can distribute services to three parts to decrease response time because video uploading takes more time from video downloading. Video can be downloaded from the cache and getting data from the cache is a fast way. The client basically users who use the system. Web Server is the first entity that meets the request. Incoming request can take place in upload service, search service or download service. If we give an opportunity to users that download video asynchronously,   system traffic will be relaxed.  An encoder is to encode uploaded video into multiple formats. There are three types of databases which are Video content database, user database, and video metadata storage. Queue process takes place between an application server and encode.

Our Youtube service would be read-heavy and we should be careful when building a system. Our main goal should be returning videos quickly. We can keep copies of videos on different servers to handle the traffic problems. Additionally, this ensures the safety of this system. We can distribute our traffic to different servers using a load balancer. The system can keep two more replicas of metadata database, user database, and video content database.  We can use CDN to cache popular data.

Flow diagram of the system;

1. A client sends a request.
2. Request meets from the webserver.
3. Web server controls the cache. There can be two more cache databases on the system.
4. If the request takes place into a cache, a response is redirected to the client.
5. Otherwise, web server redirects the request an to the application server.
6. There can be load balancer between web servers and application servers.



** If this request is search or view service,  it tries to find the request by looking at the metadata database and the video content database. A load balancer can be placed each layer of the system such as between application server and video content storage, between the application server and metadata database, etc…
When a server responds the request to the client, related data is cached according to the cache process.

As we know, Youtube is a huge video sharing system. Users can upload videos and the number of uploading videos grows exponentially day by day. According to uploading videos, there may one more same video in the system. To eliminate the duplication of videos we can implement an intelligent algorithm. For example, when a video comes to a system, the algorithm automatically checks whether this video is already kept in the system or not. If the system has already this video, then we don't need to keep duplicate data. It saves us from the unnecessary use of space. Additionally, if the incoming video includes a video kept in the system, then we can divide videos into small chunks and we just give the only reference to same video chunks to handle the duplication problem.

Replication and back-up are two important concepts to provide pillars we mentioned before. Replication is a very important concept to handle a failure of services or servers. Replication can be applied database servers, web servers, application servers, media storages and etc.. Actually we can replicate all parts of the system. (Some of AWS services like Route53, they are highly available in itself so you do not need to take care of replication of Route53, Load balancer, etc..) Notice that replication also helps system to decrease response time. You imagine, if we divide incoming requests into more resources rather than one resource, the system can easily meet all incoming requests. Additionally, the optimum number of a replica to each resource is 3 or more. You can provide redundancy by keeping data in different Availability zone or different region in AWS.

For caching strategies, we can use global caching mechanism by using cache
servers. We can use Redis or memcache but the most important part of caching
strategy is how to provide cache eviction. If we use global cache servers, we
will guarantee that each user will see the same data in the cache but there will
time latency if we use global cache servers. As a caching strategies, we can use LRU (Least Recently Used) algorithm.

For media files caching, as we mentioned before, we will use CDN. CDN is located on different edge locations so that the response time will be smaller than fetching media contents directly from AWS S3.

Load balancer allows incoming requests to be redirected to resources according to certain criteria. We can use load balancer at every layer of the system. If we want to use AWS Load balancer service, AWS will support three different Load Balancer types which are;

- Network Load Balancer
- Classical Load Balancer (Deprecated)
- Application Load Balancer

For this service, application load balancer will be fit to our service and it will also handle AZ distribution in itself. Otherwise you can use NGinx but you have to implement algorithm and you have to provide maintenance if we want to use NGinx.

We can use load balancer;

- Between requests and web servers.
- Between web servers and application servers.
- Between application servers and databases
- Between application servers and image storages.
- Between application servers and cache databases.
- We can use Round Robin method for the load balancer. Round Robin method prevents requests from going to dead servers but Round Robin method doesn't deal with the situation that any server is under heavy-traffic. We can modify Round Robin method to be a more intelligent method to handle this problem.

Video uploading is a big process. It should work with sharding mechanism and when it fails, the system should ensure that it should continue to upload video from the failing point.
Video encoding process should include queue operations. When an uploaded video comes, this new task is added to a queue and all tasks in the queue are taken one by one from a queue.
