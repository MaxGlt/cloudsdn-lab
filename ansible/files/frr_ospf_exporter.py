
#!/usr/bin/env python3

import subprocess
import time

def parse_ospf_neighbors(output):
    neighbors = 0
    lines = output.strip().split('\n')
    for line in lines:
        if line and not line.startswith("Neighbor ID"):
            neighbors += 1
    return neighbors

def collect_metrics():
    try:
        result = subprocess.run(
            ["vtysh", "-c", "show ip ospf neighbor"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise Exception(result.stderr)

        count = parse_ospf_neighbors(result.stdout)

        with open("/var/lib/node_exporter/ospf.prom", "w") as f:
            f.write(f"# HELP frr_ospf_neighbors_total\n")
            f.write(f"# TYPE frr_ospf_neighbors_total gauge\n")
            f.write(f"frr_ospf_neighbors_total {count}\n")

    except Exception as e:
        with open("/var/lib/node_exporter/ospf.prom", "w") as f:
            f.write(f"# HELP frr_ospf_neighbors_total\n")
            f.write(f"# TYPE frr_ospf_neighbors_total gauge\n")
            f.write(f"frr_ospf_neighbors_total 0\n")

if __name__ == "__main__":
    collect_metrics()
