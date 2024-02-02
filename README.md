# L4S

Low Latency, Low Loss, Scalable Throughput (L4S) seeks to reduce network latency by introducing new protocols for congestion control and queue management at hosts, servers, and routers throughout the Internet. However, because it requires such widespread changes, it is critical to understand the practical implications of deploying this technology incrementally in diverse network environments. 

In this experiment, we will see how two types of TCP congestion control mechanisms — TCP Prague (a scalable approach) and TCP Cubic (a traditional approach) — interact and affect performance when they meet at the same network bottleneck. This study methodically examines partial L4S deployments under an array of conditions, considering various Active Queue Management (AQM) types, network latencies (RTT), Explicit Congestion Notification (ECN) configurations and bottleneck bandwidth scenarios.

To run this experiment on [FABRIC](https://fabric-testbed.net), you should have a FABRIC account with keys configured, and be part of a FABRIC project. You will need to have set up SSH keys and understand how to use the Jupyter interface in FABRIC.

## Results

We organize the results according to the key conclusions drawn from our experiments. In our analysis, we primarily focus on scenarios where the Prague receiver and sender negotiate using AccECN, while the Cubic receiver and sender utilize Classic ECN, with a bottleneck capacity of 100 Mbps. However, other important cases are also considered. The figure below shows **Prague throughput share** and **relative queueing latency of cubic** across different AQM types and buffer BDP sizes.


![Results_throughput](/results/heatmap_prague_share.png)

![Results_rtt](/results/heatmap_relative_queuedelay.png)


### No Domination in FIFO Bottlenecks without ECN

Our findings suggest that in bottlenecks like FIFO, where packet loss is the only indicator of congestion, neither protocol significantly dominates in terms of throughput. However, Cubic tends to achieve a higher throughput share than Prague in most cases. This result aligns with expectations, as Prague, when encountering packet loss, behaves similarly to TCP Reno. Since Cubic is known to attain higher throughput than TCP Reno under such conditions, it consequently outperforms Prague in throughput share in FIFO settings, as demonstrated by figure above. Regarding queuing delay, as depicted in the figure, the queueing delays for Prague and Cubic are nearly equal, aligning with typical behaviors in FIFO bottleneck scenarios.


### Prague Outperforms Cubic in Single Queue Classic ECN AQMs

In Single Queue Classic ECN AQMs such as Codel and Single Queue FQ, Prague significantly outperforms Cubic in terms of throughput as illustrated in the figure above. This superiority is evident regardless of the ECN threshold and BDP size among the given parameters.

### Per-flow Queuing AQM Performance

In per-flow queuing AQMs (FQ and FQ Codel), it has been observed that with a 5 ms ECN threshold, the throughput share between Prague and Cubic is mostly equal as depicted in figure above. However, in scenarios with a 1 ms ECN threshold, Prague begins to gain more throughput. This outcome can be expected, as Cubic reacts more severely to ECN signals compared to Prague. With a 1 ms threshold, ECN signals are expected to occur more frequently, leading Cubic to decrease its window size significantly each time. As a result, Prague obtains a greater share of the throughput under these conditions.

### DualPI2 Performs as Expected

In DualPI2, we expect fair sharing between TCP Prague and TCP Cubic, supported by a dual queueing system and conditional priority schedulers. Moreover, low queuing delay for L4S traffic is anticipated due to the very low ECN threshold (approximately 1ms) in the L4S queue. In the results, these expectations are mostly satisfied. Throughput is generally shared fairly, with no dominance of TCP Prague, as demonstrated in the figure above. Additionally, Prague experiences less queuing delay compared to TCP Cubic. These observations indicate that DualPI2 performs as expected in the given network environment.

### ECN Fallback Algorithm’s Impacts on TCP Prague Performance

The results previously discussed were obtained without the new ECN Fallback algorithm for TCP Prague, as this algorithm is disabled by default. Upon manually enabling the algorithm, we observed a notable impact on TCP Prague’s performance.

In scenarios with a 5 ms ECN threshold, the algorithm functions effectively, ensuring a fair throughput distribution among flows. However, under a 1 ms ECN threshold, Prague’s dominance remains, especially in single queue FQ and Codel AQMs, as illustrated in the figure below. Although the algorithm is designed to detect single queue classic ECN AQMs, our findings suggest that at very low ECN threshold values, such as 1 ms, it struggles to accurately identify the AQM type. Consequently, in these conditions, Prague does not exhibit the expected fallback behavior.

![Results_ecnfallback](/results/heatmap_prague_share-ecnfallback.png) 

### AccECN Negotiation Requirement of TCP Prague

In this case, we tested the AccECN negotiation requirement of TCP Prague. When the receivers and senders negotiate on classic ECN instead of AccECN, the queuing delays in DualPI2 AQM become very similar for TCP Prague and TCP Cubic. This outcome differs from the results shown before, where TCP Prague exhibits much less queuing delay compared to Cubic. The underlying reason relates to the AccECN requirement. If a TCP Prague sender does not negotiate on AccECN with the receiver, it marks the packets with ECT(0) rather than ECT(1).

## Run my Experiment

To reproduce our experiments on FABRIC, log in to the FABRIC testbed's JupyterHub environment. Open a new terminal from the launcher, and run:

> git clone ...

Then, run the `single_bottleneck.ipynb` notebook.
