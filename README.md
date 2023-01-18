# CNF , Worker Node Introspection 

This repo contains mainly two toolchain.   

* main.py a standalone CLI client that aggregates hardware, software, proc, memory , PCI, numa topology tree etc., in a structured format.

* server.py a server-side, provides rest API, and each action serializes structured output. For example, if you have an ansible or any other pipeline 
and would like to query get OS-specific data without constantly ssh sessions to a host.