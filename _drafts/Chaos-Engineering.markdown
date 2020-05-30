Looking at Extreme Cases of Infrastructure Failure

Chaos Engineering is the discipline of experimenting on a system
in order to build confidence in the system’s capability
to withstand turbulent conditions in production.


We need to identify weaknesses before they manifest in system-wide, aberrant behaviors.  Systemic weaknesses could take the form of: improper fallback settings when a service is unavailable; retry storms from improperly tuned timeouts; outages when a downstream dependency receives too much traffic; cascading failures when a single point of failure crashes; etc.  We must address the most significant weaknesses proactively, before they affect our customers in production.  We need a way to manage the chaos inherent in these systems, take advantage of increasing flexibility and velocity, and have confidence in our production deployments despite the complexity that they represent.


* Build a Hypothesis around Steady State Behavior
Focus on the measurable output of a system, rather than internal attributes of the system.  Measurements of that output over a short period of time constitute a proxy for the system’s steady state.  The overall system’s throughput, error rates, latency percentiles, etc. could all be metrics of interest representing steady state behavior.  By focusing on systemic behavior patterns during experiments, Chaos verifies that the system does work, rather than trying to validate how it works.

* Vary Real-world Events
Chaos variables reflect real-world events.  Prioritize events either by potential impact or estimated frequency.  Consider events that correspond to hardware failures like servers dying, software failures like malformed responses, and non-failure events like a spike in traffic or a scaling event.  Any event capable of disrupting steady state is a potential variable in a Chaos experiment.

* Run Experiments in Production
Systems behave differently depending on environment and traffic patterns.  Since the behavior of utilization can change at any time, sampling real traffic is the only way to reliably capture the request path.  To guarantee both authenticity of the way in which the system is exercised and relevance to the current deployed system, Chaos strongly prefers to experiment directly on production traffic.

* Automate Experiments to Run Continuously
Running experiments manually is labor-intensive and ultimately unsustainable.  Automate experiments and run them continuously.  Chaos Engineering builds automation into the system to drive both orchestration and analysis.

* Minimize Blast Radius
Experimenting in production has the potential to cause unnecessary customer pain. While there must be an allowance for some short-term negative impact, it is the responsibility and obligation of the Chaos Engineer to ensure the fallout from experiments are minimized and contained.


Chaos Engineering is a powerful practice that is already changing how software is designed and engineered at some of the largest-scale operations in the world.  Where other practices address velocity and flexibility, Chaos specifically tackles systemic uncertainty in these distributed systems.  The Principles of Chaos provide confidence to innovate quickly at massive scales and give customers the high quality experiences they deserve.

an extremely complex distributed system (microservice architecture) with hundreds of deploys every day. We don’t want to remove the complexity of the system; we want to thrive on it. We want to continue to accelerate flexibility and rapid development. And with that complexity, flexibility, and rapidity, we still need to have confidence in the resiliency of our system.

an empirical, systems-based approach which addresses the chaos inherent in distributed systems at scale. This approach specifically builds confidence in the ability of those systems to withstand realistic conditions. We learn about the behavior of a distributed system by observing it in a controlled experiment, and we use those learnings to fortify our systems before any systemic effect can disrupt the quality service that we provide our customers. We call this new discipline Chaos Engineering.


One of our services is called Subscriber, which handles certain user management activities and authentication. It is possible that under some rare or even unknown situation Subscriber will be crippled. This might be due to network errors, under-provisioning of resources, or even by events in downstream services upon which Subscriber depends. When you have a distributed system at scale, sometimes bad things just happen that are outside any person’s control. We want confidence that our service is resilient to situations like this.
